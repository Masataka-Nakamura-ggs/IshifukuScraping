# 石福金属興業 金価格スクレイピングツール

石福金属興業のウェブサイトから金の小売価格を自動取得し、CSVファイルに保存するPythonツールです。ローカル実行とAWS Lambda両方に対応しています。

## 📋 機能

- 石福金属興業のウェブサイトから金の小売価格を自動取得
- 価格データをCSVファイルに保存
- エラーハンドリングとログ記録
- 日時によるログローテーション
- 包括的なテストスイート（19テスト、92%カバレッジ）
- **AWS Lambda対応**（Selenium + Chrome Layer）
- **スケジュール実行**（毎日自動実行）
- **CI/CD パイプライン**（GitHub Actions）

## 🚀 セットアップ

### 1. 仮想環境の作成と有効化

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 📁 プロジェクト構造

```
ishifuku/
├── .github/                        # GitHub Actions
│   └── workflows/
│       ├── ci.yml                  # CI/CDパイプライン
│       └── release.yml             # リリース自動化
├── .venv/                          # Python仮想環境
├── .coverage                       # テストカバレッジデータ
├── .gitignore                      # Git無視ファイル
├── .mypy_cache/                    # MyPy型チェッカーキャッシュ
├── .pytest_cache/                  # pytestキャッシュ
├── docs/                           # ドキュメント
│   └── issue/20250821/
├── lambda/                         # AWS Lambda関連
│   ├── lambda_scrape_ishifuku.py   # Lambda関数メイン
│   ├── serverless.yml             # Serverless Framework設定
│   ├── template.yaml              # AWS SAM設定
│   ├── deploy.sh                  # Serverless用デプロイスクリプト
│   ├── sam_deploy.sh              # SAM用デプロイスクリプト
│   ├── test_lambda.py             # Lambda基本テスト
│   ├── test_lambda_improved.py    # Lambda改良版テスト
│   ├── requirements.txt           # Lambda用依存関係
│   └── README.md                  # Lambda詳細ガイド
├── logs/                           # ログファイル
│   ├── scraping_error_YYYYMMDD.log # エラーログ
│   └── scraping_info_YYYYMMDD.log  # 実行ログ
├── result/                         # CSVファイル
│   └── ishihuku-gold-YYYYMMDD.csv  # 価格データ
├── tests/                          # テストファイル
│   ├── __init__.py
│   ├── test_scrape_ishifuku.py     # 基本機能テスト
│   └── test_scraping_functions.py  # スクレイピング機能テスト
├── CHANGELOG.md                    # 変更履歴
├── LICENSE                         # ライセンス
├── pyproject.toml                  # プロジェクト設定
├── requirements.txt                # 依存ライブラリ
├── pytest.ini                     # pytest設定
├── scrape_ishifuku.py             # メインスクリプト（ローカル実行用）
└── README.md                      # このファイル
```

## 🔧 使用方法

### ローカル実行

```bash
# 通常の実行
python scrape_ishifuku.py

# または仮想環境を確実にアクティベートして実行
source .venv/bin/activate && python scrape_ishifuku.py
```

### AWS Lambda実行

#### デプロイ方法

**AWS SAM（推奨）:**
```bash
cd lambda
./sam_deploy.sh dev ishifuku-gold-data
```

**Serverless Framework:**
```bash
cd lambda
./deploy.sh dev
```

#### 手動実行
```bash
# API Gateway経由
curl https://[API-ID].execute-api.ap-northeast-1.amazonaws.com/dev/scrape

# Lambda直接実行
aws lambda invoke --function-name ishifuku-scraper-dev response.json

# ローカルテスト
cd lambda
python test_lambda_improved.py
```

#### ログ確認
```bash
# CloudWatch Logs
aws logs tail '/aws/lambda/ishifuku-scraper-dev' --follow

# S3ファイル確認
aws s3 ls s3://ishifuku-gold-data-dev/ --recursive
```

### 出力例

```
石福金属興業から金の価格を取得します...
石福金属興業のトップページにアクセス中...
価格ページにアクセス中: https://retail.ishifuku-kinzoku.co.jp/price/
金の小売価格を取得しました: 17530円/g
取得元テキスト: 17,530(+117)
データをCSVファイルに保存しました: result/ishihuku-gold-20250821.csv
処理が正常に完了しました。
取得日時: 2025-08-21 15:30:45
金の小売価格: 17530円/g
保存ファイル: ishihuku-gold-20250821.csv
```

### CSVファイル形式

**ローカル実行の場合:**
```csv
2025-08-21,17530,2025-08-21 15:30:45
```

**Lambda実行の場合（S3保存）:**
```csv
2025-08-21,"{'gold_price': 17530, 'datetime': '2025-08-21 15:30:00', 'source_url': 'https://retail.ishifuku-kinzoku.co.jp/price/'}",2025-08-21 11:45:36
```

| フィールド | 説明 | 例 |
|-----------|------|-----|
| 日付 | 取得日 (YYYY-MM-DD) | 2025-08-21 |
| 金価格/データ | 金の小売価格またはJSON形式のデータ | 17530 または詳細データ |
| 取得日時 | 取得日時 (YYYY-MM-DD HH:MM:SS) | 2025-08-21 15:30:45 |

## 🧪 テスト

### ローカルテストの実行

全てのテストを実行：
```bash
pytest tests/ -v
```

カバレッジレポート付きでテストを実行：
```bash
pytest tests/ --cov=scrape_ishifuku --cov-report=term-missing
```

特定のテストクラスのみ実行：
```bash
pytest tests/test_scrape_ishifuku.py::TestExtractPriceFromText -v
```

### Lambda テストの実行

```bash
cd lambda

# 基本テスト
python test_lambda.py

# 改良版テスト（モック + 実スクレイピング）
python test_lambda_improved.py
```

### テスト構成

#### `test_scrape_ishifuku.py`
- `TestGetCurrentDatetime`: 日時取得機能のテスト
- `TestExtractPriceFromText`: 価格抽出機能のテスト
- `TestCreateEmptyCSV`: 空CSVファイル作成のテスト
- `TestSaveToCSV`: CSV保存機能のテスト
- `TestSetupLogging`: ログ設定のテスト
- `TestIntegration`: 統合テスト

#### `test_scraping_functions.py`
- `TestScrapeGoldPrice`: Seleniumスクレイピング機能のテスト
- `TestSeleniumIntegration`: main関数の統合テスト

### テスト結果

**ローカルテスト:**
```
========================== 19 passed in 24.34s ==========================
Coverage: 92%
```

**Lambda テスト:**
```
📊 テスト結果サマリー:
価格抽出テスト: ✅ PASS
Lambda モックテスト: ✅ PASS  
ローカル実スクレイピング: ✅ PASS
```

## 📊 ログ機能

### ログファイル

- **エラーログ**: `logs/scraping_error_YYYYMMDD.log`
- **実行ログ**: `logs/scraping_info_YYYYMMDD.log`

### ログローテーション

ログファイルは日付ごとに自動的にローテーションされます。

### ログレベル

- **ERROR**: エラー情報
- **INFO**: 実行状況、成功ログ

## ⚙️ 設定

### ローカル環境

#### Chrome WebDriver

Seleniumは自動的にChromeDriverをダウンロード・管理します。Chromeブラウザがインストールされている必要があります。

#### タイムアウト設定

- ページ読み込みタイムアウト: 30秒
- WebDriverWait: 10秒
- 追加待機時間: 5秒 + 3秒

### AWS Lambda環境

#### 環境変数
- `S3_BUCKET`: CSVファイル保存先バケット
- `LOG_LEVEL`: ログレベル（INFO/DEBUG/ERROR）

#### Chrome Lambda Layer
```
arn:aws:lambda:ap-northeast-1:764866452798:layer:chrome-aws-lambda:31
```

#### スケジュール実行
- デフォルト: 毎日UTC 00:00（JST 09:00）実行
- `template.yaml`の`ScheduledScraping`で変更可能

#### リソース設定
- タイムアウト: 300秒（5分）
- メモリ: 1024MB
- 必要に応じて調整可能

## 🔍 エラーハンドリング

スクリプトは以下のエラーを適切に処理します：

1. **ネットワークエラー**: サイトに接続できない場合
2. **HTML構造変更**: 価格情報が見つからない場合
3. **ファイルI/Oエラー**: CSV保存時のエラー

エラー発生時は：
- 詳細なエラー情報をログに記録
- 空のCSVファイルを作成
- 正常終了（終了コード0）

## 🛠️ 開発

### CI/CD パイプライン

GitHub Actionsによる自動化：

- **CI パイプライン** (`.github/workflows/ci.yml`):
  - Python 3.9, 3.10, 3.11, 3.12 での自動テスト
  - コードカバレッジ測定
  - プルリクエスト時の自動実行

- **リリース パイプライン** (`.github/workflows/release.yml`):
  - タグプッシュ時の自動リリース
  - 変更履歴の自動生成

### プロジェクト設定

`pyproject.toml`によるモダンなPythonプロジェクト管理：
- パッケージメタデータ
- 依存関係管理
- ツール設定統合

### 新しいテストの追加

1. `tests/` ディレクトリにテストファイルを作成
2. ファイル名は `test_*.py` の形式
3. テスト関数は `test_*` で開始

### モック使用例

```python
@patch('scrape_ishifuku.webdriver.Chrome')
def test_scraping_function(self, mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    # テストロジック
```

## � デプロイメント

### AWS Lambda デプロイ

詳細なデプロイガイドは [`lambda/README.md`](lambda/README.md) を参照してください。

#### 前提条件
- AWS CLI v2
- AWS SAM CLI または Serverless Framework
- Python 3.9+
- Docker（オプション: SAMでのローカルテスト時のみ）

> **Dockerについて**: このプロジェクトはPure Pythonライブラリのみを使用するため、基本的にDockerは不要です。DockerはAWS SAMでローカル環境でのLambdaテスト（`sam local start-api`など）を行う場合のみ必要になります。通常のデプロイメントでは不要です。

#### クイックスタート
```bash
# AWS SAM
cd lambda && ./sam_deploy.sh dev

# Serverless Framework
cd lambda && ./deploy.sh dev
```

#### 監視・アラート
- CloudWatch によるログ監視
- エラー率・実行時間のアラート
- S3 への自動バックアップ

### コスト最適化
- **Lambda料金**: 約$0.20/月（日次実行）
- **S3料金**: 約$0.01/月
- **最適化ポイント**: ログ保持期間、メモリサイズ調整

## �📝 ライセンス

MIT License - 詳細は [`LICENSE`](LICENSE) を参照してください。

## 🤝 貢献

バグ報告や機能要求は、[GitHub Issues](https://github.com/Masataka-Nakamura-ggs/IshifukuScraping/issues) で報告してください。

### 貢献の流れ
1. プロジェクトをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### 開発環境セットアップ
```bash
git clone https://github.com/Masataka-Nakamura-ggs/IshifukuScraping.git
cd IshifukuScraping
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

### 開発ツール
- **pytest**: テストフレームワーク
- **coverage**: コードカバレッジ測定
- **mypy**: 静的型チェック（オプション）
- **CI/CD**: GitHub Actions自動化

## ⚠️ 注意事項

- ウェブスクレイピングは対象サイトの利用規約を遵守してください
- 過度なアクセスはサーバーに負荷をかける可能性があります
- 価格データは参考情報として使用してください
- AWS Lambda使用時はAWSの利用料金が発生します

## 📊 技術スタック

### フロントエンド
- **Selenium WebDriver**: ブラウザ自動化
- **BeautifulSoup4**: HTML解析
- **Chrome/ChromeDriver**: ヘッドレスブラウザ

### バックエンド
- **Python 3.9+**: メイン言語
- **pytest**: テストフレームワーク
- **coverage.py**: コードカバレッジ測定
- **boto3**: AWS SDK

### インフラ
- **AWS Lambda**: サーバーレス実行環境
- **Amazon S3**: ファイルストレージ
- **CloudWatch**: ログ・監視
- **API Gateway**: HTTP API

### DevOps
- **GitHub Actions**: CI/CD
- **AWS SAM**: インフラ構築
- **Serverless Framework**: デプロイメント

## 📈 ロードマップ

- [ ] 複数金属対応（銀、プラチナ等）
- [ ] リアルタイム価格変動通知
- [ ] データ可視化ダッシュボード
- [ ] 価格予測機能（機械学習）
- [ ] REST API の提供
