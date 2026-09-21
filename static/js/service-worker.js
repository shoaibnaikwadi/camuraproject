// =========================================================
// Camura PWA Service Worker
// =========================================================

const CACHE_NAME = "camura-v2";

const APP_SHELL = [
    "/",
    "/static/manifest.json",
    "/static/img/camura-icon-192.png",
    "/static/img/camura-icon-512.png",
    "/static/img/camura_logo.png",
    "/static/bootstrap/css/bootstrap.min.css",
    "/static/bootstrap/js/bootstrap.bundle.min.js",
    "/static/css/style.css"
];


// =========================================================
// INSTALL
// =========================================================

self.addEventListener("install", event => {

    event.waitUntil(

        caches.open(CACHE_NAME)
            .then(cache => {

                console.log("Camura: caching app shell");

                return cache.addAll(APP_SHELL);

            })

    );

    self.skipWaiting();

});


// =========================================================
// ACTIVATE
// =========================================================

self.addEventListener("activate", event => {

    event.waitUntil(

        caches.keys()
            .then(keys => {

                return Promise.all(

                    keys
                        .filter(key => key !== CACHE_NAME)
                        .map(key => caches.delete(key))

                );

            })

            .then(() => self.clients.claim())

    );

});


// =========================================================
// FETCH
// =========================================================

self.addEventListener("fetch", event => {

    const request = event.request;

    // Only handle GET requests
    if (request.method !== "GET") {
        return;
    }

    const url = new URL(request.url);

    // Only handle Camura's own website
    if (url.origin !== self.location.origin) {
        return;
    }


    // -----------------------------------------------------
    // Static files: Cache First
    // -----------------------------------------------------

    if (
        url.pathname.startsWith("/static/")
    ) {

        event.respondWith(

            caches.match(request)
                .then(cachedResponse => {

                    if (cachedResponse) {
                        return cachedResponse;
                    }

                    return fetch(request)
                        .then(response => {

                            if (
                                response &&
                                response.status === 200
                            ) {

                                const responseClone =
                                    response.clone();

                                caches.open(CACHE_NAME)
                                    .then(cache => {
                                        cache.put(
                                            request,
                                            responseClone
                                        );
                                    });

                            }

                            return response;

                        });

                })

        );

        return;
    }


    // -----------------------------------------------------
    // Django pages: Network First
    // -----------------------------------------------------

    event.respondWith(

        fetch(request)
            .then(response => {

                return response;

            })
            .catch(() => {

                return caches.match(request)
                    .then(cachedResponse => {

                        return cachedResponse ||
                            caches.match("/");

                    });

            })

    );

});