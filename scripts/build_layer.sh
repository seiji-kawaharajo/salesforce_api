#!/bin/bash

# スクリプトがあるディレクトリの絶対パスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "${SCRIPT_DIR}" )"

# --- 設定 ---
PYTHON_VERSION="3.12"
PROJECT_NAME="my-lambda-layer"
LAYER_ZIP_NAME="${PROJECT_ROOT}/${PROJECT_NAME}.zip"
LAYER_BUILD_DIR="${PROJECT_ROOT}/build/${PROJECT_NAME}_build"
LAYER_INNER_PATH="${LAYER_BUILD_DIR}/python/lib/python${PYTHON_VERSION}/site-packages"

# --- 実行 ---

echo "--- ${PROJECT_NAME} Lambdaレイヤーのビルドを開始します ---"

# 1. Ryeプロジェクトの依存関係を同期 (--no-dev を使用)
echo "1. Ryeの依存関係を同期しています (--no-dev を使用)..."
(cd "${PROJECT_ROOT}" && rye sync --no-dev) || { echo "Rye sync (no-dev) に失敗しました。終了します。"; exit 1; }

# 2. レイヤーの出力ディレクトリをクリーンアップし、作成
echo "2. 出力ディレクトリを準備しています..."
rm -rf "${LAYER_BUILD_DIR}"
mkdir -p "${LAYER_INNER_PATH}" || { echo "出力ディレクトリの作成に失敗しました。終了します。"; exit 1; }

# 3. 仮想環境からsite-packagesのパスを取得し、依存関係をコピー
echo "3. 仮想環境から依存関係をコピーしています..."
VENV_SITE_PACKAGES=$(cd "${PROJECT_ROOT}" && rye run python -c "import site; print(site.getsitepackages()[0])")

if [ -z "${VENV_SITE_PACKAGES}" ]; then
    echo "仮想環境のsite-packagesパスを見つけられませんでした。Rye syncが完了しているか確認してください。"
    exit 1
fi

cp -r "${VENV_SITE_PACKAGES}"/* "${LAYER_INNER_PATH}/" || { echo "ファイルのコピーに失敗しました。終了します。"; exit 1; }

# 4. ZIPアーカイブの作成
echo "4. ZIPアーカイブを作成しています..."
(cd "${LAYER_BUILD_DIR}" && zip -r "${LAYER_ZIP_NAME}" ./*) || { echo "ZIPアーカイブの作成に失敗しました。終了します。"; exit 1; }

# 5. 一時的なビルドディレクトリのクリーンアップ (オプション)
echo "5. 一時的なビルドディレクトリをクリーンアップしています..."
rm -rf "${LAYER_BUILD_DIR}"

# --- 追加: 開発環境を元の状態に戻す ---
echo "6. 開発環境のRye依存関係を同期し直しています..."
(cd "${PROJECT_ROOT}" && rye sync) || { echo "Rye sync (dev) に失敗しました。開発環境を手動で戻してください。"; }

echo "--- ビルドと環境復元が完了しました: ${LAYER_ZIP_NAME} ---"
