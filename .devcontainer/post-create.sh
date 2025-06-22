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

# Git設定（Docker Desktop環境の場合のみ）
if [ -z "$CODESPACES" ]; then
    echo "🔧 Configuring Git for Docker Desktop environment..."
    git config --global --add safe.directory '*'
    git config --global user.name 'seiji.kawaharajo'
    git config --global user.email 'seiji.kawaharajo@sol-tech.co.jp'
else
    echo "📝 Skipping Git configuration (Codespaces environment detected)"
fi

echo "✅ Post-create setup completed successfully!"

# pre-commitフックの自動インストール
echo "🔧 Installing pre-commit hooks..."
rye run pre-commit install
