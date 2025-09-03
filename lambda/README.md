# 金価格スクレイピング Lambda - デプロイメントガイド

## 概要
石福金属興業の金価格をスクレイピングするAWS Lambda関数を、AWS SAM (Serverless Application Model) を用いてデプロイするための手順書です。
このシステムは、SeleniumとヘッドレスChromeを使用してウェブサイトから価格情報を取得し、結果をS3バケットにCSV形式で保存します。実行はAPI Gateway経由での手動トリガー、またはEventBridgeによる定時実行が可能です。

## アーキテクチャ
1. トリガー:
    - API Gateway: 手動で即時実行するためのHTTP GETエンドポイントを提供します。
    - Amazon EventBridge: cron式に基づき、毎日定時にLambda関数を自動実行します。
1. 実行:
    - AWS Lambda: PythonランタイムでSeleniumを実行し、スクレイピング処理を行います。ChromeブラウザはLambda Layerを通じて提供されます。
1. ストレージ:
    - Amazon S3: スクレイピング結果のCSVファイルが保存されます。
1. 監視と通知:
    - Amazon CloudWatch: Lambda関数のログを収集し、エラー発生を監視します。
    - Amazon EventBridge / SNS: S3へのファイル保存成功をトリガーに、SNSトピックへ通知を発行します。

## ファイル構成

```
lambda/
├── README.md                 # このファイル
├── requirements.txt          # Lambda用依存関係
├── template.yaml             # AWS SAM設定
└── sam_deploy.sh             # SAM用デプロイスクリプト
src/
   ├── ishifuku/             # メインのソースコードパッケージ
   │   ├── __init__.py
   │   ├── config.py         # 設定管理
   │   ├── core.py           # スクレイピングのコアロジック
   │   ├── optimized_core.py # キャッシュ機能付きのコアロジック (オプション)
   │   ├── scraping/         # WebDriver, Parser, Extractorなど
   │   ├── storage/          # S3/CSVへの保存ロジック
   │   └── utils/            # 日時処理、ロギングなど
   └── main_lambda.py        # Lambda関数のエントリーポイント
```

## 前提条件

### 必要なツール
- AWS CLI v2
- AWS SAM CLI
- Docker（オプション: SAMローカルテスト用のみ）
- Python 3.9+

### インストール手順
```bash
# AWS CLI
brew install awscli

# AWS SAM CLI
brew tap aws/tap
brew install aws-sam-cli

# AWS認証設定
aws configure
```

## デプロイメント方法
`lambda`ディレクトリに移動し、デプロイスクリプトを実行します。
```
cd lambda
./sam_deploy.sh [環境名] [S3バケットのベース名]
```
#### 実行例
```bash
cd lambda
./sam_deploy.sh dev ishifuku-gold-data
```
#### 引数
1. `[環境名]` (省略可, デフォルト: ishifuku-gold-data)
    - デプロイ環境 (dev, staging, prodなど) を指定します。リソース名の一部として使用されます。
1. `[S3バケットのベース名]` (必須ではない、デフォルト: `ishifuku-gold-data`)
    - データを保存するS3バケットの基本名を指定します。
    - 【重要】S3バケット名は全世界で一意である必要があるため、自分だけのユニークな名前を指定してください。 (例: my-gold-data-20250903)

## 設定項目
設定は主にtemplate.yamlとsrc/ishifuku/config.pyで管理されています。
### 環境変数 (template.yamlで定義)
- `S3_BUCKET_NAME`: CSVファイルの保存先S3バケット名。スクリプトにより動的に設定されます。
- `LOG_LEVEL`: ログレベル（INFO/DEBUG/ERROR）

### スケジュール (template.yamlで定義)
- デフォルト: 毎日UTC 00:00（JST 09:00）実行
- `template.yaml`の`ScheduledScraping`で変更可能

### タイムアウト・メモリ(template.yamlで定義)
- タイムアウト: 300秒（5分）
- メモリ: 1024MB

### Chrome Lambda Layer (template.yamlで定義)
- このプロジェクトはスクレイピングにSeleniumとChromeを使用するため、Chrome Lambda Layerが必須です。
- template.yamlのChromeLayerArnパラメータで、デプロイするリージョンに合ったレイヤーのARNを指定してください。

## 実行・テスト
デプロイ完了後、sam_deploy.shの出力に表示されるURLやARNを使用してテストできます。
### 手動実行
```bash
# デプロイ完了時に表示されるApiUrlにリクエストを送る
curl [表示されたApiUrl]
```
```bash
# API Gateway経由
curl https://[API-ID].execute-api.ap-northeast-1.amazonaws.com/dev/scrape

# Lambda直接実行（推奨ハンドラー）
aws lambda invoke --function-name ishifuku-scraper-dev response.json
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

このプロジェクトはtemplate.yamlによって、監視と通知の仕組みが自動で構築されます。

1. 成功通知 (S3 -> EventBridge -> SNS)
    - 仕組み: S3バケットへのファイル保存が成功すると、そのイベントがAmazon EventBridgeに送信され、SNSトピックを通じて通知が発行されます。
    - 設定: デプロイ後、AWSコンソールでishifuku-scraper-success-notifications-devというSNSトピックに自分のEメールアドレスを**サブスクライブ（購読登録）**してください。

2. エラー監視 (CloudWatch Alarm)
    - 仕組み: Lambda関数でエラーが発生すると、CloudWatch Alarmが発動します。
    - 設定: template.yamlでScrapingErrorAlarmが定義されています。このアラームに通知先を設定するには、AlarmActionsプロパティを追加し、通知用のSNSトピック（別途作成）のARNを指定します。
```
