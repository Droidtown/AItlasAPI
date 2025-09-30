/**
 * 初始化圖表的函式
 * @returns  none
 */
function initForceGraph() {
    const elem = document.getElementById('graph');
    let dateSelector = document.getElementById('dateSelector');
    if (!dateSelector) {
        console.error('找不到 dateSelector');
        return;
    }
    const { width, height } = elem.getBoundingClientRect();

    G_ForceGraph = ForceGraph()(elem)
        .width(width)
        .height(height)
        .minZoom(1)
        .nodeLabel(node => node.id)
        .nodeCanvasObject((node, ctx, globalScale) => {
            const label = node.id;
            const fontSize = 16 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'black';
            ctx.fillText(label, node.x, node.y);
        })
        .nodePointerAreaPaint((node, color, ctx) => {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI, false);
            ctx.fill();
        })
        .linkDirectionalArrowLength(4)
        .linkDirectionalArrowRelPos(1)
        .linkCurvature('curvature')
        .linkCanvasObjectMode(() => 'after')
        .onNodeClick(node => {
            G_ForceGraph.centerAt(node.x, node.y, 1000);
            G_ForceGraph.zoom(4, 100);
        })
        .onNodeDragEnd(node => {
            node.fx = node.x;
            node.fy = node.y;
        })
        .onLinkClick((link, event) => {
            window.showLinkInfo(event.clientX, event.clientY, link);
        });

    // 註冊事件：下拉選單事件監聽
    dateSelector.addEventListener('change', (e) => {
        _updateGraphByDate(e.target.value);
    });

    // 預設初始設定
    // 使得頁面載入時選擇第一個日期並觸發一次圖表渲染。
    dateSelector = _initDateSelector(dateSelector);
    if (dateSelector.options.length > 0) {
        dateSelector.selectedIndex = 0;
        _updateGraphByDate(dateSelector.value);
    }
    G_ForceGraphInitialized = true
}

/**
 * 根據所選資料內的時間，製造出 DataSelector。
 *
 * 清空傳入的 dateSelecotr 元素，從 G_EventMap 中提取所有事件的日期。
 * 以 <option> 形式加入至下拉式選單中
 *
 * @param {HTMLElement} dateSelector - 欲插入日期選項的 <select> 元素
 * @returns {HTMLElement} dateSelector - 已插入日期選項的 <selecot> 元素
 */
// 設置日期下拉選單選項
function _initDateSelector(dateSelector) {
    // 清空再塞
    dateSelector.innerHTML = '';
    Object.keys(G_EventMap).forEach(date => {
        const option = document.createElement('option');
        option.value = date;
        option.textContent = date;
        dateSelector.appendChild(option);
    });
    return dateSelector
}

/**
 * 根據選擇的日期更新圖表資料
 *
 * 呼叫 _getGraphDataByDate 取得節點與連線資料。
 * 並將資料套用到 Graph 上，重渲染 forceGraph 圖。
 *
 * @param {string} dateStr - 要查詢的日期字串
 * @returns {void}
 */
function _updateGraphByDate(dateStr) {
    const data = _getGraphDataByDate(dateStr);
    G_ForceGraph.graphData(data);
}

/**
 * 根據指定日期取得圖形資料（節點與連線）。
 *
 * 會從 G_EventMap 中提取該日期的事件資料，
 * 建立唯一的節點清單與連線清單，若有雙向連線，會加入弧度來區分。
 *
 * @param {string} dateStr - 日期字串（例如 "2025-06-09"）
 * @returns {{ nodes: { id: string }[], links: { source: string, target: string, curvature: number }[] }}
 *          節點與連線的資料物件
 */
function _getGraphDataByDate(dateStr) {
    const events = G_EventMap[dateStr] || [];

    const nodeSet = new Set();
    events.forEach(e => {
        nodeSet.add(e.source);
        nodeSet.add(e.target);
    });
    const nodes = Array.from(nodeSet).map(id => ({ id }));

    const linkMap = new Map();
    const links = events.map(link => {
        const key = `${link.source}->${link.target}`;
        const reverseKey = `${link.target}->${link.source}`;
        const hasReverse = linkMap.has(reverseKey);
        linkMap.set(key, true);
        return { ...link, curvature: hasReverse ? 0.25 : 0 };
    });

    return { nodes, links };
}
