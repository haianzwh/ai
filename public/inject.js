(function() {
  'use strict';

  function checkAuth() {
    if (!localStorage.getItem('auth_token')) {
      window.location.replace('/login.html');
      return false;
    }
    return true;
  }

  if (!checkAuth()) return;

  setInterval(function() {
    if (!localStorage.getItem('auth_token')) window.location.replace('/login.html');
  }, 30000);

  window.addEventListener('storage', function(e) {
    if (e.key === 'auth_token' && !e.newValue) window.location.replace('/login.html');
  });

  window.addEventListener('pageshow', function(e) {
    if (e.persisted && !localStorage.getItem('auth_token')) window.location.replace('/login.html');
  });

  var u = JSON.parse(localStorage.getItem('user_info') || '{}');
  var name = u.username || 'admin';
  var av = name.charAt(0).toUpperCase();
  var isMobile = window.innerWidth < 768;

  var s = document.createElement('style');
  s.textContent = [
    // 桌面端: 右上角浮动菜单
    '.cm{position:fixed;top:8px;right:12px;z-index:99999;display:flex;align-items:center;gap:6px;padding:5px 8px;border-radius:24px;background:rgba(30,30,40,.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);box-shadow:0 4px 20px rgba(0,0,0,.25);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;transition:all .3s}',
    '.cm:hover{opacity:1!important;padding:6px 14px;gap:10px}',
    '.ca{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#fff;flex-shrink:0;text-transform:uppercase;box-shadow:0 2px 8px rgba(99,102,241,.35)}',
    '.cd{color:rgba(255,255,255,.5);font-size:17px;text-decoration:none;display:flex;align-items:center;line-height:1;flex-shrink:0;cursor:pointer;padding:3px 2px}',
    '.cd:hover{color:#fff}',

    // 隐藏文本和退出按钮，hover 显示
    '.cmn,.cmo{width:0;opacity:0;overflow:hidden;white-space:nowrap;transition:all .3s}',
    '.cm:hover .cmn{width:auto;opacity:1;font-size:13px;font-weight:500;color:rgba(255,255,255,.85);max-width:80px;text-overflow:ellipsis}',
    '.cm:hover .cmo{width:auto;opacity:1;padding:5px 12px;background:transparent;border:1px solid rgba(239,68,68,.35);border-radius:14px;color:rgba(239,68,68,.8);font-size:12px;cursor:pointer;font-weight:500;margin-left:2px}',
    '.cmo:hover{background:rgba(239,68,68,.15)!important;border-color:rgba(239,68,68,.6)!important;color:#ef4444!important}',

    // 移动端: 底部导航栏
    '@media(max-width:767px){',
    '  .cm{top:auto;bottom:0;right:0;left:0;opacity:1;padding:0;border-radius:0;border:none;border-top:1px solid rgba(255,255,255,.1);background:rgba(20,20,35,.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);justify-content:space-around;height:56px}',
    '  .cm:hover{padding:0;gap:0}',
    '  .ca{width:30px;height:30px;font-size:12px;margin:0 4px}',
    '  .cd{font-size:20px;padding:6px 12px;flex-direction:column;align-items:center;gap:2px;color:rgba(255,255,255,.4)}',
    '  .cd:hover{color:#6366f1}',
    '  .cmn{width:auto!important;opacity:1!important;font-size:10px;font-weight:400;color:rgba(255,255,255,.3);max-width:none}',
    '  .cmo{width:auto!important;opacity:1!important;font-size:10px;border-color:rgba(239,68,68,.25);padding:4px 10px;border-radius:10px;margin:0}',
    '  .cm:hover .cmn,.cm:hover .cmo{width:auto;opacity:1}',
    '  body{padding-bottom:56px}',  // 为底部导航留空间
    '}',
  ].join('');
  document.head.appendChild(s);

  var m = document.createElement('div');
  m.className = 'cm';
  m.innerHTML =
    '<div class="ca">'+av+'</div>' +
    '<span class="cd" id="btnProjects">&#x1F4C1;<span class="cmn">项目</span></span>' +
    '<span class="cd" id="btnUpload">&#x1F4E4;<span class="cmn">上传</span></span>' +
    '<span class="cd" id="btnRanking">&#x1F3C6;<span class="cmn">排行</span></span>' +
    '<span class="cmn" style="margin:0 4px">'+name+'</span>' +
    '<button class="cmo">退出</button>';
  document.body.appendChild(m);

  function navTo(url) {
    window.top.location = url;
  }

  document.getElementById('btnProjects').addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation(); navTo('/projects.html');
  });
  document.getElementById('btnUpload').addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation(); navTo('/upload.html');
  });
  document.getElementById('btnRanking').addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation(); navTo('/ranking.html');
  });

  m.querySelector('.cmo').addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation();
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    document.cookie = 'auth_token=;path=/;max-age=0';
    window.location.replace('/login.html');
  });
})();
