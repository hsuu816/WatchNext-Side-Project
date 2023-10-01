// 搜尋功能篩選
function keywordSearch() {
    var keyword = document.getElementById('search-input').value;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/v1/search/' + encodeURIComponent(keyword), true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var responseData = JSON.parse(xhr.responseText);
            
            // 找到用於顯示戲劇資訊的容器元素
            var dramaContainer = document.querySelector(".row");
    
            // 清空容器內的現有內容
            dramaContainer.innerHTML = "";
    
            // 遍歷responseData中的資料並插入到容器中
            responseData.dramas.forEach(function(drama) {
                var dramaElement = document.createElement("div");
                dramaElement.className = "col-md-3"; // 確保每個卡片佔用相同的列寬
    
                // 把category一個個取出放入html
                const categoriesHTML = drama.categories.map(category => `
                    <span class="badge rounded-pill bg-primary text-white">${category}</span>`).join('');
    
                // 生成html內容
                dramaElement.innerHTML = `
                    <div class="card drama_list" style="width: 18rem;">
                        <a href="/api/v1/detail/${drama.name}">
                            <img src="${drama.image}" alt="${drama.name}" class="drama-img">
                        </a>
                        <div class="card-body">
                            <h6 class="card-title">${drama.name}</h6>
                            <p class="card-text">${drama.eng_name}</p>
                            ${categoriesHTML}
                        </div>
                    </div>
                `;
    
                // 插入到html容器中
                dramaContainer.appendChild(dramaElement);
            });
        }
    };
    xhr.send();
};

document.addEventListener('DOMContentLoaded', function () {
    // 取得搜尋按鈕
    var searchButton = document.getElementById('search-button');

    // 當點選search時，執行keywordSearch function
    searchButton.addEventListener('click', function () {
        keywordSearch();
    });
});


// 類型按鈕篩選
document.addEventListener("DOMContentLoaded", function() {
    var buttons = document.querySelectorAll("button[data-category]");
    
    buttons.forEach(function(button) {
        button.addEventListener("click", function() {
            var category = encodeURIComponent(this.getAttribute("data-category"));
            console.log("Button clicked!");
            
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/api/v1/category/" + encodeURIComponent(category), true);
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var responseData = JSON.parse(xhr.responseText);
            
                    // 找到用於顯示戲劇資訊的容器元素
                    var dramaContainer = document.querySelector(".row");
            
                    // 清空容器內的現有內容
                    dramaContainer.innerHTML = "";
            
                    // 遍歷responseData中的資料並插入到容器中
                    responseData.dramas.forEach(function(drama) {
                        var dramaElement = document.createElement("div");
                        dramaElement.className = "col-md-3"; // 確保每個卡片佔用相同的列寬
            
                        // 把category一個個取出放入html
                        const categoriesHTML = drama.categories.map(category => `
                            <span class="badge rounded-pill bg-primary text-white">${category}</span>`).join('');
            
                        // 生成html內容
                        dramaElement.innerHTML = `
                            <div class="card drama_list" style="width: 18rem;">
                                <a href="/api/v1/detail/${drama.name}">
                                    <img src="${drama.image}" alt="${drama.name}" class="drama-img">
                                </a>
                                <div class="card-body">
                                    <h6 class="card-title">${drama.name}</h6>
                                    <p class="card-text">${drama.eng_name}</p>
                                    ${categoriesHTML}
                                </div>
                            </div>
                        `;
            
                        // 插入到html容器中
                        dramaContainer.appendChild(dramaElement);
                    });
                }
            };
            xhr.send();
        });
    });
});


// 評分星星顯示
document.addEventListener('DOMContentLoaded', function () {
    const stars = document.querySelectorAll('#rating-stars i');
    // 獲取資料庫儲存的評分數據，如果沒有就預設為0
    const scoreElement = document.getElementById('score');
    const initialScore = scoreElement ? parseInt(scoreElement.innerText) : 0;

    console.log('Initial Score:', initialScore);

    // 依照評分數據改變星星顏色
    stars.forEach((star, index) => {
        const isStarActive = index < initialScore;
        star.classList.toggle('active', isStarActive);
        star.style.color = isStarActive ? 'gold' : 'black';
    });
    
    stars.forEach(star => {
        star.addEventListener('click', function () {
            const clickedStar = this;
            const clickedStarIndex = parseInt(clickedStar.getAttribute('data-star'));

            // 依照點擊星星來改變顏色
            stars.forEach((s, index) => {
                if (index + 1 <= clickedStarIndex) {
                    s.classList.add('active');
                    s.style.color = 'gold';
                    
                } else {
                    s.classList.remove('active');
                    s.style.color = 'black';
                }
            });

            const dramaName = this.parentElement.getAttribute('data-movie-name');
            const selectedStars = document.querySelectorAll('#rating-stars i.active').length;

            // 將評分數據發送到後端
            fetch(`/api/v1/score/${dramaName}/${selectedStars}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    // 更新前端顯示的評分
                    document.querySelector('#rating-stars p').innerText = `score:${data.score}`;
                });
        });
    });
});

