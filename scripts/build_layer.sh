#!/bin/bash

# スクリプトがあるディレクトリの絶対パスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "${SCRIPT_DIR}" )"

# --- 設定 ---
PYTHON_VERSION="3.13"
PROJECT_NAME="salesforce-api-layer"
LAYER_ZIP_NAME="${PROJECT_ROOT}/${PROJECT_NAME}.zip"
LAYER_BUILD_DIR="${PROJECT_ROOT}/build/${PROJECT_NAME}_build"
LAYER_INNER_PATH="${LAYER_BUILD_DIR}/python/lib/python${PYTHON_VERSION}/site-packages"
MAX_LAYER_SIZE_MB=250

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

# 4. プロジェクトのソースコードをコピー
echo "4. プロジェクトのソースコードをコピーしています..."
cp -r "${PROJECT_ROOT}/src/"* "${LAYER_INNER_PATH}/" || { echo "src配下のコピーに失敗しました。終了します。"; exit 1; }

# 5. サイズ最適化
echo "5. サイズ最適化を実行しています..."
# Pythonキャッシュファイルを削除
find "${LAYER_INNER_PATH}" -name "*.pyc" -delete
find "${LAYER_INNER_PATH}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 不要なファイルを削除
find "${LAYER_INNER_PATH}" -name "*.pyo" -delete
find "${LAYER_INNER_PATH}" -name "*.pyd" -delete
find "${LAYER_INNER_PATH}" -name "*.so" -not -path "*/site-packages/*" -delete

# テストファイルを削除
find "${LAYER_INNER_PATH}" -path "*/tests/*" -type f -delete
find "${LAYER_INNER_PATH}" -path "*/test_*" -type f -delete
find "${LAYER_INNER_PATH}" -name "*_test.py" -delete

# ドキュメントファイルを削除
find "${LAYER_INNER_PATH}" -name "*.md" -delete
find "${LAYER_INNER_PATH}" -name "*.txt" -not -name "*.py" -delete
find "${LAYER_INNER_PATH}" -name "LICENSE" -delete
find "${LAYER_INNER_PATH}" -name "README*" -delete

# 6. 検証ステップ
echo "6. 検証を実行しています..."
# Layerサイズの確認
LAYER_SIZE_MB=$(du -sm "${LAYER_INNER_PATH}" | cut -f1)
echo "Layer size: ${LAYER_SIZE_MB}MB"

if [ "${LAYER_SIZE_MB}" -gt "${MAX_LAYER_SIZE_MB}" ]; then
    echo "警告: Layerサイズが${MAX_LAYER_SIZE_MB}MBを超えています (${LAYER_SIZE_MB}MB)"
    echo "不要な依存関係を削除することを検討してください。"

    # 大きなファイル/ディレクトリの一覧を表示
    echo "大きなファイル/ディレクトリ:"
    du -sh "${LAYER_INNER_PATH}"/* | sort -hr | head -10
fi

# 必須ファイルの存在確認
REQUIRED_FILES=("salesforce_api" "utils")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -d "${LAYER_INNER_PATH}/${file}" ]; then
        echo "エラー: 必須ディレクトリ '${file}' が見つかりません。"
        exit 1
    fi
done

echo "検証完了: 必須ファイルが正常に含まれています。"

# 7. ZIPアーカイブの作成
echo "7. ZIPアーカイブを作成しています..."
(cd "${LAYER_BUILD_DIR}" && zip -r "${LAYER_ZIP_NAME}" ./*) || { echo "ZIPアーカイブの作成に失敗しました。終了します。"; exit 1; }

# ZIPファイルサイズの確認
ZIP_SIZE_MB=$(du -sm "${LAYER_ZIP_NAME}" | cut -f1)
echo "ZIP file size: ${ZIP_SIZE_MB}MB"

# 8. 一時的なビルドディレクトリのクリーンアップ (オプション)
echo "8. 一時的なビルドディレクトリをクリーンアップしています..."
rm -rf "${LAYER_BUILD_DIR}"

# --- 追加: 開発環境を元の状態に戻す ---
echo "9. 開発環境のRye依存関係を同期し直しています..."
(cd "${PROJECT_ROOT}" && rye sync) || { echo "Rye sync (dev) に失敗しました。開発環境を手動で戻してください。"; }

echo "--- ビルドと環境復元が完了しました: ${LAYER_ZIP_NAME} ---"
echo "Layer size: ${LAYER_SIZE_MB}MB, ZIP size: ${ZIP_SIZE_MB}MB"
