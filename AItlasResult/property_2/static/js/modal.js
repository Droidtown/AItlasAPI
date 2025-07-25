/**
 * 秀出畫面
 * 準備放 forceGraph 跟 mermaidGraph 中線條的資料。
 *
 * @param {void}
 * @returns {void}
 */
function _showModal() {
    document.getElementById('modal-backdrop').style.display = 'block';
    document.getElementById('modal-infoData').style.display = 'block';
}

/**
 * 關閉畫面
 * 關閉秀出 forceGraph 跟 mermaidGrph 中線條的資料
 *
 * @param {void}
 * @returns {void}
 */
function closeModal() {
    document.getElementById('modal-backdrop').style.display = 'none'
    document.getElementById('modal-infoData').style.display = 'none'
}

/**
 * 在 modal 畫面中，顯示與指定連線（link）相關的互動資訊。
 *
 * 根據給定的座標`x`和`y`來設定 modal 的位置，並根據 link 資料渲染 forceGraph
 *
 * @param {number} x - 滑鼠點擊的 X 座標，用於定位 modal。
 * @param {number} y - 滑鼠點擊的 Y 座標，用於定位 modal。
 * @param {{
 *   source: { id: string },
 *   target: { id: string },
 *   label: string,
 *   meta_data: string,
 *   date_only: string,
 *   url: string
 * }} link
 */
function showLinkInfo(x, y, link) {
    console.log(link)
    const tooltip = document.getElementById('modal-infoData');
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
    tooltip.innerHTML = `
    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 6px; background: white; width: fit-content; font-family: sans-serif; position: relative;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 4px;">
            <span style="font-size: 18px;">👁️</span>
            <span>
            <span style="color: green; font-weight: bold;">${link.source.id}</span>
            對
            <span style="color: red; font-weight: bold;">${link.target.id}</span>
            的互動
            </span>
        </div>
        </div>
        <a class="btn btn-primary" data-bs-toggle="collapse" href="#collapseMetaData" role="button" aria-expanded="false" aria-controls="collapseMetaData">
            ${link.label}
        </a>
        <div class="collapse" id="collapseMetaData">
            <div class="card card-body">
                ${link.date_only}
                <a href="${link.url}">文章連結</a>
                <br>
                ${link.meta_data}
            </div>
        </div>
    </div>
    `;
    _showModal();
}

/**
 * 讀文章資料與實體資料（人名、地點、Entity、事件）。
 * 同時渲染文章內容、實體資訊表格，以及更新事件地圖。
 * 其中會將內容存入：G_EventMap、G_MermaidGraphData
 */
function getData() {
    // dataDICT 在 data.js
    
    // 顯示文章
    let html = "";
    let peopleList = [];          // 最後要輸出的 list[dict]
    let peopleSet = new Set();    // 用來記錄每個 JSON 字串，防止重複
    let placeLIST = [];
    let placeSet = new Set();      // 用來記錄每個 JSON 字串，防止重複
    let entityLIST = [];          // 用來記錄所有 Entity 的結果
    let entitySet = new Set();    // 用來記錄每個 JSON 字串，防止重複
    let eventLIST = [];          // 用來記錄所有事件的結果
    let eventSet = new Set();    // 用來記錄每個 JSON 字串，防止重複

    dataDICT.articles.forEach(function (article) {
        // 收集人物
        _collectEntities(article.peoples, peopleSet, peopleList, 'peoples');
        // 收集地點
        _collectEntities(article.places, placeSet, placeLIST, 'places');
        // 收集Entity
        _collectEntities(article.entities, entitySet, entityLIST, 'entities');
        // 收集 event
        const events = article.events || [];
        events.forEach(function (event) {
            // 去重
            const hash = JSON.stringify(event);
            if (!eventSet.has(hash)) {
                eventSet.add(hash);
                eventLIST.push(event);
            }
        });

        // 組合文章
        html += `
        <div class="articleBlock">
            <h3>${article.title}</h3>
            <div class="content">${article.content}</div>
        </div>
    `;
    });

    $("#articlePresent").html(html);
    eventLIST.sort((a, b) => new Date(a.date_only) - new Date(b.date_only));
    const eventMap = {};
    eventLIST.forEach(event => {
        const date = event.date_only;
        if (!eventMap[date]) {
            eventMap[date] = [];
        }
        eventMap[date].push(event);
    });

    // 更新知識
    _renderEntityList(peopleList, '#peopleTable');
    _renderEntityList(placeLIST, '#placeTable');
    _renderEntityList(entityLIST, '#entityTable');

    // 更新全域變數
    _renderGlobalEntities(dataDICT.global_entities);
    _onEventMapReceived(eventMap);
}

/**
 * 根據 entities 動態插入 時序圖 欄位的 checkbox
 * @param {*} entities
 */
function _renderGlobalEntities(entities) {
    // 填寫 人
    const peopleLIST = entities.peoples || [];

    const peopleHTML = peopleLIST.map(person => `
    <label style="display:inline-block; margin-right:10px;">
        <input type="checkbox" class="entity-checkbox" value="${person}" checked>
        <label class="form-check-label highlight_yellow" for="flexCheckChecked">
            ${person}
        </label>
    </label>
  `).join("");

    // 填寫 地點
    const placeLIST = entities.places || [];

    const placeHTML = placeLIST.map(place => `
    <label style="display:inline-block; margin-right:10px;">
        <input type="checkbox" class="entity-checkbox" value="${place}" checked>
        <label class="form-check-label highlight_pink" for="flexCheckChecked">
            ${place}
        </label>
    </label>
  `).join("");

    // 填寫 實體
    const entityLIST = entities.entities || []

    const entityHTML = entityLIST.map(entity => `
    <label style="display:inline-block; margin-right:10px;">
        <input type="checkbox" class="entity-checkbox" value="${entity}" checked>
        <label class="form-check-label highlight_blue" for="flexCheckChecked">
            ${entity}
        </label>
    </label>
  `).join("");

    if (peopleLIST.length > 0) {
        document.getElementById("entityCheckboxContainer").innerHTML =
            `<strong>人物</strong><br>` + peopleHTML + `<br><br>`;
    }
    else {
        document.getElementById("entityCheckboxContainer").innerHTML =
        `<strong>人物</strong><br>無`
    }

    if (placeLIST.length > 0) {
        document.getElementById("entityCheckboxContainer").innerHTML +=
            `<strong>地點</strong><br>` + placeHTML + `<br><br>`;
    }
    else {
        document.getElementById("entityCheckboxContainer").innerHTML =
        `<strong>地點</strong><br>無`
    }

    if (entityLIST.length > 0) {
        document.getElementById("entityCheckboxContainer").innerHTML +=
            `<strong>實體</strong><br>` + entityHTML;
    }
    else {
        document.getElementById("entityCheckboxContainer").innerHTML =
        `<strong>實體</strong><br>無`
    }

}

/**
 * 接收後端傳回的事件資料 eventMap，
 * 並初始化 forceGraph 與產生 MermaidGraph 所需的文字格式。
 *
 * @param {Object} receivedEventMap - 日期為 key、事件陣列為 value 的物件。
 */
function _onEventMapReceived(receivedEventMap) {
    // forceGraph的部分

    // 將 eventMap 存到全域變數 G_EventMap
    G_EventMap = receivedEventMap;
    // 收集所有勾選的 checkbox 的 entity
    $(".entity-checkbox:checked").each(function () {
        G_SelectedEntity_LIST.push($(this).val());
    });

    if (isElementInViewport(document.getElementById("relationGraph"))) {
        initForceGraph();
    }

    if (isElementInViewport(document.getElementById("sequenceDiagram"))) {
        initMermaid();
    }
}

function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top < window.innerHeight &&
        rect.bottom > 0 &&
        rect.left < window.innerWidth &&
        rect.right > 0
    );
}

/**
 * 收集並去除重複的實體資料（人物、地點、entity）。
 * 每筆資料用 JSON 字串比較，避免重複加入結果清單。
 *
 * @param {Object} source - 原始實體資料，格式為 { name: [record, ...] }。
 * @param {Set} set - 用於去重的 Set。
 * @param {Array} list - 最後要輸出的實體清單。
 * @param {string} label - 類型名稱（例如 'peoples', 'places'），目前未使用。
 */
function _collectEntities(source, set, list, label) {
    const entries = source || {};
    Object.entries(entries).forEach(function ([name, record]) {
        let fullObject = { name: name, data: record };
        let hash = JSON.stringify(fullObject);
        if (!set.has(hash)) {
            set.add(hash);
            list.push(fullObject);
        }
    });
}

/**
 * 將實體清單渲染為 HTML，使用 Bootstrap 的 collapse 元件顯示細節。
 *
 * @param {Array} myList - 包含實體名稱與資料的物件陣列。
 * @param {string} containerSelector - 放置 HTML 的容器選擇器（例如 '#peopleTable'）。
 */
function _renderEntityList(myList, containerSelector) {
    let html = '';
    const typeSTR = containerSelector.replace("#", "");

    myList.forEach((item, index) => {        
        const collapseId = `${typeSTR}collapseItem${index}`;

        // 按鈕 + 內容 包在一個有 margin 的區塊中
        html += `
      <div class="mb-3">
        <p>
          <button class="btn btn-primary" type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#${collapseId}"
                  aria-expanded="false"
                  aria-controls="${collapseId}">
            ${item.name}
          </button>
        </p>

        <div class="collapse" id="${collapseId}">
          <div class="card card-body">
            ${Object.entries(item.data).map(([key, values]) => (
            `<strong>${key}:</strong> ${values.join('、')}<br>`
        )).join('')
            }
          </div>
        </div>
      </div>
    `;
    });

    $(containerSelector).html(html);
}