#!/bin/bash

# hadolint実行スクリプト
# ローカルでDockerfileの静的解析を実行

set -euo pipefail

# スクリプトがあるディレクトリの絶対パスを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"

echo "=== HadolintによるDockerfile静的解析を開始します ==="

# hadolintがインストールされているかチェック
if ! command -v hadolint &> /dev/null; then
    echo "hadolintがインストールされていません。"
    echo "インストール方法:"
    echo "  macOS: brew install hadolint"
    echo "  Linux: curl -L https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 -o /usr/local/bin/hadolint && chmod +x /usr/local/bin/hadolint"
    echo "  Windows: choco install hadolint"
    exit 1
fi

# 設定ファイルのパス
CONFIG_FILE="${PROJECT_ROOT}/.hadolint.yaml"

# Dockerfileのパス
DOCKERFILE="${PROJECT_ROOT}/.devcontainer/Dockerfile"

# 設定ファイルが存在するかチェック
if [[ ! -f "${CONFIG_FILE}" ]]; then
    echo "設定ファイルが見つかりません: ${CONFIG_FILE}"
    exit 1
fi

# Dockerfileが存在するかチェック
if [[ ! -f "${DOCKERFILE}" ]]; then
    echo "Dockerfileが見つかりません: ${DOCKERFILE}"
    exit 1
fi

echo "設定ファイル: ${CONFIG_FILE}"
echo "Dockerfile: ${DOCKERFILE}"
echo ""

# hadolintを実行
echo "hadolintを実行中..."
if hadolint --config "${CONFIG_FILE}" "${DOCKERFILE}"; then
    echo ""
    echo "✅ Hadolintの静的解析が完了しました。問題は見つかりませんでした。"
    exit 0
else
    echo ""
    echo "❌ Hadolintで問題が見つかりました。上記の警告・エラーを修正してください。"
    exit 1
fi
