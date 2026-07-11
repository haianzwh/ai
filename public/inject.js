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

  var s = document.createElement('style');
  s.textContent = [
    '.cm{position:fixed;top:56px;right:16px;z-index:99999;display:flex;align-items:center;gap:6px;padding:6px;border-radius:24px;background:rgba(30,30,40,.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);box-shadow:0 4px 20px rgba(0,0,0,.25);opacity:.7;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;transition:all .3s}',
    '.cm:hover{opacity:1;padding:8px 14px;gap:10px}',
    '.ca{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;color:#fff;flex-shrink:0;text-transform:uppercase;box-shadow:0 2px 8px rgba(99,102,241,.35)}',
    '.cd{color:rgba(255,255,255,.5);font-size:18px;text-decoration:none;display:flex;align-items:center;line-height:1;flex-shrink:0;position:relative;z-index:99999}.cd:hover{color:#fff}',
    '.cn,.co{width:0;opacity:0;overflow:hidden;white-space:nowrap;transition:all .3s}',
    '.cm:hover .cn{width:auto;opacity:1;font-size:13px;font-weight:500;color:rgba(255,255,255,.85);max-width:70px;text-overflow:ellipsis}',
    '.cm:hover .co{width:auto;opacity:1;padding:5px 12px;background:transparent;border:1px solid rgba(239,68,68,.35);border-radius:14px;color:rgba(239,68,68,.8);font-size:12px;cursor:pointer;font-weight:500}',
    '.co:hover{background:rgba(239,68,68,.15)!important;border-color:rgba(239,68,68,.6)!important;color:#ef4444!important}',
    '@media(max-width:768px){.cm{top:48px;right:10px;padding:5px}.cm:hover{padding:6px 10px;gap:6px}.ca{width:28px;height:28px;font-size:13px}}'
  ].join('');
  document.head.appendChild(s);

  var m = document.createElement('div');
  m.className = 'cm';
  m.innerHTML = '<div class="ca">'+av+'</div><span class="cd" style="cursor:pointer" title="项目管理" id="projLink">&#x1F4C1;</span><span class="cn">'+name+'</span><button class="co">退出</button>';
  document.body.appendChild(m);

  document.getElementById('projLink').addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation();
    window.top.location = '/projects.html';
  });

  m.querySelector('.co').addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation();
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    document.cookie = 'auth_token=;path=/;max-age=0';
    window.location.replace('/login.html');
  });
})();
