# Lambda デプロイメントガイド

## 概要
石福金属興業の金価格スクレイピングをAWS Lambdaで実行するためのデプロイメント手順です。

重要: 現在の推奨Lambdaハンドラーは `src/main_lambda.py` の `lambda_handler` です。
従来の Selenium + Chrome Layer 方式はレガシー扱いになりました（必要時のみ使用）。

## ファイル構成

```
lambda/
├── README.md                              # このファイル
├── requirements.txt                       # Lambda用依存関係
├── template.yaml                          # AWS SAM設定
├── serverless.yml                         # Serverless Framework設定
├── deploy.sh                              # Serverless用デプロイスクリプト
├── sam_deploy.sh                          # SAM用デプロイスクリプト
└── __pycache__/                           # Pythonキャッシュ
src/
└── main_lambda.py                         # Lambdaハンドラー本体（`handler: main_lambda.lambda_handler`）
```

## 前提条件

### 必要なツール
- AWS CLI v2
- AWS SAM CLI
- Docker（オプション: SAMローカルテスト用のみ）
- Python 3.9+

> 注意: 推奨構成（`src/main_lambda.py`）はプロジェクト内のモジュールとS3を利用します。Selenium/Chrome Layerは不要です。DockerはSAMのローカル実行時のみ必要です。

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

Handler 設定例（template.yaml の該当関数）:

```
Handler: src/main_lambda.lambda_handler
Runtime: python3.12
MemorySize: 512
Timeout: 60
Environment:
   Variables:
      S3_BUCKET: your-bucket-name
```

```bash
cd lambda
./sam_deploy.sh dev ishifuku-gold-data
```

### 2. Serverless Frameworkを使用

`serverless.yml` の関数設定例:

```
functions:
   scraper:
      handler: src/main_lambda.lambda_handler
      runtime: python3.12
      memorySize: 512
      timeout: 60
      environment:
         S3_BUCKET: ${env:S3_BUCKET}
```

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

## Chrome Lambda Layer（LEGACY）

レガシー構成（`lambda/lambda_scrape_ishifuku_legacy.py`）で Selenium/Chrome を使う場合のみ必要です。

使用例レイヤー ARN:
```
arn:aws:lambda:ap-northeast-1:764866452798:layer:chrome-aws-lambda:31
```

自前でレイヤーを作成する場合（参考）:
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
# API Gateway経由（SAM）
curl https://[API-ID].execute-api.ap-northeast-1.amazonaws.com/dev/scrape

# Lambda直接実行（推奨ハンドラー）
aws lambda invoke --function-name ishifuku-scraper-dev response.json

# ローカルテスト（推奨構成: `src/main_lambda.py`）
python -c 'from src.main_lambda import lambda_handler; print(lambda_handler({}, None))'

# legacyテスト（必要時のみ）
python lambda/test_lambda.py
python lambda/test_lambda_improved.py
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

1. **Chrome Layer エラー（legacy）**
   ```
   Error: Chrome binary not found
   ```
   → legacy 構成を使っている場合のみ該当。推奨構成では不要。

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
   # 推奨: 直接ハンドラーを呼び出し
   python -c 'from src.main_lambda import lambda_handler; print(lambda_handler({}, None))'
   
   # legacy 構成を試す場合
   python lambda/test_lambda.py
   python lambda/test_lambda_improved.py
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
