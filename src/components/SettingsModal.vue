<script setup lang="ts">
const emit = defineEmits<{
  close: []
}>()

function handleClose() {
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
      <div class="modal-header">
        <h2>设置</h2>
        <button class="close-btn" @click="handleClose">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <section class="settings-section">
          <h3>API 密钥管理</h3>
          <p class="section-desc">API 密钥通过命令行配置，存储在安全位置</p>

          <div class="auth-info">
            <div class="info-row">
              <span class="info-label">存储路径：</span>
              <code>~/.local/share/opencode/auth.json</code>
            </div>
            <div class="info-row">
              <span class="info-label">配置命令：</span>
              <code>opencode providers login</code>
            </div>
          </div>

          <div class="provider-status">
            <div class="status-item">
              <span class="status-dot active"></span>
              <span class="status-text">OpenCode Go - 已认证</span>
            </div>
          </div>

          <div class="help-text">
            <p>如需更换 API Key，请运行：</p>
            <code class="command-block">opencode providers logout && opencode providers login</code>
          </div>
        </section>

        <section class="settings-section">
          <h3>关于</h3>
          <div class="about-info">
            <p>AI Chat - 基于 OpenCode 的智能对话界面</p>
            <p class="version">版本 1.0.0</p>
          </div>
        </section>
      </div>

      <div class="modal-footer">
        <button class="close-footer-btn" @click="handleClose">关闭</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e8e8;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.settings-section {
  margin-bottom: 24px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.settings-section h3 {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px;
}

.section-desc {
  font-size: 13px;
  color: #999;
  margin: 0 0 16px;
}

.no-providers {
  text-align: center;
  padding: 24px;
  color: #999;
  background: #f8f9fa;
  border-radius: 8px;
}

.no-providers p {
  margin: 0;
}

.auth-info {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #666;
  flex-shrink: 0;
}

.info-row code {
  background: #e8e8e8;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #333;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
}

.provider-status {
  margin-bottom: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.active {
  background: #22c55e;
}

.status-text {
  font-size: 14px;
  color: #333;
}

.help-text {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 12px 16px;
}

.help-text p {
  margin: 0 0 8px;
  font-size: 13px;
  color: #92400e;
}

.help-text .command-block {
  display: block;
  background: #fef3c7;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #78350f;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.provider-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.input-group {
  display: flex;
  gap: 8px;
}

.api-key-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.api-key-input:focus {
  border-color: #4a9eff;
  box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
}

.toggle-visibility {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #fff;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.toggle-visibility:hover {
  background: #f5f5f5;
}

.toggle-visibility svg {
  width: 18px;
  height: 18px;
}

.about-info {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.about-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.about-info .version {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #e8e8e8;
}

.close-footer-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: #4a9eff;
  border: none;
  color: #fff;
}

.close-footer-btn:hover {
  background: #3a8eef;
}
</style>
