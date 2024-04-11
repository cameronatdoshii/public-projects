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

            // Adjust the conditional check for both direct array or object with Items array
            let items = Array.isArray(data) ? data : data.Items;
            if (items && items.length > 0) {
                items.forEach((song, index) => {
                    const songBox = document.createElement('div');
                    const imageName = `${encodeURIComponent(song.title.replace(/\s+/g, '_'))}.jpg`;
                    const artist = encodeURIComponent(song.artist.replace(/\s+/g, '_'));
                    const year = song.year;
                    const title = encodeURIComponent(song.title.replace(/\s+/g, '_'));
                    const imagePath = `images/${artist}/${year}/${title}.jpg`;

                    fetch(`/generate-presigned-url?path=${imagePath}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.url) {
                            // Now you have a presigned URL that you can use in the img src attribute
                            songBox.querySelector('img').src = data.url;
                        } else {
                            imgElement.src = 'path/to/default/image.jpg'; // Fallback image path
                            console.log('Presigned URL not found, using fallback image.');
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching the presigned URL:', error);
                        const imgElement = document.createElement('img');
                        imgElement.src = 'path/to/default/image.jpg'; // Fallback image path
                        imgElement.alt = 'Default Image';
                        songBox.appendChild(imgElement);
                    });
                    songBox.className = 'song-item';
                    songBox.innerHTML = `
                        <p>Title: ${song.title}</p>
                        <p>Artist: ${song.artist}</p>
                        <p>Year: ${song.year}</p>
                        <img src="https://s3864826-a1-music-image-bucket.s3.amazonaws.com/images/${encodeURIComponent(song.artist)}/${song.year}/${imageName}" alt="${song.artist} Image">
                        <button id="subscribe-${index}" class="subscribe-button">Subscribe</button>
                    `;
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
                                imagePath: song.img_url
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
