#!/bin/bash
set -e

echo "🚀 Post-create setup starting..."

# Python環境の設定
echo "📦 Setting up Python environment..."
rye pin 3.13
rye sync

# Node.js依存関係のインストール
echo "📦 Installing Node.js dependencies..."
npm i

# Git設定
echo "🔧 Configuring Git..."
git config --global --add safe.directory '*'
git config --global user.name 'seiji.kawaharajo'
git config --global user.email 'seiji.kawaharajo@sol-tech.co.jp'

echo "✅ Post-create setup completed successfully!"
