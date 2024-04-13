document.addEventListener('DOMContentLoaded', function () {
    const queryForm = document.getElementById('query-form');
    const resultsArea = document.getElementById('query-results-area');

    queryForm.addEventListener('submit', function (event) {
        console.log('Form submission intercepted.');
        event.preventDefault();

        const formData = new FormData(queryForm);
        const searchParams = new URLSearchParams();
        for (const pair of formData) {
            searchParams.append(pair[0], pair[1]);
        }

        fetch('/main-query-music', {
            method: 'POST',
            body: searchParams,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            resultsArea.innerHTML = '';

            let items = Array.isArray(data) ? data : data.Items;
            if (items && items.length > 0) {
                items.forEach((song, index) => {
                    const songBox = document.createElement('div');
                    const artist = encodeURIComponent(song.artist.replace(/\s+/g, '_'));
                    const imagePath = `images/${artist}.jpg`;

                    fetch(`/generate-presigned-url?path=${imagePath}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.url) {
                            songBox.innerHTML = `
                                <p>Title: ${song.title}</p>
                                <p>Artist: ${song.artist}</p>
                                <p>Year: ${song.year}</p>
                                <img src="${data.url}" alt="${song.artist} Image">
                                <p>Image Path: ${data.url}</p>
                                <button id="subscribe-${index}" class="subscribe-button">Subscribe</button>
                            `;
                            songBox.className = 'song-item';
                            resultsArea.appendChild(songBox);

                            const subscribeButton = document.getElementById(`subscribe-${index}`);
                            subscribeButton.addEventListener('click', function() {
                                fetch('/main-music-subscribe', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({
                                        title: song.title,
                                        artist: song.artist,
                                        year: song.year,
                                        imagePath: data.url  // Use the presigned URL here
                                    }),
                                })
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error(`HTTP error! status: ${response.status}`);
                                    }
                                    return response.json();
                                })
                                .then(subscriptionData => {
                                    console.log('Subscription successful', subscriptionData);
                                    window.location.reload();
                                })
                                .catch(error => {
                                    console.error('Error subscribing:', error);
                                });
                            });
                        } else {
                            console.error('Presigned URL not found, using fallback image.');
                            // Handle cases where presigned URL is not available
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching the presigned URL:', error);
                    });
                });
            } else {
                console.log('No items to display.');
                resultsArea.innerHTML = 'No results found.';
            }
        })
        .catch(error => {
            console.error('Error during fetch or processing:', error);
            resultsArea.innerHTML = 'Failed to load results.';
        });
    });

    document.querySelectorAll('.remove-subscription').forEach(button => {
        button.addEventListener('click', function() {
            const parentItem = this.closest('.subscription-item');
            if (parentItem) {
                parentItem.style.display = 'none';

                const title = parentItem.querySelector('p:first-child').textContent.split(': ')[1];
                const artist = parentItem.querySelector('p:nth-child(2)').textContent.split(': ')[1];
                const year = parentItem.querySelector('p:nth-child(3)').textContent.split(': ')[1];

                fetch('/remove-subscription', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        artist: artist,
                        year: year
                    }),
                })
                .then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Error:', error));
            }
        });
    });
});
