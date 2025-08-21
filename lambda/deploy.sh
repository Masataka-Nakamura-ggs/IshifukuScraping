#!/bin/bash
# AWS Lambda デプロイメントスクリプト

set -e

echo "🚀 石福金属興業スクレイパーのLambdaデプロイを開始..."

# 1. 依存関係のインストール
echo "📦 依存関係をインストール中..."
pip install -r requirements.txt -t .

# 2. 不要なファイルを削除
echo "🧹 不要なファイルをクリーンアップ中..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# 3. デプロイメントパッケージを作成
echo "📦 デプロイメントパッケージを作成中..."
zip -r lambda-deployment-package.zip . -x "*.git*" "*.pytest_cache*" "*__pycache__*" "deploy.sh" "*.md"

echo "✅ デプロイメントパッケージが作成されました: lambda-deployment-package.zip"
echo ""
echo "📋 次のステップ:"
echo "1. AWS CLIでLambda関数を作成またはアップデート"
echo "2. Chrome Lambda Layerを追加"
echo "3. 環境変数を設定"
echo ""
echo "例: aws lambda update-function-code --function-name ishifuku-scraper --zip-file fileb://lambda-deployment-package.zip"
