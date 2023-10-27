// remove pagination buttons
function deletePagination() {
    const paginationContainer = document.querySelector(".pagination");
    paginationContainer.innerHTML = "";
}

// filtering in search function
function keywordSearch() {
    var keyword = document.getElementById('search-input').value;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/v1/search/' + encodeURIComponent(keyword), true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            const responseData = JSON.parse(xhr.responseText);
            
            // locate the container element for displaying drama information
            const dramaContainer = document.querySelector(".drama-display");
    
            // clear the existing content inside the container
            dramaContainer.innerHTML = "";
    
            if (responseData.dramas.length === 0) {
                // If empty, insert HTML element for displaying text
                const noDataElement = document.createElement("div");
                noDataElement.className = "text-center";
                noDataElement.style.width = "100%";
                noDataElement.style.margin = "20px";
                noDataElement.innerHTML = "<p>沒有相關戲劇，請使用別的關鍵字搜尋。</p>";
                dramaContainer.appendChild(noDataElement);
            } else {
                responseData.dramas.forEach(function(drama) {
                    const dramaElement = document.createElement("div");
                    dramaElement.className = "text-center";
        
                    // extract and insert each category into HTML
                    const categoriesHTML = drama.categories.map(category => `
                        <span class="badge rounded-pill bg-primary text-white">${category}</span>`).join('');
                    
                    // generate HTML content
                    dramaElement.innerHTML = `
                        <div class="card drama_list" style="width: 18rem;">
                            <a href="/api/v1/detail/${drama._id.$oid}">
                                <img src="${drama.image}" alt="${drama.name}" class="drama-img">
                            </a>
                            <div class="card-body">
                                <h6 class="card-title">${drama.name}</h6>
                                <p class="card-text">${drama.eng_name}</p>
                                ${categoriesHTML}
                            </div>
                        </div>
                    `;
        
                    // insert into the HTML container
                    dramaContainer.appendChild(dramaElement);
                });
            }
            deletePagination();
        }
    };
    xhr.send();
};

document.addEventListener('DOMContentLoaded', function () {
    // get search button
    const searchButton = document.getElementById('search-button');
    // get search input element
    const searchInput = document.getElementById('search-input');

    // When the search button is clicked, execute the keywordSearch function
    searchButton.addEventListener('click', function () {
        keywordSearch();
    });
    // When the pressed key is 'Enter', execute the keywordSearch function
    searchInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            keywordSearch();
        }
    });
});

// filtering in categories button
document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll("button[data-category]");
    
    buttons.forEach(function(button) {
        button.addEventListener("click", function() {
            const category = encodeURIComponent(this.getAttribute("data-category"));
            
            const xhr = new XMLHttpRequest();
            xhr.open("GET", "/api/v1/category/" + encodeURIComponent(category), true);
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    const responseData = JSON.parse(xhr.responseText);
            
                    const dramaContainer = document.querySelector(".drama-display");
            
                    dramaContainer.innerHTML = "";
            
                    responseData.dramas.forEach(function(drama) {
                        const dramaElement = document.createElement("div");
                        dramaElement.className = "text-center";
            
                        const categoriesHTML = drama.categories.map(category => `
                            <span class="badge rounded-pill bg-primary text-white">${category}</span>`).join('');

                        dramaElement.innerHTML = `
                            <div class="card drama_list" style="width: 18rem;">
                                <a href="/api/v1/detail/${drama._id.$oid}">
                                    <img src="${drama.image}" alt="${drama.name}" class="drama-img">
                                </a>
                                <div class="card-body">
                                    <h6 class="card-title">${drama.name}</h6>
                                    <p class="card-text">${drama.eng_name}</p>
                                    ${categoriesHTML}
                                </div>
                            </div>
                        `;
            
                        dramaContainer.appendChild(dramaElement);
                    });
                    deletePagination();
                }
            };
            xhr.send();
        });
    });
});


// star rating display
document.addEventListener('DOMContentLoaded', function () {
    const stars = document.querySelectorAll('#rating-stars i');
    // Retrieve the rating data
    const scoreElement = document.getElementById('rating');
    // defaulting to 0 if none exists
    const initialScore = scoreElement ? parseInt(scoreElement.innerText) : 0;

    // change star colors based on the rating data
    stars.forEach((star, index) => {
        const isStarActive = index < initialScore;
        star.classList.toggle('active', isStarActive);
        star.style.color = isStarActive ? 'gold' : 'black';
    });
    
    stars.forEach(star => {
        star.addEventListener('click', function () {
            const clickedStar = this;
            const clickedStarIndex = parseInt(clickedStar.getAttribute('data-star'));

            // change colors based on the clicked star
            stars.forEach((s, index) => {
                if (index + 1 <= clickedStarIndex) {
                    s.classList.add('active');
                    s.style.color = 'gold';
                    
                } else {
                    s.classList.remove('active');
                    s.style.color = 'black';
                }
            });

            const dramaId = this.parentElement.getAttribute('data-movie-id');
            const selectedStars = document.querySelectorAll('#rating-stars i.active').length;

            // send rating data to backend
            fetch(`/api/v1/rating/${dramaId}/${selectedStars}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    // Update frontend display of the rating
                    document.querySelector('#rating').innerText = `${data.rating}`;
                });
        });
    });
});

