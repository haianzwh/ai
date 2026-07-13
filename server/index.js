const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
app.use(express.json({ limit: '100kb' }));
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') return res.status(400).json({ success: false, message: '请求格式错误' });
  next(err);
});

const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(64).toString('hex');
const MAX_FILES = 100;
const FILE_DIR = '/tmp/opencode/generated_files';

// Allowed directories for file download
const ALLOWED_DIRS = [
  '/tmp/opencode/generated_files',
  '/tmp/opencode',
  '/home/ubuntu',
].map(d => path.resolve(d));

function isPathAllowed(target) {
  const resolved = path.resolve(target);
  return ALLOWED_DIRS.some(dir => resolved.startsWith(dir));
}

if (!fs.existsSync(FILE_DIR)) fs.mkdirSync(FILE_DIR, { recursive: true });

const db = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME || 'aichat',
  connectionLimit: 10,
});

// In-memory rate limiter
const rateLimitMap = new Map();
function rateLimit(key, max = 10, windowMs = 60000) {
  const now = Date.now();
  if (!rateLimitMap.has(key)) rateLimitMap.set(key, []);
  const timestamps = rateLimitMap.get(key).filter(t => now - t < windowMs);
  if (timestamps.length >= max) return false;
  timestamps.push(now);
  rateLimitMap.set(key, timestamps);
  return true;
}

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
  } catch(e) { res.status(401).json({ error: '登录已过期' }); }
}

app.post('/api/auth/login', async (req, res) => {
  try {
    const ip = req.ip;
    if (!rateLimit('login:' + ip, 10, 60000))
      return res.status(429).json({ success: false, message: '请求过于频繁，请稍后再试' });
    const { username, password } = req.body;
    if (!username || !password)
      return res.status(400).json({ success: false, message: '请输入用户名和密码' });
    const [users] = await db.query('SELECT * FROM users WHERE username = ? AND status = ?', [username, 'active']);
    if (!users.length) return res.status(401).json({ success: false, message: '用户名或密码错误' });
    const match = await bcrypt.compare(password, users[0].password);
    if (!match) return res.status(401).json({ success: false, message: '用户名或密码错误' });
    const token = jwt.sign({ id: users[0].id, username: users[0].username }, JWT_SECRET, { expiresIn: '24h' });
    await db.query('UPDATE users SET last_login = NOW() WHERE id = ?', [users[0].id]);
    res.json({ success: true, token, user: { id: users[0].id, username: users[0].username, email: users[0].email } });
  } catch (e) {
    res.status(500).json({ success: false, message: '服务器内部错误' });
  }
});

app.post('/api/auth/register', async (req, res) => {
  try {
    const ip = req.ip;
    if (!rateLimit('register:' + ip, 5, 60000))
      return res.status(429).json({ success: false, message: '请求过于频繁，请稍后再试' });
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
  } catch (e) {
    res.status(500).json({ success: false, message: '服务器内部错误' });
  }
});

app.post('/api/auth/forgot-password', async (req, res) => {
  try {
    const ip = req.ip;
    if (!rateLimit('forgot:' + ip, 5, 60000))
      return res.status(429).json({ success: false, message: '请求过于频繁，请稍后再试' });
    const { username, email } = req.body;
    if (!username || !email) return res.status(400).json({ success: false, message: '请输入用户名和邮箱' });
    const [users] = await db.query('SELECT id FROM users WHERE username = ? AND email = ?', [username, email]);
    if (!users.length) return res.status(404).json({ success: false, message: '用户名或邮箱不匹配' });
    res.json({ success: true, message: '请联系管理员重置密码' });
  } catch (e) {
    res.status(500).json({ success: false, message: '服务器内部错误' });
  }
});

app.get('/api/projects', auth, async (req, res) => {
  try {
    const currentUser = req.user.username;
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
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
    res.status(500).json({ success: false, message: '创建失败' });
  }
});

function cleanDir(dir) {
  if (!dir.includes('generated_files')) return;
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

function execFind(dir) {
  return new Promise((resolve) => {
    const files = [];
    const args = [
      dir, '-maxdepth', '3', '-type', 'f',
      '-newer', '/tmp/opencode/ai-chat',
      '-not', '-path', '*/node_modules/*',
      '-not', '-path', '*/.git/*',
      '-not', '-path', '*/ai-chat/*',
      '-not', '-path', '*/.cache/*',
      '-not', '-path', '*/.npm/*',
      '-not', '-path', '*/server/*',
      '-not', '-path', '*/src/*',
      '-not', '-name', '*.js',
      '-not', '-name', '*.ts',
      '-not', '-name', '*.vue',
      '-not', '-name', '*.json',
      '-not', '-name', '*.css',
      '-not', '-name', '*.lock',
      '-not', '-name', '*.log',
      '-not', '-name', '*.toml',
      '-not', '-name', '*.cfg',
      '-not', '-name', '.*',
    ];
    const proc = spawn('find', args, { timeout: 5000, stdio: ['ignore', 'pipe', 'ignore'] });
    let output = '';
    proc.stdout.on('data', chunk => output += chunk.toString());
    proc.on('close', () => {
      for (const f of output.trim().split('\n')) {
        if (f) files.push(f);
      }
      resolve(files);
    });
    proc.on('error', () => resolve([]));
  });
}

app.get('/api/projects/:id/files', auth, async (req, res) => {
  const seen = new Set();
  const files = [];
  const dirs = ['/tmp/opencode', '/home/ubuntu'];
  for (const d of dirs) {
    const out = await execFind(d);
    for (const f of out) {
      if (seen.has(f) || f.endsWith('.log') || f.endsWith('.lock')) continue;
      try {
        const stat = fs.statSync(f);
        if (stat.size < 50) continue;
        seen.add(f);
        files.push({ name: path.basename(f), path: f, size: stat.size, mtime: stat.mtime.toISOString() });
      } catch(e) {}
    }
  }
  files.sort((a,b) => new Date(b.mtime) - new Date(a.mtime));
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

app.get('/api/download/file', auth, (req, res) => {
  const fp = req.query.path;
  if (!fp) return res.status(400).end();
  if (!isPathAllowed(fp)) return res.status(403).json({ error: '不允许的路径' });
  if (!fs.existsSync(fp)) return res.status(404).end();
  const stat = fs.statSync(fp);
  if (!stat.isFile()) return res.status(400).json({ error: '不是文件' });
  res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(path.basename(fp))}"`);
  const stream = fs.createReadStream(fp);
  stream.on('error', () => res.status(500).end());
  stream.pipe(res);
});

app.get('/api/download/project/:id', auth, async (req, res) => {
  try {
    const projectDir = path.join(FILE_DIR, req.params.id.substring(0, 8));
    if (!fs.existsSync(projectDir)) return res.status(404).json({ error: '项目无文件' });
    const tarPath = path.join('/tmp', `project-${crypto.randomBytes(8).toString('hex')}.tar.gz`);
    const proc = spawn('tar', ['-czf', tarPath, '-C', projectDir, '.'], { timeout: 10000, stdio: ['ignore', 'pipe', 'pipe'] });
    await new Promise((resolve, reject) => {
      proc.on('close', (code) => code === 0 ? resolve() : reject());
      proc.on('error', reject);
    });
    if (!fs.existsSync(tarPath) || fs.statSync(tarPath).size < 100) {
      try { fs.unlinkSync(tarPath); } catch(e) {}
      return res.status(404).json({ error: '无文件' });
    }
    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition', `attachment; filename=project-${req.params.id.substring(0,8)}.tar.gz`);
    const stream = fs.createReadStream(tarPath);
    stream.on('close', () => { try { fs.unlinkSync(tarPath); } catch(e) {} });
    stream.on('error', () => { try { fs.unlinkSync(tarPath); } catch(e) {} });
    stream.pipe(res);
  } catch (e) { res.status(500).json({ error: '打包失败' }); }
});

app.get('/api/download/latest', auth, async (req, res) => {
  try {
    const tarPath = path.join('/tmp', `latest-${crypto.randomBytes(8).toString('hex')}.tar.gz`);
    const proc = spawn('tar', [
      '-czf', tarPath,
      '-C', '/tmp/opencode',
      '--exclude=ai-chat', '--exclude=node_modules', '--exclude=.git',
      '--exclude=*.log', '--exclude=*.lock', '--exclude=*.js',
      '--exclude=*.mjs', '--exclude=*.json',
      '--newer', '/tmp/opencode/ai-chat/login.html',
      '.'
    ], { timeout: 10000, stdio: ['ignore', 'pipe', 'pipe'] });
    await new Promise((resolve, reject) => {
      proc.on('close', (code) => code === 0 ? resolve() : reject());
      proc.on('error', reject);
    });
    if (!fs.existsSync(tarPath) || fs.statSync(tarPath).size < 100) {
      try { fs.unlinkSync(tarPath); } catch(e) {}
      return res.status(404).json({ error: '没有新文件' });
    }
    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition', 'attachment; filename=generated-files.tar.gz');
    const stream = fs.createReadStream(tarPath);
    stream.on('close', () => { try { fs.unlinkSync(tarPath); } catch(e) {} });
    stream.on('error', () => { try { fs.unlinkSync(tarPath); } catch(e) {} });
    stream.pipe(res);
  } catch (e) { res.status(500).json({ error: '打包失败' }); }
});

app.get('/api/stats/ranking', auth, async (req, res) => {
  try {
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
    const sessions = data.data || [];
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
      acc.input += p.input; acc.output += p.output; acc.reasoning += p.reasoning;
      acc.total += p.total; acc.sessions += p.sessions;
      return acc;
    }, { input: 0, output: 0, reasoning: 0, total: 0, sessions: 0 });
    res.json({ success: true, ranking: ranking.slice(0, 50), totals });
  } catch (e) { res.status(500).json({ success: false, message: '获取失败' }); }
});

app.get('/api/stats/users', auth, async (req, res) => {
  try {
    const currentUser = req.user;
    const isAdmin = currentUser.username === 'admin';
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
    const sessions = data.data || [];
    const [recorded] = await db.query('SELECT session_id FROM user_sessions');
    const recordedIds = new Set(recorded.map(r => r.session_id));
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
  } catch (e) { res.status(500).json({ success: false, message: '获取失败' }); }
});

if (!process.env.DB_PASSWORD) {
  console.error('错误: 请设置 DB_PASSWORD 环境变量');
  process.exit(1);
}

app.listen(3001, '0.0.0.0', () => console.log('running'));
