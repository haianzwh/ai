(function() {
  'use strict';

  function checkAuth() {
    var token = localStorage.getItem('auth_token');
    if (!token) {
      window.location.replace('/login.html');
      return false;
    }
    return true;
  }

  if (!checkAuth()) return;

  setInterval(function() {
    if (!localStorage.getItem('auth_token')) {
      window.location.replace('/login.html');
    }
  }, 30000);

  window.addEventListener('storage', function(e) {
    if (e.key === 'auth_token' && !e.newValue) {
      window.location.replace('/login.html');
    }
  });

  window.addEventListener('pageshow', function(e) {
    if (e.persisted) {
      if (!localStorage.getItem('auth_token')) {
        window.location.replace('/login.html');
      }
    }
  });

  var userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
  var username = userInfo.username || 'admin';
  var avatar = username.charAt(0).toUpperCase();

  var style = document.createElement('style');
  style.textContent = '.c-m{position:fixed;top:56px;right:16px;z-index:99999;display:flex;align-items:center;gap:0;padding:6px;border-radius:24px;background:rgba(30,30,40,.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);box-shadow:0 4px 20px rgba(0,0,0,.25);transition:all .3s ease;opacity:.7;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;overflow:hidden}' +
    '.c-m:hover{opacity:1;background:rgba(35,35,50,.92);border-color:rgba(255,255,255,.18);box-shadow:0 6px 24px rgba(0,0,0,.35);padding:8px 14px;gap:10px}' +
    '.c-a{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;color:#fff;flex-shrink:0;letter-spacing:0;line-height:1;text-transform:uppercase;box-shadow:0 2px 8px rgba(99,102,241,.35);transition:all .3s ease}' +
    '.c-n,.c-o{opacity:0;width:0;overflow:hidden;white-space:nowrap;transition:all .3s ease}' +
    '.c-m:hover .c-n{opacity:1;width:auto;font-size:13px;font-weight:500;color:rgba(255,255,255,.85);max-width:70px;text-overflow:ellipsis}' +
    '.c-m:hover .c-o{opacity:1;width:auto;padding:5px 12px;background:transparent;border:1px solid rgba(239,68,68,.35);border-radius:14px;color:rgba(239,68,68,.8);font-size:12px;cursor:pointer;font-weight:500;letter-spacing:.5px}' +
    '.c-o:hover{background:rgba(239,68,68,.15)!important;border-color:rgba(239,68,68,.6)!important;color:#ef4444!important}' +
    '@media(max-width:768px){.c-m{top:48px;right:10px;padding:5px}.c-m:hover{padding:6px 10px;gap:6px}.c-a{width:28px;height:28px;font-size:13px}.c-m:hover .c-n{font-size:12px;max-width:50px}.c-m:hover .c-o{padding:4px 8px;font-size:11px}}';
  document.head.appendChild(style);

  var menu = document.createElement('div');
  menu.className = 'c-m';
  menu.innerHTML = '<div class="c-a">' + avatar + '</div><span class="c-n">' + username + '</span><button class="c-o">退出</button>';
  document.body.appendChild(menu);

  menu.querySelector('.c-o').addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    document.cookie = 'auth_token=;path=/;max-age=0';
    window.location.replace('/login.html');
  });
})();
