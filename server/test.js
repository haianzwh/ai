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

app.listen(3001, '0.0.0.0', () => console.log('running'));
