/**
 * ==============================================================
 * AI Chat 后端 API 服务器
 * 技术栈: Node.js + Express + MySQL + JWT
 * 端口: 3001 (通过 nginx /auth/ 反向代理)
 * ==============================================================
 */

// ---------- 依赖引入 ----------
const express = require('express');          // Web 框架
const mysql = require('mysql2/promise');      // MySQL 数据库连接池
const bcrypt = require('bcryptjs');           // 密码哈希加密
const jwt = require('jsonwebtoken');          // JSON Web Token 身份验证
const { spawn } = require('child_process');  // 安全调用系统命令(代替 execSync)
const fs = require('fs');                     // 文件系统操作
const path = require('path');                 // 路径处理
const crypto = require('crypto');             // 加密随机数生成

const app = express();

// 解析 JSON 请求体, 限制最大 100KB 防止内存攻击
app.use(express.json({ limit: '100kb' }));

// JSON 解析错误处理 (如格式不正确的请求体)
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed')
    return res.status(400).json({ success: false, message: '请求格式错误' });
  next(err);
});

// ---------- 配置 ----------
// JWT 密钥: 从环境变量读取, 未设置则每次重启生成随机密钥(会导致旧token失效)
const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(64).toString('hex');

// 每个项目最多保留的文件数
const MAX_FILES = 100;

// 生成文件存放的基础目录
const FILE_DIR = '/tmp/opencode/generated_files';

// ---------- 安全: 文件下载白名单 ----------
// 只有这些目录下的文件允许被下载, 防止路径遍历攻击读取系统文件
const ALLOWED_DIRS = [
  '/tmp/opencode/generated_files',
  '/tmp/opencode',
  '/home/ubuntu',
].map(d => path.resolve(d));  // 转为绝对路径, 防止符号链接和 .. 攻击

// 检查目标路径是否在白名单内
function isPathAllowed(target) {
  const resolved = path.resolve(target);  // 规范化路径, 消除 ..
  return ALLOWED_DIRS.some(dir => resolved.startsWith(dir));
}

// 确保文件存放目录存在
if (!fs.existsSync(FILE_DIR)) fs.mkdirSync(FILE_DIR, { recursive: true });

// ---------- MySQL 数据库连接池 ----------
const db = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',     // 数据库地址
  user: process.env.DB_USER || 'root',           // 数据库用户名
  password: process.env.DB_PASSWORD,             // 数据库密码(必须通过环境变量设置)
  database: process.env.DB_NAME || 'aichat',     // 数据库名
  connectionLimit: 10,                            // 最大同时连接数
});

// ---------- 内存频率限制器 ----------
// 不做持久化, 服务重启后清零
const rateLimitMap = new Map();

// key: 限制标识(如 "login:192.168.1.1")
// max: 窗口内最大请求数
// windowMs: 时间窗口(毫秒)
// 返回 false 表示超限
function rateLimit(key, max = 10, windowMs = 60000) {
  const now = Date.now();
  if (!rateLimitMap.has(key)) rateLimitMap.set(key, []);
  // 先清理窗口之外的旧记录
  const timestamps = rateLimitMap.get(key).filter(t => now - t < windowMs);
  if (timestamps.length >= max) return false;  // 超过限制
  timestamps.push(now);                         // 记录本次请求
  rateLimitMap.set(key, timestamps);
  return true;
}

// ---------- 认证中间件 ----------
// 支持两种方式传 token:
//   1. HTTP Header: Authorization: Bearer <token>
//   2. Cookie: auth_token=<token>
// 解析后验证 JWT, 失败返回 401
function auth(req, res, next) {
  // 从 Header 中提取 token (去掉 "Bearer " 前缀)
  const headerToken = (req.headers.authorization || '').replace('Bearer ', '');
  
  // 从 Cookie 中解析 auth_token
  const cookies = (req.headers.cookie || '').split(';').reduce((acc, c) => {
    const [k, v] = c.trim().split('=');
    if (k) acc[k] = v;
    return acc;
  }, {});
  
  // 优先使用 Header token, 否则使用 Cookie token
  const token = headerToken || cookies.auth_token;
  if (!token) return res.status(401).json({ error: '请先登录' });
  
  try {
    // 验证JWT并解码出用户信息 { id, username }
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;   // 把用户信息挂到请求对象上, 后续路由可用
    next();               // 放行
  } catch(e) {
    res.status(401).json({ error: '登录已过期' });
  }
}

// ==============================================================
// API 路由
// ==============================================================

// ---------- POST /api/auth/login 用户登录 ----------
app.post('/api/auth/login', async (req, res) => {
  try {
    const ip = req.ip;
    // 频率限制: 同一IP每分钟最多10次登录尝试, 防暴力破解
    if (!rateLimit('login:' + ip, 10, 60000))
      return res.status(429).json({ success: false, message: '请求过于频繁，请稍后再试' });

    const { username, password } = req.body;
    if (!username || !password)
      return res.status(400).json({ success: false, message: '请输入用户名和密码' });

    // 查询用户 (只查 status='active' 的活跃用户)
    const [users] = await db.query(
      'SELECT * FROM users WHERE username = ? AND status = ?',
      [username, 'active']
    );
    if (!users.length)
      return res.status(401).json({ success: false, message: '用户名或密码错误' });

    // bcrypt 比对密码 (数据库中存的是哈希值, 不存明文)
    const match = await bcrypt.compare(password, users[0].password);
    if (!match)
      return res.status(401).json({ success: false, message: '用户名或密码错误' });

    // 生成 JWT, 有效期24小时
    const token = jwt.sign(
      { id: users[0].id, username: users[0].username },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    // 更新最后登录时间
    await db.query('UPDATE users SET last_login = NOW() WHERE id = ?', [users[0].id]);

    // 返回 token 和用户信息 (不含密码)
    res.json({
      success: true,
      token,
      user: { id: users[0].id, username: users[0].username, email: users[0].email }
    });
  } catch (e) {
    res.status(500).json({ success: false, message: '服务器内部错误' });
  }
});

// ---------- POST /api/auth/register 用户注册 ----------
app.post('/api/auth/register', async (req, res) => {
  try {
    const ip = req.ip;
    // 频率限制: 同一IP每分钟最多5次注册, 防恶意注册
    if (!rateLimit('register:' + ip, 5, 60000))
      return res.status(429).json({ success: false, message: '请求过于频繁，请稍后再试' });

    const { username, password, email } = req.body;

    // 用户名校验: 3-20位, 只能包含字母数字下划线
    if (!username || username.length < 3 || username.length > 20 ||
        !/^[a-zA-Z0-9_]+$/.test(username))
      return res.status(400).json({ success: false, message: '用户名3-20位，字母数字下划线' });

    // 密码校验: 至少8位, 必须包含字母和数字
    if (!password || password.length < 8 ||
        !/[a-zA-Z]/.test(password) || !/[0-9]/.test(password))
      return res.status(400).json({ success: false, message: '密码至少8位，含字母和数字' });

    // 邮箱格式校验
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      return res.status(400).json({ success: false, message: '邮箱格式不正确' });

    // 查重: 用户名是否已存在
    const [existing] = await db.query('SELECT id FROM users WHERE username = ?', [username]);
    if (existing.length)
      return res.status(409).json({ success: false, message: '用户名已存在' });

    // 密码加盐哈希 (cost factor=10)
    const hash = await bcrypt.hash(password, 10);

    // 写入数据库
    const [r] = await db.query(
      'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
      [username, hash, email]
    );
    res.json({ success: true, userId: r.insertId });
  } catch (e) {
    res.status(500).json({ success: false, message: '服务器内部错误' });
  }
});

// ---------- POST /api/auth/forgot-password 忘记密码 ----------
app.post('/api/auth/forgot-password', async (req, res) => {
  try {
    const ip = req.ip;
    if (!rateLimit('forgot:' + ip, 5, 60000))
      return res.status(429).json({ success: false, message: '请求过于频繁，请稍后再试' });

    const { username, email } = req.body;
    if (!username || !email)
      return res.status(400).json({ success: false, message: '请输入用户名和邮箱' });

    // 验证用户名和邮箱是否匹配
    const [users] = await db.query(
      'SELECT id FROM users WHERE username = ? AND email = ?',
      [username, email]
    );
    if (!users.length)
      return res.status(404).json({ success: false, message: '用户名或邮箱不匹配' });

    // 当前仅提示联系管理员重置, 未实现自动重置密码
    res.json({ success: true, message: '请联系管理员重置密码' });
  } catch (e) {
    res.status(500).json({ success: false, message: '服务器内部错误' });
  }
});

// ---------- GET /api/projects 获取当前用户的项目列表 ----------
app.get('/api/projects', auth, async (req, res) => {
  try {
    const currentUser = req.user.username;
    
    // 从 opencode 获取所有 session(会话)
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();

    // 从数据库查当前用户关联的 session 列表
    const [userSessions] = await db.query(
      'SELECT session_id FROM user_sessions WHERE username = ?',
      [currentUser]
    );
    const userSessionIds = new Set(userSessions.map(r => r.session_id));

    // 过滤: 只返回属于当前用户的 session
    const projects = (data.data || [])
      .filter(s => userSessionIds.has(s.id))
      .map(s => ({
        id: s.id,
        title: s.title || '未命名',
        dir: s.location?.directory || '/home',
        updated: new Date(s.time.updated).toLocaleString('zh-CN'),
        tokens: (s.tokens?.input || 0) + (s.tokens?.output || 0),
      }));

    res.json({ success: true, projects, username: currentUser });
  } catch (e) {
    res.json({ success: true, projects: [] });
  }
});

// ---------- POST /api/projects 创建新项目(会话) ----------
app.post('/api/projects', auth, async (req, res) => {
  try {
    // 通过 opencode API 创建一个新 session
    const resp = await fetch('http://localhost:4096/api/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await resp.json();
    const sessionId = data.data?.id;

    if (sessionId) {
      // 把新 session 绑定到当前用户名下
      await db.query(
        'INSERT IGNORE INTO user_sessions (username, session_id, tokens_input, tokens_output, tokens_reasoning) VALUES (?, ?, 0, 0, 0)',
        [req.user.username, sessionId]
      );
      res.json({ success: true, id: sessionId, title: data.data.title || '新项目' });
    } else {
      res.status(500).json({ success: false, message: '创建失败' });
    }
  } catch (e) {
    res.status(500).json({ success: false, message: '创建失败' });
  }
});

// ---------- 辅助函数: 清理项目文件夹中的旧文件 ----------
// 保留最新的 MAX_FILES 个文件, 删除其余
function cleanDir(dir) {
  // 安全校验: 只允许清理 generated_files 目录下的文件
  if (!dir.includes('generated_files')) return;
  try {
    // 读取目录所有文件, 按修改时间倒序排列
    const files = fs.readdirSync(dir).map(f => {
      const fp = path.join(dir, f);
      return { name: f, path: fp, mtime: fs.statSync(fp).mtime };
    }).sort((a, b) => b.mtime - a.mtime);  // 最新的排前面
    
    // 删除超过上限的旧文件
    for (let i = MAX_FILES; i < files.length; i++) {
      fs.unlinkSync(files[i].path);
    }
  } catch(e) {}
}

// ---------- 辅助函数: 用 find 命令搜索生成文件 ----------
// 使用 spawn (而非 execSync) 防止命令注入攻击
function execFind(dir) {
  return new Promise((resolve) => {
    const files = [];
    const args = [
      dir,                           // 搜索目录
      '-maxdepth', '3',              // 最多搜3层目录
      '-type', 'f',                  // 只找文件, 不找目录
      '-newer', '/tmp/opencode/ai-chat',  // 只找比项目时间新的文件
      // 排除规则: 避免收录源代码和系统文件
      '-not', '-path', '*/node_modules/*',
      '-not', '-path', '*/.git/*',
      '-not', '-path', '*/ai-chat/*',     // 排除后端代码
      '-not', '-path', '*/.cache/*',
      '-not', '-path', '*/.npm/*',
      '-not', '-path', '*/server/*',      // 排除服务端目录
      '-not', '-path', '*/src/*',          // 排除源码目录
      '-not', '-name', '*.js',            // 排除 JS 源码
      '-not', '-name', '*.ts',            // 排除 TypeScript
      '-not', '-name', '*.vue',           // 排除 Vue 组件
      '-not', '-name', '*.json',          // 排除 JSON 配置
      '-not', '-name', '*.css',           // 排除样式文件
      '-not', '-name', '*.lock',          // 排除 lock 文件
      '-not', '-name', '*.log',           // 排除日志文件
      '-not', '-name', '*.toml',          // 排除 TOML 配置
      '-not', '-name', '*.cfg',           // 排除配置文件
      '-not', '-name', '.*',              // 排除隐藏文件
    ];
    // spawn: 参数以数组形式传递, 无法注入命令
    const proc = spawn('find', args, {
      timeout: 5000,
      stdio: ['ignore', 'pipe', 'ignore']  // 忽略 stdin/stderr, 只读 stdout
    });
    let output = '';
    proc.stdout.on('data', chunk => output += chunk.toString());
    proc.on('close', () => {
      for (const f of output.trim().split('\n')) {
        if (f) files.push(f);
      }
      resolve(files);
    });
    proc.on('error', () => resolve([]));  // 出错返回空数组
  });
}

// ---------- GET /api/projects/:id/files 获取项目的文件列表 ----------
app.get('/api/projects/:id/files', auth, async (req, res) => {
  const seen = new Set();           // 去重: 防止同名文件重复
  const files = [];
  const dirs = ['/tmp/opencode', '/home/ubuntu'];  // 搜索目录

  // 遍历每个搜索目录, 收集生成的文件
  for (const d of dirs) {
    const out = await execFind(d);
    for (const f of out) {
      if (seen.has(f) || f.endsWith('.log') || f.endsWith('.lock')) continue;
      try {
        const stat = fs.statSync(f);
        if (stat.size < 50) continue;  // 跳过太小的文件 (<50字节)
        seen.add(f);
        files.push({
          name: path.basename(f),
          path: f,
          size: stat.size,
          mtime: stat.mtime.toISOString()
        });
      } catch(e) {}
    }
  }

  // 按修改时间倒序
  files.sort((a, b) => new Date(b.mtime) - new Date(a.mtime));

  // 把文件复制到项目专属目录 (方便打包下载)
  const projectDir = path.join(FILE_DIR, req.params.id.substring(0, 8));
  if (!fs.existsSync(projectDir)) fs.mkdirSync(projectDir, { recursive: true });

  for (const f of files.slice(0, MAX_FILES)) {
    const dest = path.join(projectDir, f.name);
    if (!fs.existsSync(dest)) {
      try { fs.copyFileSync(f.path, dest); } catch(e) {}
    }
  }

  // 清理超过100个的旧文件
  cleanDir(projectDir);

  res.json({ success: true, files: files.slice(0, MAX_FILES) });
});

// ---------- GET /api/download/file 下载单个文件 ----------
// 调用方式: /api/download/file?path=/tmp/opencode/xxx.pptx
app.get('/api/download/file', auth, (req, res) => {
  const fp = req.query.path;
  if (!fp) return res.status(400).end();

  // 安全校验: 路径必须在白名单内, 防止读取 /etc/passwd 等系统文件
  if (!isPathAllowed(fp))
    return res.status(403).json({ error: '不允许的路径' });

  if (!fs.existsSync(fp)) return res.status(404).end();

  // 确保是文件不是目录
  const stat = fs.statSync(fp);
  if (!stat.isFile()) return res.status(400).json({ error: '不是文件' });

  // 设置下载响应头 (Content-Disposition 让浏览器下载而非预览)
  res.setHeader('Content-Disposition',
    `attachment; filename="${encodeURIComponent(path.basename(fp))}"`);

  // 流式传输文件内容到客户端
  const stream = fs.createReadStream(fp);
  stream.on('error', () => res.status(500).end());
  stream.pipe(res);
});

// ---------- GET /api/download/project/:id 按项目打包下载 ----------
app.get('/api/download/project/:id', auth, async (req, res) => {
  try {
    // 项目文件保存在 generated_files/<session前8位>/
    const projectDir = path.join(FILE_DIR, req.params.id.substring(0, 8));
    if (!fs.existsSync(projectDir))
      return res.status(404).json({ error: '项目无文件' });

    // 随机文件名: 防止并发冲突和其他进程读取 temp 文件
    const tarPath = path.join('/tmp',
      `project-${crypto.randomBytes(8).toString('hex')}.tar.gz`);

    // 用 tar 打包 (spawn 安全执行, 参数数组传参)
    const proc = spawn('tar', ['-czf', tarPath, '-C', projectDir, '.'], {
      timeout: 10000,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    await new Promise((resolve, reject) => {
      proc.on('close', (code) => code === 0 ? resolve() : reject());
      proc.on('error', reject);
    });

    // 打包为空则清理并返回404
    if (!fs.existsSync(tarPath) || fs.statSync(tarPath).size < 100) {
      try { fs.unlinkSync(tarPath); } catch(e) {}
      return res.status(404).json({ error: '无文件' });
    }

    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition',
      `attachment; filename=project-${req.params.id.substring(0, 8)}.tar.gz`);

    // 流式传输, 传输完成后自动清理临时文件
    const stream = fs.createReadStream(tarPath);
    stream.on('close', () => { try { fs.unlinkSync(tarPath); } catch(e) {} });
    stream.on('error', () => { try { fs.unlinkSync(tarPath); } catch(e) {} });
    stream.pipe(res);
  } catch (e) {
    res.status(500).json({ error: '打包失败' });
  }
});

// ---------- GET /api/download/latest 一键下载最新生成文件 ----------
app.get('/api/download/latest', auth, async (req, res) => {
  try {
    const tarPath = path.join('/tmp',
      `latest-${crypto.randomBytes(8).toString('hex')}.tar.gz`);

    const proc = spawn('tar', [
      '-czf', tarPath,
      '-C', '/tmp/opencode',               // 从 /tmp/opencode 打包
      '--exclude=ai-chat',                  // 排除后端代码
      '--exclude=node_modules',
      '--exclude=.git',
      '--exclude=*.log',
      '--exclude=*.lock',
      '--exclude=*.js',
      '--exclude=*.mjs',
      '--exclude=*.json',
      '--newer', '/tmp/opencode/ai-chat/login.html',  // 只打比项目新的文件
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
  } catch (e) {
    res.status(500).json({ error: '打包失败' });
  }
});

// ==============================================================
// 统计与排名 API
// ==============================================================

// ---------- GET /api/stats/ranking 项目(会话) Token 排名 ----------
app.get('/api/stats/ranking', auth, async (req, res) => {
  try {
    // 从 opencode 获取所有会话数据 (包含 token 用量)
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
    const sessions = data.data || [];

    // 按项目标题聚合 Token 统计
    const projectStats = {};
    for (const s of sessions) {
      const key = s.title || '未命名';  // 以标题为聚合键
      if (!projectStats[key]) {
        projectStats[key] = {
          name: key, input: 0, output: 0, reasoning: 0,
          sessions: 0, dir: s.location?.directory || ''
        };
      }
      projectStats[key].input += s.tokens?.input || 0;           // 输入token
      projectStats[key].output += s.tokens?.output || 0;         // 输出token
      projectStats[key].reasoning += s.tokens?.reasoning || 0;   // 推理token
      projectStats[key].sessions += 1;                            // 会话计数
    }

    // 计算总 token 并排序 (从高到低)
    const ranking = Object.values(projectStats)
      .map(p => ({ ...p, total: p.input + p.output + p.reasoning }))
      .sort((a, b) => b.total - a.total);

    // 汇总所有项目的总计
    const totals = ranking.reduce((acc, p) => {
      acc.input += p.input;
      acc.output += p.output;
      acc.reasoning += p.reasoning;
      acc.total += p.total;
      acc.sessions += p.sessions;
      return acc;
    }, { input: 0, output: 0, reasoning: 0, total: 0, sessions: 0 });

    // 返回前50名
    res.json({ success: true, ranking: ranking.slice(0, 50), totals });
  } catch (e) {
    res.status(500).json({ success: false, message: '获取失败' });
  }
});

// ---------- GET /api/stats/users 用户 Token 排名 ----------
app.get('/api/stats/users', auth, async (req, res) => {
  try {
    const currentUser = req.user;                           // 当前登录用户
    const isAdmin = currentUser.username === 'admin';       // 是否管理员

    // 获取所有 opencode 会话
    const resp = await fetch('http://localhost:4096/api/session');
    const data = await resp.json();
    const sessions = data.data || [];

    // 获取数据库中已记录的 session (防重复计费)
    const [recorded] = await db.query('SELECT session_id FROM user_sessions');
    const recordedIds = new Set(recorded.map(r => r.session_id));

    // 将未记录的 session 归属给当前用户
    let newTokens = 0;
    for (const s of sessions) {
      if (!recordedIds.has(s.id)) {
        const input = s.tokens?.input || 0;
        const output = s.tokens?.output || 0;
        const reasoning = s.tokens?.reasoning || 0;
        const total = input + output + reasoning;
        if (total > 0) {
          // INSERT IGNORE: 防止并发重复插入
          await db.query(
            'INSERT IGNORE INTO user_sessions (username, session_id, tokens_input, tokens_output, tokens_reasoning) VALUES (?, ?, ?, ?, ?)',
            [currentUser.username, s.id, input, output, reasoning]
          );
          newTokens += total;
        }
      }
    }

    // 更新当前用户的累计 Token 和活跃时间
    if (newTokens > 0) {
      await db.query(
        'UPDATE users SET total_tokens = COALESCE(total_tokens,0) + ?, last_active = NOW() WHERE username = ?',
        [newTokens, currentUser.username]
      );
    } else {
      await db.query('UPDATE users SET last_active = NOW() WHERE username = ?',
        [currentUser.username]);
    }

    // 全部用户的 token 统计
    const totalTokens = sessions.reduce(
      (s, x) => s + (x.tokens?.input || 0) + (x.tokens?.output || 0) + (x.tokens?.reasoning || 0),
      0
    );

    // 查询所有活跃用户, 按 token 总量排序
    const [users] = await db.query(
      'SELECT id, username, email, created_at, last_login, last_active, COALESCE(total_tokens,0) AS total_tokens FROM users WHERE status = ? ORDER BY COALESCE(total_tokens,0) DESC',
      ['active']
    );

    // 在线判断阈值: 30分钟内活跃=在线
    const ONLINE_THRESHOLD = 30 * 60 * 1000;
    const now = Date.now();

    // 隐私遮蔽函数: 只显示首尾字符, 中间用 * 代替
    function mask(s) {
      if (!s) return '';
      if (s.length <= 2) return s[0] + '*';
      return s.substring(0, 1) + '*'.repeat(Math.min(s.length - 2, 4)) + s.substring(s.length - 1);
    }

    // 构建用户列表 (含隐私控制)
    const userList = users.map(u => {
      const isMe = u.id === currentUser.id;
      return {
        id: u.id,
        // 管理员和本人可以看到真实用户名/邮箱, 其他人看到的是遮蔽版本
        username: isAdmin || isMe ? u.username : mask(u.username),
        email: isAdmin || isMe ? u.email : mask(u.email),
        totalTokens: u.total_tokens,
        isMe,                                                           // 是否是当前用户
        isOnline: u.last_active ?
          (now - new Date(u.last_active).getTime()) < ONLINE_THRESHOLD : false,  // 是否在线
        lastLogin: u.last_login ?
          new Date(u.last_login).toLocaleString('zh-CN') : '从未登录',
      };
    });

    res.json({
      success: true,
      users: userList,
      totalSessions: sessions.length,
      totalTokens,
      currentUser: currentUser.username
    });
  } catch (e) {
    res.status(500).json({ success: false, message: '获取失败' });
  }
});

// ---------- 启动检查: 必须设置 DB_PASSWORD ----------
if (!process.env.DB_PASSWORD) {
  console.error('错误: 请设置 DB_PASSWORD 环境变量');
  process.exit(1);
}

// ---------- 启动服务器 ----------
app.listen(3001, '0.0.0.0', () => console.log('running'));
