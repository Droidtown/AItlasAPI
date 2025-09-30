/**
 * 新增事件監聽：監聽按下按鈕時有勾選的 checkbox，將內容傳給 Mermaid 並初始化。
 */
document.addEventListener("DOMContentLoaded", function () {
    // 綁定事件
    document.getElementById('submit-entity-selection').addEventListener('click', function () {
        G_SelectedEntity_LIST = []
        // 收集所有勾選的 checkbox 的 entity
        $(".entity-checkbox:checked").each(function () {
            G_SelectedEntity_LIST.push($(this).val());
        });

        console.log("你選擇了：", G_SelectedEntity_LIST);
        initMermaid();
    });
});

/**
 * 新增事件監聽：監聽 Mermaid 圖中的每一條訊息線（class="messageLine0"）。
 * 根據點擊的索引位置，從全域事件地圖 G_EventMap 中找出對應事件資料，
 * 並以 window.showLinkInfo() 顯示詳細資訊。
 */
$(document).on('click', '.messageLine0', function (event) {
    const allLines = $('.messageLine0');
    const clickedIndex = allLines.index(this); // 這是第n個事件

    // 找出第 clickedIndex 個事件
    const targetEvent = G_FilterEvent_LIST[clickedIndex];
    window.showLinkInfo(event.pageX, event.pageY, targetEvent);
});

/**
 * 初始化 Mermaid 時序圖。
 * - 檢查資料是否存在
 * - 設定 Mermaid 的樣式與主題
 * - 將 Mermaid 語法插入 DOM 並渲染圖表
 * - 呼叫 adjustActorRects() 調整參與者框框尺寸
 *
 * @returns none
 */
function initMermaid() {
    console.log("In initMermaid")

    // 將 G_EventMap 整理送到 G_Event_LIST
    G_Event_LIST = _parseMAP2LIST(G_EventMap)

    // 將 G_Event_LIST 根據 G_selectedEntity_LIST 的內容做篩選後送到 G_FilterEvent_LIST
    G_FilterEvent_LIST = _buildFilterEventLIST(G_Event_LIST, G_SelectedEntity_LIST)
    console.log(G_FilterEvent_LIST)
    if (G_FilterEvent_LIST.length === 0) {
        alert("在選取的人物中，沒有時序圖關係可以呈現");
        return;
    }
    G_MermaidGraphData = _genMermaidData(G_FilterEvent_LIST);
    mermaid.initialize({
        fontSize: '13px',
        theme: 'base',  // 一定要加這行，才能用 themeVariables 覆蓋預設
        themeVariables: {
            lineColor: '#666666',
            signalColor: '#666666',
            signalTextColor: '#666666',
            actorBorder: '#666666',
            actorTextColor: '#666666',
            actorBkg: '#f5f5f5',
            activationBorderColor: '#666666',
            activationBkgColor: '#eeeeee',
        }
    });

    const container = document.getElementById('mermaidGraph');
    if (!container) {
        console.error("找不到 mermaidGraph 容器");
        return;
    }
    container.innerHTML = '';  // 清空
    container.innerHTML = `<div class="mermaid">${G_MermaidGraphData}</div>`;

    mermaid.run({ nodes: [container.querySelector(".mermaid")] });
    G_MermaidGraphInitialized = true;

    _adjustActorRects({ paddingX: 12, paddingY: 6 });
}

/**
 * 將 G_Event_LIST 根據 selectedEntityLIST 的內容做篩選後送到 G_FilterEvent_LIST
 *
 * @param {Object} eventLIST
 * @param {Object} selectedEntityLIST
 * @return {Object} filterEventLIST
 */
function _buildFilterEventLIST(eventLIST, selectedEntityLIST) {
    let filterEventLIST = [];
    eventLIST.forEach(entry => {
        if (selectedEntityLIST.includes(entry.source) && selectedEntityLIST.includes(entry.target)) {
            filterEventLIST.push({
                "encounter_time": entry.encounter_time,
                "label": entry.label,
                "metaData": entry.metaData,
                "source": {
                    "id": entry.source
                },
                "target": {
                    "id": entry.target
                },
                "url": entry.url
            })
        }
    });

    return filterEventLIST
}

/**
 * 將 G_EventMap 整理送到 G_Event_LIST
 * @param {Object} G_EventMap
 * @return {Object} G_Event_LIST
 */
function _parseMAP2LIST(G_EventMap) {
    return Object.values(G_EventMap).flat();
}

/**
 * 調整 Mermaid 圖中每個 actor（參與者）的矩形框尺寸與位置，使其與文字對齊。
 * 使用字型大小與 padding 調整視覺效果。
 *
 * @param {Object} options - 可選參數：
 * @param {string} options.svgSelector - SVG 選擇器，預設為 '#mermaidGraph svg'
 * @param {number} options.paddingX - 水平方向的內距，預設為 12
 * @param {number} options.paddingY - 垂直方向的內距，預設為 6
 *
 * @returns {void}
 */
function _adjustActorRects({ svgSelector = '#mermaidGraph svg', paddingX = 12, paddingY = 6 } = {}) {
    document.fonts.ready.then(() => {
        setTimeout(() => {
            const svg = document.querySelector(svgSelector);
            if (!svg) return;

            // 控制 SVG 寬度不壓縮
            const viewBoxWidth = svg.viewBox.baseVal.width;
            svg.setAttribute('width', `${viewBoxWidth}px`);
            svg.style.width = `${viewBoxWidth}px`;
            svg.style.maxWidth = 'none';
            const fontSize = 13; // 預設字體大小

            // 調整每個 actor 的框框
            const groups = svg.querySelectorAll('g');
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    groups.forEach(group => {
                        const rect = group.querySelector('rect.actor');
                        const text = group.querySelector('text.actor');
                        const tspan = text ? text.querySelector('tspan') : null;

                        if (rect && text && tspan) {
                            const textX = parseFloat(text.getAttribute('x'));
                            const textY = parseFloat(text.getAttribute('y'));
                            const bbox = tspan.getBBox(); // 用來抓高度

                            let textWidth, textHeight;
                            try {
                                const bbox = tspan.getBBox();
                                if (bbox.width > 0 && bbox.height > 0) {
                                    textWidth = bbox.width;
                                    textHeight = bbox.height;
                                } else {
                                    throw new Error('bbox 為 0');
                                }
                            } catch (e) {
                                // fallback: 根據字數估算寬高
                                const textContent = tspan.textContent.trim();
                                textWidth = _estimateWidth(textContent);
                                textHeight = fontSize;
                            }
                            const rectX = textX - textWidth / 2 - paddingX;
                            const rectY = textY - textHeight / 2 - paddingY;
                            const rectWidth = textWidth + paddingX * 2;
                            const rectHeight = textHeight + paddingY * 2;

                            rect.setAttribute('x', rectX);
                            rect.setAttribute('y', rectY);
                            rect.setAttribute('width', rectWidth);
                            rect.setAttribute('height', rectHeight);
                        }
                    });
                })
            });
        }, 300); // 稍微等 Mermaid 渲染穩定
    });
}

/**
 * 粗略估算一段文字的寬度，用於 fallback 計算 actor 框框尺寸。
 * 英文與數字以 8px 寬處理，中文或其他字符以 12px 處理。
 *
 * @param {string} text - 要估算寬度的文字
 * @returns {number} - 估算的寬度（像素）
 */
function _estimateWidth(text) {
    let width = 0;
    for (let ch of text) {
        if (/[A-Za-z0-9]/.test(ch)) {
            width += 8; // 英文或數字
        } else {
            width += 12; // 中文或其他
        }
    }
    return width;
}

/**
 * 將事件資料 eventMap 轉換成 Mermaid 的 sequenceDiagram 格式。
 *
 * @param {Object} G_FilterEvent_LIST - 事件地圖
 * @returns {string} - Mermaid 語法的字串。
 */
function _genMermaidData(eventLIST) {
    let outputTEXT = "sequenceDiagram\n";
    const participantSET = new Set();

    // 加入 人、地點、實體
    eventLIST.forEach(entry => {
        if (!participantSET.has(entry.source.id)) {
            outputTEXT += `    participant ${entry.source.id}\n`;
            participantSET.add(entry.source.id);
        }
        if (!participantSET.has(entry.target.id)) {
            outputTEXT += `    participant ${entry.target.id}\n`;
            participantSET.add(entry.target.id);
        }
    });

    // 加入事件
    eventLIST.forEach(entry => {
        outputTEXT += `\n    ${entry.source.id}->>${entry.target.id}: ${entry.label}\n`;
    });

    return outputTEXT;
}