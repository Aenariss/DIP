self.addEventListener('fetch', event => {
    if (event.request.mode === 'navigate') {
        console.log('Intercepted navigation:', event.request.url);

        // Force another fetch for the same page
        event.respondWith(
            fetch(event.request).then(response => {
                console.log('Fetching again:', event.request.url);
                fetch(event.request); // Triggers duplicate request
                return response;
            })
        );
    }
});