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
                    // 將原本顯示戲劇資訊的class內容清空
                    var dramaContainer = document.querySelector(".drama-container");
                    dramaContainer.innerHTML = "";

                    // 將 responseData 中的資料插入容器中
                    responseData.dramas.forEach(function(drama) {
                        var dramaElement = document.createElement("div");
                        dramaElement.className = "drama_list";

                        // 根據 responseData 生成 HTML
                        dramaElement.innerHTML = `
                            <div class="detail">
                                <a href="/api/v1/detail/${ drama.name }">
                                    <img src="${drama.image}" alt="${drama.name}" class="drama-img">
                                </a>
                                <h3>${drama.name}</h3>
                                <p>${drama.eng_name}</p>
                                <p>類別：${drama.categories.join(", ")}</p>
                            </div>
                        `;

                        // 插入戲劇資訊
                        dramaContainer.appendChild(dramaElement);
                    });
                }
            };
            
            xhr.send();
        });
    });
});
