#!/bin/bash
# WSL2 环境前置配置脚本
# 用途：在 WSL2 中启用 systemd、安装 Chrome 及中文字体
# 使用方式：sudo bash scripts/setup-wsl2.sh
# 完成后需要在 PowerShell 中执行 wsl --shutdown，再重新启动 WSL

set -e

# 检查是否在 WSL2 中
if ! grep -qi microsoft /proc/version 2>/dev/null; then
  echo "This script is for WSL2 environment only."
  exit 1
fi

# 检查 root 权限
if [ "$(id -u)" -ne 0 ]; then
  echo "Please run with sudo: sudo bash $0"
  exit 1
fi

echo "Setting up WSL2 environment for OpenClaw for Business..."

# 1) 在 WSL 里启用 systemd
echo "[Step 1/3] Enabling systemd in WSL..."
tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
echo "  Done. /etc/wsl.conf updated."

# 2) 安装 xvfb 和中文字体
echo "[Step 2/3] Installing xvfb and CJK fonts..."
apt update -qq
apt install -y fonts-noto-cjk fonts-noto-cjk-extra xvfb

# 3) 安装 Chrome
echo "[Step 3/3] Installing Google Chrome..."
wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i /tmp/chrome.deb || true
apt -f install -y
rm -f /tmp/chrome.deb

echo ""
echo "WSL2 setup complete!"
echo ""
echo "Next steps:"
echo "  1. Open PowerShell (on Windows) and run:  wsl --shutdown"
echo "  2. Restart WSL"
echo "  3. Continue with the OpenClaw installation (./scripts/dev.sh or ./scripts/reinstall-daemon.sh)"
