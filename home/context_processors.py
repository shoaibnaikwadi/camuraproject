from django.db.models import Sum
from .models import CartItem

def cart_count(request):
    if request.user.is_authenticated:
        total_qty = CartItem.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        total_qty = 0
    return {'cart_items_count': total_qty}
