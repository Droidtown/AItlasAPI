let G_EventMap = {};
let G_ForceGraph = {};
let G_ForceGraphInitialized = false;
let G_MermaidGraphInitialized = false;
let G_MermaidGraphData = {};
let G_Event_LIST = []
let G_FilterEvent_LIST = [];
let G_SelectedEntity_LIST = [];

/**
 * 從瀏覽器的 cookie 中取得指定名稱的值。
 * 為了取得 CSRF token。
 *
 * @param {string} name - 要查找的 cookie 名稱。
 * @returns {string|null} 對應的 cookie 值，若找不到則回傳 null。
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// 設定 jQuery 全域 AJAX 的 CSRF Token 標頭，避免跨站請求攻擊（CSRF）。
// 對非 GET 類型的請求自動加上 `X-CSRFToken` 標頭。
$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (!(/^GET|HEAD|OPTIONS|TRACE$/.test(settings.type)) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});

/**
 * 等待 DOM 完全載入後，註冊 tab 切換事件。
 * 針對兩個 tab：
 * - #relationGraph-tab：切換時檢查並初始化 force-graph。
 * - #sequenceDiagram-tab：切換時檢查並初始化 Mermaid 圖。
 */
document.addEventListener("DOMContentLoaded", function () {
  // 切到 #relationGraph-tab 這頁時，如果圖形還沒初始化，而且有資料可用，就初始化圖形。
  document.getElementById('relationGraph-tab').addEventListener('shown.bs.tab', () => {
    // console.log("關聯圖這頁被按到了")
    // console.log("初始化了?", G_ForceGraphInitialized)
    if (!G_ForceGraphInitialized) {
      initForceGraph();
    }
  });

  // 切到 #sequenceDiagram 這頁時，如果圖形還沒初始化，而且有資料可用，就初始化模型。
  document.getElementById('sequenceDiagram-tab').addEventListener('shown.bs.tab', () => {
    // console.log("時序圖這頁被按到了")
    // console.log("初始化了?", G_MermaidGraphInitialized, "有東西嗎?", G_MermaidGraphData)
    if (!G_MermaidGraphInitialized) {
      initMermaid();
    }
  })
});