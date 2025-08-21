# Lambda デプロイメントガイド

## 概要
石福金属興業の金価格スクレイピングをAWS Lambdaで実行するためのデプロイメント手順です。

## 前提条件

### 必要なツール
- AWS CLI v2
- AWS SAM CLI
- Docker
- Python 3.9+

### インストール手順

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# AWS SAM CLI
brew install aws-sam-cli

# AWS認証設定
aws configure
```

## デプロイメント方法

### 1. AWS SAMを使用（推奨）

```bash
cd lambda
./sam_deploy.sh dev ishifuku-gold-data
```

### 2. Serverless Frameworkを使用

```bash
cd lambda
npm install -g serverless
./deploy.sh dev
```

## 設定項目

### 環境変数
- `S3_BUCKET`: CSVファイル保存先バケット
- `LOG_LEVEL`: ログレベル（INFO/DEBUG/ERROR）

### スケジュール
- デフォルト: 毎日UTC 00:00（JST 09:00）実行
- `template.yaml`の`ScheduledScraping`で変更可能

### タイムアウト・メモリ
- タイムアウト: 300秒（5分）
- メモリ: 1024MB
- 必要に応じて`template.yaml`で調整

## Chrome Lambda Layer

### 使用レイヤー
```
arn:aws:lambda:ap-northeast-1:764866452798:layer:chrome-aws-lambda:31
```

### 自前でレイヤーを作成する場合
```bash
# Chrome/ChromeDriverのダウンロードとパッケージ化
mkdir chrome-layer
cd chrome-layer
# Chromeのダウンロード...
zip -r chrome-layer.zip .
aws lambda publish-layer-version --layer-name chrome --zip-file fileb://chrome-layer.zip
```

## 実行・テスト

### 手動実行
```bash
# API Gateway経由
curl https://[API-ID].execute-api.ap-northeast-1.amazonaws.com/dev/scrape

# Lambda直接実行
aws lambda invoke --function-name ishifuku-scraper-dev response.json

# ローカルテスト
python test_lambda.py
```

### ログ確認
```bash
# CloudWatch Logs
aws logs tail '/aws/lambda/ishifuku-scraper-dev' --follow

# エラーログのみ
aws logs filter-log-events \
    --log-group-name '/aws/lambda/ishifuku-scraper-dev' \
    --filter-pattern 'ERROR'
```

### S3ファイル確認
```bash
# ファイル一覧
aws s3 ls s3://ishifuku-gold-data-dev/ --recursive

# 最新ファイルのダウンロード
aws s3 cp s3://ishifuku-gold-data-dev/gold_prices_$(date +%Y%m%d).csv ./
```

## トラブルシューティング

### よくある問題

1. **Chrome Layer エラー**
   ```
   Error: Chrome binary not found
   ```
   → Chrome Lambda Layerが正しく設定されているか確認

2. **タイムアウトエラー**
   ```
   Task timed out after 300.00 seconds
   ```
   → メモリサイズを増加またはタイムアウト時間を延長

3. **S3アクセスエラー**
   ```
   AccessDenied: Access Denied
   ```
   → IAM権限とバケット名を確認

### デバッグ方法

1. **ローカルテスト**
   ```bash
   python lambda/test_lambda.py
   ```

2. **CloudWatch Insights**
   ```sql
   fields @timestamp, @message
   | filter @message like /ERROR/
   | sort @timestamp desc
   | limit 20
   ```

3. **X-Ray トレーシング**
   ```bash
   # template.yamlに追加
   Tracing: Active
   ```

## コスト最適化

### Lambda料金
- 実行時間: 約30秒/回
- メモリ: 1024MB
- 月間実行回数: 30回（日次）
- 推定月額: $0.20

### S3料金
- ストレージ: 約1MB/月
- 推定月額: $0.01

### 節約のポイント
- 不要なログの削除（14日保持）
- メモリサイズの最適化
- 実行頻度の調整

## セキュリティ

### IAM権限
最小権限の原則に従い、必要な権限のみ付与：
- S3: 指定バケットへの読み書き
- CloudWatch: ログ出力
- VPC: 不要（パブリックサブネット使用）

### 機密情報
- API キーなどは AWS Systems Manager Parameter Store を使用
- 環境変数は暗号化オプションを有効化

## 監視・アラート

### CloudWatch アラーム
- エラー率 > 0%でアラート
- 実行時間 > 4分でアラート
- メモリ使用率 > 90%でアラート

### 通知設定
```bash
# SNSトピック作成
aws sns create-topic --name ishifuku-alerts

# アラームとの連携
aws cloudwatch put-metric-alarm \
    --alarm-name ishifuku-errors \
    --alarm-actions arn:aws:sns:ap-northeast-1:123456789012:ishifuku-alerts
```
