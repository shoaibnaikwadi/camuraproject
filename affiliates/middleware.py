from .models import AffiliateProfile


class AffiliateReferralMiddleware:
    """
    Capture ?ref=CAMXXXXXXXX and store it in the visitor's session.

    Must be installed after SessionMiddleware and
    AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        referral_code = request.GET.get("ref", "").strip().upper()

        if referral_code and len(referral_code) <= 20:
            affiliate = AffiliateProfile.objects.filter(
                referral_code__iexact=referral_code,
                is_enabled=True,
            ).only("id", "user_id", "referral_code").first()

            if affiliate:
                is_own_link = (
                    request.user.is_authenticated
                    and request.user.pk == affiliate.user_id
                )

                if not is_own_link:
                    # Last valid affiliate link clicked wins.
                    request.session["affiliate_referral_code"] = (
                        affiliate.referral_code
                    )

                    # Retain the referral for 30 days.
                    request.session.set_expiry(60 * 60 * 24 * 30)

        return self.get_response(request)