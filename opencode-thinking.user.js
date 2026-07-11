// ==UserScript==
// @name         OpenCode Web - 中文思考过程
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  在 opencode web 中显示可折叠的中文思考过程
// @author       AI Chat
// @match        http://localhost:4096/*
// @match        http://43.155.173.12:4096/*
// @grant        GM_addStyle
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    // 注入自定义样式
    GM_addStyle(`
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
            cursor: pointer !important;
            user-select: none !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }

        .session-turn-thinking-heading::before {
            content: "💭" !important;
            font-size: 16px !important;
        }

        .session-turn-thinking-heading::after {
            content: "▼" !important;
            font-size: 10px !important;
            margin-left: auto !important;
            transition: transform 0.3s ease !important;
        }

        /* 折叠状态 */
        [data-slot="session-turn-thinking"].collapsed .session-turn-thinking-heading::after {
            transform: rotate(-90deg) !important;
        }

        [data-slot="session-turn-thinking"].collapsed [data-component="text-reveal"] {
            display: none !important;
        }

        /* 思考内容 */
        [data-slot="session-turn-thinking"] [data-component="text-reveal"] {
            margin-top: 12px !important;
            padding-top: 12px !important;
            border-top: 1px solid rgba(99, 102, 241, 0.1) !important;
            font-size: 13px !important;
            line-height: 1.6 !important;
            color: rgba(255, 255, 255, 0.7) !important;
            white-space: pre-wrap !important;
        }

        /* Spinner 样式 */
        [data-slot="session-turn-thinking"] [data-component="spinner"] {
            color: #6366f1 !important;
        }
    `);

    // 等待 DOM 加载完成
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setup);
        } else {
            setup();
        }
    }

    function setup() {
        // 监听 DOM 变化，添加折叠功能
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) {
                        const thinkingElements = node.querySelectorAll 
                            ? node.querySelectorAll('[data-slot="session-turn-thinking"]')
                            : [];
                        
                        if (node.matches && node.matches('[data-slot="session-turn-thinking"]')) {
                            setupThinkingElement(node);
                        }
                        
                        thinkingElements.forEach(setupThinkingElement);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // 处理已存在的元素
        document.querySelectorAll('[data-slot="session-turn-thinking"]').forEach(setupThinkingElement);
    }

    function setupThinkingElement(element) {
        if (element.dataset.thinkingSetup) return;
        element.dataset.thinkingSetup = 'true';

        const heading = element.querySelector('.session-turn-thinking-heading');
        if (heading) {
            // 修改标题为中文
            const originalText = heading.textContent;
            if (originalText.includes('Thinking') || originalText.includes('thinking')) {
                heading.textContent = '思考过程';
            }

            // 添加点击事件
            heading.addEventListener('click', (e) => {
                e.preventDefault();
                element.classList.toggle('collapsed');
            });
        }
    }

    init();
})();
