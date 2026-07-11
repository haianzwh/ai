const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

const db = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: '88311807ZWh123!',
  database: 'aichat',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    console.log('Login attempt:', username);
    const [users] = await db.query('SELECT * FROM users WHERE username = ? AND status = ?', [username, 'active']);
    console.log('Users found:', users.length);
    if (users.length === 0) return res.status(401).json({ success: false, message: '用户名或密码错误' });
    const user = users[0];
    const match = await bcrypt.compare(password, user.password);
    console.log('Password match:', match);
    if (!match) return res.status(401).json({ success: false, message: '用户名或密码错误' });
    const token = jwt.sign({ id: user.id, username: user.username }, 'secret', { expiresIn: '24h' });
    res.json({ success: true, message: '登录成功', token, user: { id: user.id, username: user.username } });
  } catch (e) {
    console.error('Error:', e.message);
    res.status(500).json({ success: false, message: e.message });
  }
});

app.post('/api/auth/register', async (req, res) => {
  try {
    const { username, password, email } = req.body;
    console.log('Register attempt:', username);
    
    // 用户名校验
    if (!username || username.trim() === '') {
      return res.status(400).json({ success: false, message: '用户名不能为空' });
    }
    if (username.length < 3 || username.length > 20) {
      return res.status(400).json({ success: false, message: '用户名长度必须在 3-20 位之间' });
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return res.status(400).json({ success: false, message: '用户名只能包含字母、数字和下划线' });
    }
    
    // 密码校验
    if (!password || password === '') {
      return res.status(400).json({ success: false, message: '密码不能为空' });
    }
    if (password.length < 8) {
      return res.status(400).json({ success: false, message: '密码长度至少 8 位' });
    }
    if (password.length > 50) {
      return res.status(400).json({ success: false, message: '密码长度不能超过 50 位' });
    }
    if (!/[a-zA-Z]/.test(password) || !/[0-9]/.test(password)) {
      return res.status(400).json({ success: false, message: '密码必须包含字母和数字' });
    }
    
    // 邮箱校验
    if (!email || email.trim() === '') {
      return res.status(400).json({ success: false, message: '邮箱不能为空' });
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return res.status(400).json({ success: false, message: '邮箱格式不正确' });
    }
    
    const [existing] = await db.query('SELECT id FROM users WHERE username = ?', [username]);
    if (existing.length > 0) {
      return res.status(409).json({ success: false, message: '用户名已存在' });
    }
    
    const hashedPassword = await bcrypt.hash(password, 10);
    const [result] = await db.query('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, hashedPassword, email]);
    
    res.json({ success: true, message: '注册成功', userId: result.insertId });
  } catch (e) {
    console.error('Register error:', e.message);
    res.status(500).json({ success: false, message: e.message });
  }
});

app.post('/api/auth/forgot-password', async (req, res) => {
  try {
    const { username, email } = req.body;
    console.log('Forgot password attempt:', username, email);
    
    if (!username || !email) {
      return res.status(400).json({ success: false, message: '用户名和邮箱不能为空' });
    }
    
    const [users] = await db.query('SELECT id, email FROM users WHERE username = ? AND email = ?', [username, email]);
    if (users.length === 0) {
      return res.status(404).json({ success: false, message: '用户名或邮箱不匹配' });
    }
    
    // 生成重置 token（实际项目中应该发送邮件）
    const resetToken = jwt.sign({ userId: users[0].id }, 'secret', { expiresIn: '1h' });
    console.log('Reset token:', resetToken);
    
    // TODO: 实际项目中应该发送邮件到用户邮箱
    res.json({ success: true, message: '重置密码邮件已发送（模拟）', resetToken });
  } catch (e) {
    console.error('Forgot password error:', e.message);
    res.status(500).json({ success: false, message: e.message });
  }
});

app.listen(3001, '0.0.0.0', () => console.log('running'));
