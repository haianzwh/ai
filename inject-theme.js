// 在浏览器控制台执行此脚本，或通过书签注入
(function() {
  const customCSS = `
    /* 思考过程容器 */
    [data-slot="session-turn-thinking"] {
      background: rgba(99, 102, 241, 0.05) !important;
      border: 1px solid rgba(99, 102, 241, 0.2) !important;
      border-radius: 8px !important;
      padding: 12px 16px !important;
      margin: 12px 0 !important;
      transition: all 0.3s ease !important;
    }

    [data-slot="session-turn-thinking"]:hover {
      background: rgba(99, 102, 241, 0.08) !important;
      border-color: rgba(99, 102, 241, 0.3) !important;
    }

    /* 思考标题 */
    .session-turn-thinking-heading {
      font-weight: 600 !important;
      color: #6366f1 !important;
    }

    /* 思考内容 */
    [data-slot="session-turn-thinking"] [data-component="text-reveal"] {
      margin-top: 12px !important;
      padding-top: 12px !important;
      border-top: 1px solid rgba(99, 102, 241, 0.1) !important;
      font-size: 13px !important;
      line-height: 1.6 !important;
      color: rgba(255, 255, 255, 0.7) !important;
    }
  `;

  // 注入到 localStorage
  localStorage.setItem('opencode-theme-css-dark', customCSS);
  localStorage.setItem('opencode-theme-css-light', customCSS);
  
  // 触发重新加载
  location.reload();
  
  console.log('✅ 主题 CSS 已注入，页面将重新加载');
})();
