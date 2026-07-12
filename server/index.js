const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') return res.status(400).json({ success: false, message: '请求格式错误' });
  next(err);
});

const JWT_SECRET = 'secret';
const MAX_FILES = 100;
const FILE_DIR = '/tmp/opencode/generated_files';

// 确保文件目录存在
if (!fs.existsSync(FILE_DIR)) fs.mkdirSync(FILE_DIR, { recursive: true });

const db = mysql.createPool({
  host: 'localhost', user: 'root', password: '88311807ZWh123!',
  database: 'aichat', connectionLimit: 10
});

// 中间件：验证登录
function auth(req, res, next) {
  const headerToken = (req.headers.authorization || '').replace('Bearer ', '');
  const cookies = (req.headers.cookie || '').split(';').reduce((acc, c) => {
    const [k, v] = c.trim().split('=');
    if (k) acc[k] = v;
    return acc;
  }, {});
  const token = headerToken || cookies.auth_token;
  if (!token) return res.status(401).json({ error: '请先登录' });
  try { 
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next(); 
  }
  catch(e) { res.status(401).json({ error: '登录已过期' }); }
}

// Auth APIs
app.post('/api/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const [users] = await db.query('SELECT * FROM users WHERE username = ? AND status = ?', [username, 'active']);
    if (!users.length) return res.status(401).json({ success: false, message: '用户名或密码错误' });
    const match = await bcrypt.compare(password, users[0].password);
    if (!match) return res.status(401).json({ success: false, message: '用户名或密码错误' });
    const token = jwt.sign({ id: users[0].id, username: users[0].username }, JWT_SECRET, { expiresIn: '24h' });
    await db.query('UPDATE users SET last_login = NOW() WHERE id = ?', [users[0].id]);
    res.json({ success: true, token, user: { id: users[0].id, username: users[0].username, email: users[0].email } });
  } catch (e) { res.status(500).json({ success: false, message: e.message }); }
});

app.post('/api/auth/register', async (req, res) => {
  try {
    const { username, password, email } = req.body;
    if (!username || username.length < 3 || username.length > 20 || !/^[a-zA-Z0-9_]+$/.test(username))
      return res.status(400).json({ success: false, message: '用户名3-20位，字母数字下划线' });
    if (!password || password.length < 8 || !/[a-zA-Z]/.test(password) || !/[0-9]/.test(password))
      return res.status(400).json({ success: false, message: '密码至少8位，含字母和数字' });
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      return res.status(400).json({ success: false, message: '邮箱格式不正确' });
    const [existing] = await db.query('SELECT id FROM users WHERE username = ?', [username]);
    if (existing.length) return res.status(409).json({ success: false, message: '用户名已存在' });
    const hash = await bcrypt.hash(password, 10);
    const [r] = await db.query('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, hash, email]);
    res.json({ success: true, userId: r.insertId });
  } catch (e) { res.status(500).json({ success: false, message: e.message }); }
});

app.post('/api/auth/forgot-password', async (req, res) => {
  try {
    const { username, email } = req.body;
    if (!username || !email) return res.status(400).json({ success: false, message: '请输入用户名和邮箱' });
    const [users] = await db.query('SELECT id FROM users WHERE username = ? AND email = ?', [username, email]);
    if (!users.length) return res.status(404).json({ success: false, message: '用户名或邮箱不匹配' });
    res.json({ success: true, message: '重置链接已生成' });
  } catch (e) { res.status(500).json({ success: false, message: e.message }); }
});

// 项目列表（按当前用户过滤）
app.get('/api/projects', auth, async (req, res) => {
  try {
    const currentUser = req.user.username;
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
    
    // 获取用户关联的 session
    const [userSessions] = await db.query('SELECT session_id FROM user_sessions WHERE username = ?', [currentUser]);
    const userSessionIds = new Set(userSessions.map(r => r.session_id));
    
    const projects = (data.data || [])
      .filter(s => userSessionIds.has(s.id))
      .map(s => ({
        id: s.id, title: s.title || '未命名',
        dir: s.location?.directory || '/home',
        updated: new Date(s.time.updated).toLocaleString('zh-CN'),
        tokens: (s.tokens?.input||0) + (s.tokens?.output||0),
      }));
    
    res.json({ success: true, projects, username: currentUser });
  } catch (e) { res.json({ success: true, projects: [] }); }
});

// 创建新项目
app.post('/api/projects', auth, async (req, res) => {
  try {
    const resp = await fetch('http://localhost:4096/api/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await resp.json();
    const sessionId = data.data?.id;
    
    if (sessionId) {
      await db.query('INSERT IGNORE INTO user_sessions (username, session_id, tokens_input, tokens_output, tokens_reasoning) VALUES (?, ?, 0, 0, 0)',
        [req.user.username, sessionId]);
      res.json({ success: true, id: sessionId, title: data.data.title || '新项目' });
    } else {
      res.status(500).json({ success: false, message: '创建失败' });
    }
  } catch (e) {
    res.status(500).json({ success: false, message: e.message });
  }
});

// 清理项目文件夹：保留最新 MAX_FILES 个文件
function cleanDir(dir) {
  if (!dir.includes('generated_files')) return; // 安全检查：只清理 generated_files 目录
  try {
    const files = fs.readdirSync(dir).map(f => {
      const fp = path.join(dir, f);
      return { name: f, path: fp, mtime: fs.statSync(fp).mtime };
    }).sort((a, b) => b.mtime - a.mtime);
    
    for (let i = MAX_FILES; i < files.length; i++) {
      fs.unlinkSync(files[i].path);
    }
  } catch(e) {}
}

// 项目文件列表（需登录）
app.get('/api/projects/:id/files', auth, async (req, res) => {
  const seen = new Set();
  const files = [];
  const dirs = ['/tmp/opencode', '/home/ubuntu'];
  
  for (const d of dirs) {
    try {
      const out = execSync(`find ${d} -maxdepth 3 -type f -newer /tmp/opencode/ai-chat -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/ai-chat/*' -not -path '*/.cache/*' -not -path '*/.npm/*' -not -path '*/server/*' -not -path '*/src/*' -not -name '*.js' -not -name '*.ts' -not -name '*.vue' -not -name '*.json' -not -name '*.css' -not -name '*.lock' -not -name '*.log' -not -name '*.toml' -not -name '*.cfg' -not -name '.*' 2>/dev/null || true`, { encoding: 'utf8', timeout: 5000 });
      for (const f of out.trim().split('\n')) {
        if (!f || seen.has(f) || f.endsWith('.log') || f.endsWith('.lock')) continue;
        const stat = fs.statSync(f);
        if (stat.size < 50) continue;
        seen.add(f);
        files.push({ name: path.basename(f), path: f, size: stat.size, mtime: stat.mtime.toISOString() });
      }
    } catch(e) {}
  }
  files.sort((a,b) => new Date(b.mtime) - new Date(a.mtime));
  
  // 复制到项目目录并限制100个
  const projectDir = path.join(FILE_DIR, req.params.id.substring(0, 8));
  if (!fs.existsSync(projectDir)) fs.mkdirSync(projectDir, { recursive: true });
  
  for (const f of files.slice(0, MAX_FILES)) {
    const dest = path.join(projectDir, f.name);
    if (!fs.existsSync(dest)) {
      try { fs.copyFileSync(f.path, dest); } catch(e) {}
    }
  }
  cleanDir(projectDir);
  
  res.json({ success: true, files: files.slice(0, MAX_FILES) });
});

// 下载单个文件（需登录）
app.get('/api/download/file', auth, (req, res) => {
  const fp = req.query.path;
  if (!fp || !fs.existsSync(fp)) return res.status(404).end();
  res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(path.basename(fp))}"`);
  fs.createReadStream(fp).pipe(res);
});

// 按项目打包下载（需登录）
app.get('/api/download/project/:id', auth, (req, res) => {
  try {
    const projectDir = path.join(FILE_DIR, req.params.id.substring(0, 8));
    if (!fs.existsSync(projectDir)) return res.status(404).json({ error: '项目无文件' });
    
    const tarPath = `/tmp/project-${req.params.id.substring(0,8)}.tar.gz`;
    execSync(`tar -czf ${tarPath} -C ${projectDir} . 2>/dev/null || true`, { timeout: 10000 });
    if (!fs.existsSync(tarPath) || fs.statSync(tarPath).size < 100)
      return res.status(404).json({ error: '无文件' });
    
    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition', `attachment; filename=project-${req.params.id.substring(0,8)}.tar.gz`);
    fs.createReadStream(tarPath).pipe(res);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// 一键下载最新生成文件
app.get('/api/download/latest', auth, (req, res) => {
  try {
    const tarPath = '/tmp/latest-generated.tar.gz';
    execSync(`cd /tmp/opencode && tar -czf ${tarPath} --exclude=ai-chat --exclude=node_modules --exclude=.git --exclude='*.log' --exclude='*.lock' --exclude='*.js' --exclude='*.mjs' --exclude='*.json' --newer /tmp/opencode/ai-chat/login.html . 2>/dev/null || true`, { timeout: 10000 });
    if (!fs.existsSync(tarPath) || fs.statSync(tarPath).size < 100)
      return res.status(404).json({ error: '没有新文件' });
    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition', 'attachment; filename=generated-files.tar.gz');
    fs.createReadStream(tarPath).pipe(res);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.listen(3001, '0.0.0.0', () => console.log('running'));

// Token 统计排名
app.get('/api/stats/ranking', auth, async (req, res) => {
  try {
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
    const sessions = data.data || [];
    
    // 按项目/目录聚合 token
    const projectStats = {};
    for (const s of sessions) {
      const key = s.title || '未命名';
      if (!projectStats[key]) {
        projectStats[key] = { name: key, input: 0, output: 0, reasoning: 0, sessions: 0, dir: s.location?.directory || '' };
      }
      projectStats[key].input += s.tokens?.input || 0;
      projectStats[key].output += s.tokens?.output || 0;
      projectStats[key].reasoning += s.tokens?.reasoning || 0;
      projectStats[key].sessions += 1;
    }
    
    const ranking = Object.values(projectStats)
      .map(p => ({ ...p, total: p.input + p.output + p.reasoning }))
      .sort((a, b) => b.total - a.total);
    
    const totals = ranking.reduce((acc, p) => {
      acc.input += p.input;
      acc.output += p.output;
      acc.reasoning += p.reasoning;
      acc.total += p.total;
      acc.sessions += p.sessions;
      return acc;
    }, { input: 0, output: 0, reasoning: 0, total: 0, sessions: 0 });
    
    res.json({ success: true, ranking: ranking.slice(0, 50), totals });
  } catch (e) {
    res.status(500).json({ success: false, message: e.message });
  }
});

// 用户排名
app.get('/api/stats/users', auth, async (req, res) => {
  try {
    const currentUser = req.user;
    const isAdmin = currentUser.username === 'admin';
    
    // 获取所有 opencode sessions
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
    const sessions = data.data || [];
    
    // 获取已记录的 session
    const [recorded] = await db.query('SELECT session_id FROM user_sessions');
    const recordedIds = new Set(recorded.map(r => r.session_id));
    
    // 归还未记录的 sessions 给当前用户
    let newTokens = 0;
    for (const s of sessions) {
      if (!recordedIds.has(s.id)) {
        const input = s.tokens?.input || 0;
        const output = s.tokens?.output || 0;
        const reasoning = s.tokens?.reasoning || 0;
        const total = input + output + reasoning;
        if (total > 0) {
          await db.query('INSERT IGNORE INTO user_sessions (username, session_id, tokens_input, tokens_output, tokens_reasoning) VALUES (?, ?, ?, ?, ?)',
            [currentUser.username, s.id, input, output, reasoning]);
          newTokens += total;
        }
      }
    }
    
    // 更新当前用户token
    if (newTokens > 0) {
      await db.query('UPDATE users SET total_tokens = COALESCE(total_tokens,0) + ?, last_active = NOW() WHERE username = ?', [newTokens, currentUser.username]);
    } else {
      await db.query('UPDATE users SET last_active = NOW() WHERE username = ?', [currentUser.username]);
    }
    
    const totalTokens = sessions.reduce((s, x) => s + (x.tokens?.input||0) + (x.tokens?.output||0) + (x.tokens?.reasoning||0), 0);
    
    const [users] = await db.query('SELECT id, username, email, created_at, last_login, last_active, COALESCE(total_tokens,0) AS total_tokens FROM users WHERE status = ? ORDER BY COALESCE(total_tokens,0) DESC', ['active']);
    
    const ONLINE_THRESHOLD = 30 * 60 * 1000;
    const now = Date.now();
    
    function mask(s) {
      if (!s) return '';
      if (s.length <= 2) return s[0] + '*';
      return s.substring(0, 1) + '*'.repeat(Math.min(s.length - 2, 4)) + s.substring(s.length - 1);
    }
    
    const userList = users.map(u => {
      const isMe = u.id === currentUser.id;
      return {
        id: u.id,
        username: isAdmin || isMe ? u.username : mask(u.username),
        email: isAdmin || isMe ? u.email : mask(u.email),
        totalTokens: u.total_tokens,
        isMe,
        isOnline: u.last_active ? (now - new Date(u.last_active).getTime()) < ONLINE_THRESHOLD : false,
        lastLogin: u.last_login ? new Date(u.last_login).toLocaleString('zh-CN') : '从未登录',
      };
    });
    
    res.json({ success: true, users: userList, totalSessions: sessions.length, totalTokens, currentUser: currentUser.username });
  } catch (e) {
    res.status(500).json({ success: false, message: e.message });
  }
});
