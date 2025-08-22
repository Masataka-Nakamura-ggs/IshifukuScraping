# 石福金属興業 金価格スクレイピングツール v2.0

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-160%2B%20passed-green.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg)](htt- 📖 [アーキテクチャ仕様書](docs/ARCHITECTURE_v2.md)
- 🧪 [テスト仕様書](tests/)
- 🐛 [Issues](https://github.com/Masataka-Nakamura-ggs/IshifukuScraping/issues)
- 💬 [Discussions](https://github.com/Masataka-Nakamura-ggs/IshifukuScraping/discussions)github.com/psf/black)
[![Type Check](https://img.shields.io/badge/type%20check-mypy-blue.svg)](http://mypy-lang.org/)

石福金属興業のウェブサイトから金の小売価格を自動取得し、CSVファイルに保存するPythonツールです。**v2.0では完全リファクタリングを実施し、保守性・拡張性・テスト容易性・パフォーマンス監視を大幅に改善しました。**

## 📋 主要機能

- 🏅 **金価格自動取得**: 石福金属興業サイトからの価格スクレイピング
- 💾 **データ保存**: CSV/S3への自動保存
- 🧪 **高品質テスト**: 84%カバレッジ、160+テストケース
- ☁️ **AWS Lambda対応**: サーバーレス実行環境
- 📊 **パフォーマンス監視**: 実行時間・メモリ使用量追跡
- 🔔 **監視・アラート**: 自動エラー通知機能
- 🚀 **CI/CDパイプライン**: GitHub Actions による自動化
- 📈 **スケジュール実行**: 定期的な価格取得

## 🎯 v2.0の主要改善点

### ✨ アーキテクチャの刷新
- **モジュール分離**: 347行の単一ファイルを機能別に分割
- **設定管理統一**: ハードコードされた値を設定ファイルに集約
- **依存性注入**: テスト容易性の向上とモック化対応
- **型安全性**: 完全な型アノテーション
- **ファクトリパターン**: 環境別の最適化されたインスタンス生成

### 📈 品質指標の向上
- **コード行数**: メインファイル 347行 → 各モジュール平均80行
- **テストカバレッジ**: 84%（160+テストケース）
- **実行時間**: パフォーマンス維持（12-18秒）
- **コード品質**: PEP 8準拠、mypy完全対応

### 🚀 CI/CD パイプライン
- **GitHub Actions**: 自動化されたテスト・ビルド・デプロイ
- **複数Python版対応**: 3.9-3.13での動作保証
- **品質ゲート**: カバレッジ80%以上の強制
- **セキュリティスキャン**: Bandit・Safety統合

### 📊 パフォーマンス監視
- **実行時間測定**: 詳細な性能プロファイリング
- **メモリ使用量追跡**: リソース効率の最適化
- **WebDriver性能**: ページロード・要素検索の計測
- **キャッシュ機能**: 重複アクセスの削減

## 🏛️ アーキテクチャ構成

```
ishifuku/
├── src/
│   ├── ishifuku/                  # 📦 メインライブラリ
│   │   ├── config.py             # ⚙️  統一設定管理
│   │   ├── core.py               # 🎯 メインスクレイピング処理
│   │   ├── optimized_core.py     # 🚀 パフォーマンス最適化版
│   │   ├── scraping/             # 🕷️  スクレイピング機能
│   │   │   ├── driver.py         #   WebDriver管理
│   │   │   ├── parser.py         #   HTML解析
│   │   │   └── extractor.py      #   価格抽出
│   │   ├── storage/              # 💾 データ保存
│   │   │   ├── csv_handler.py    #   CSV操作
│   │   │   └── s3_handler.py     #   S3操作（Lambda用）
│   │   └── utils/                # 🛠️  ユーティリティ
│   │       ├── datetime_utils.py #   日時処理
│   │       └── logging_utils.py  #   ログ管理
│   ├── main_local.py             # 🖥️  ローカル実行用
│   └── main_lambda.py            # ☁️  Lambda実行用
├── tests/                       # 🧪 テストスイート（160+テスト）
├── docs/                        # 📚 ドキュメント
│   ├── ARCHITECTURE_v2.md       #   アーキテクチャ仕様書
│   └── issue/                   #   設計文書
├── .github/                     # GitHub Actions
│   └── workflows/
│       ├── ci.yml              # CI/CDパイプライン
│       └── release.yml         # リリース自動化
├── result/                      # 出力データ
├── logs/                        # ログファイル
└── [設定ファイル群]              # pyproject.toml, pytest.ini等
```

## 🚀 クイックスタート

### 1. 環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/Masataka-Nakamura-ggs/IshifukuScraping.git
cd IshifukuScraping

# 仮想環境作成・有効化
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 依存関係インストール
pip install -r requirements.txt
```

### 2. ローカル実行

```bash
# 基本実行
python src/main_local.py

# パフォーマンス最適化版
python src/main_local.py --optimized

# ログレベル指定
python src/main_local.py --log-level DEBUG
```

### 3. 実行結果

```
result/ishihuku-gold-YYYYMMDD.csv  # 価格データ
logs/ishifuku_YYYYMMDD.log        # 実行ログ
```

## 🧪 テスト実行

### 全テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=src --cov-report=html

# 特定テストのみ
pytest tests/test_core.py -v

# パフォーマンステスト
pytest tests/test_performance.py -v
```

### コード品質チェック

```bash
# フォーマット
black src/ tests/

# インポート整理
isort src/ tests/

# 構文チェック
flake8 src/ tests/

# 型チェック
mypy src/
```

## ☁️ AWS Lambda デプロイ

### 1. 環境準備

```bash
# AWS CLI設定
aws configure

# Serverless Framework インストール
npm install -g serverless
npm install -g serverless-python-requirements
```

### 2. デプロイ

```bash
cd lambda/

# 開発環境デプロイ
serverless deploy --stage dev

# 本番環境デプロイ
serverless deploy --stage prod
```

### 3. 手動実行

```bash
# Lambda関数実行
serverless invoke --function scrape_ishifuku --stage dev
```

## 📊 監視・アラート

### CloudWatch メトリクス

- 実行時間・成功率
- エラー発生数・種別
- メモリ使用量
- レスポンス時間

### アラート設定

```yaml
# cloudwatch-alarms.yml例
ScrapeFailureAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: IshifukuScrapeFailure
    MetricName: Errors
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
```

## 🔧 設定オプション

### 環境変数

```bash
# 基本設定
ISHIFUKU_URL=https://ishifuku.co.jp/kinprice/
ISHIFUKU_TIMEOUT=30
ISHIFUKU_RETRY_COUNT=3

# AWS設定（Lambda用）
AWS_S3_BUCKET=ishifuku-data
AWS_S3_PREFIX=gold-prices/

# 監視設定
ENABLE_MONITORING=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### config.py カスタマイズ

```python
# src/ishifuku/config.py
class Config:
    # スクレイピング設定
    URL = "https://ishifuku.co.jp/kinprice/"
    TIMEOUT = 30
    RETRY_COUNT = 3
    
    # パフォーマンス設定
    ENABLE_CACHE = True
    CACHE_TTL = 3600
    
    # 監視設定
    ENABLE_METRICS = True
    METRICS_INTERVAL = 60
```

## 📈 パフォーマンス

### ベンチマーク結果

```
基本版:
- 平均実行時間: 15.3秒
- メモリ使用量: 145MB
- CPU使用率: 23%

最適化版:
- 平均実行時間: 12.1秒 (21%改善)
- メモリ使用量: 132MB (9%改善)
- CPU使用率: 19% (17%改善)
```

### パフォーマンスチューニング

1. **WebDriverオプション最適化**
2. **不要なリソース読み込み無効化**
3. **要素検索の最適化**
4. **メモリ使用量の削減**

## 🔒 セキュリティ

### セキュリティスキャン

```bash
# 脆弱性スキャン
bandit -r src/

# 依存関係チェック
safety check

# シークレットスキャン
detect-secrets scan
```

### セキュリティ対策

- 依存関係の定期更新
- シークレット情報の環境変数化
- AWS IAM最小権限の原則
- VPC内での実行（本番環境）

## 🛠️ 開発・貢献

### 開発環境セットアップ

```bash
# 開発依存関係インストール
pip install -r requirements-dev.txt

# pre-commit フック設定
pre-commit install

# 開発モード実行
python -m src.main_local --dev
```

### プルリクエスト手順

1. **Issue作成**: 修正・機能追加の内容を説明
2. **ブランチ作成**: `feature/issue-123-description`
3. **実装**: テスト込みで実装
4. **テスト実行**: 全テストパス確認
5. **プルリクエスト**: 詳細な説明付きで作成
6. **レビュー**: コードレビュー対応
7. **マージ**: CI/CD パス後にマージ

### 開発ガイドライン

- 新機能には必ずテストを作成
- 型アノテーションを完全に記述
- Google Style docstringを使用
- `black`, `flake8`, `mypy` を通過させる
- カバレッジ80%以上を維持

## 📚 技術スタック

### コア技術
- **Python 3.9+**: メイン言語
- **Selenium**: ブラウザ自動化
- **BeautifulSoup**: HTML解析
- **pandas**: データ処理

### テスト・品質
- **pytest**: テストフレームワーク
- **coverage.py**: コードカバレッジ測定
- **mypy**: 静的型チェック
- **black/flake8**: コードフォーマット

### インフラ・DevOps
- **AWS Lambda**: サーバーレス実行環境
- **Amazon S3**: ファイルストレージ
- **CloudWatch**: ログ・監視
- **GitHub Actions**: CI/CD
- **Serverless Framework**: デプロイメント

## 📈 ロードマップ

### Phase 1: 基盤機能強化 (完了)
- ✅ アーキテクチャリファクタリング
- ✅ テストカバレッジ84%達成
- ✅ CI/CDパイプライン構築
- ✅ パフォーマンス監視実装

### Phase 2: 機能拡張
- [ ] 複数金属対応（銀、プラチナ等）
- [ ] リアルタイム価格変動通知
- [ ] データ可視化ダッシュボード
- [ ] 価格予測機能（機械学習）

### Phase 3: スケーラビリティ
- [ ] 分散処理対応
- [ ] リアルタイムWebSocket API
- [ ] マルチテナント機能
- [ ] 高可用性構成

### Phase 4: 企業対応
- [ ] RBAC（ロールベースアクセス制御）
- [ ] 監査ログ機能
- [ ] SLA保証
- [ ] 24/7監視体制

## 🔗 関連リンク

- 📖 [アーキテクチャ仕様書](docs/ARCHITECTURE_v2.md)
- 🧪 [テスト仕様書](tests/)
- 🐛 [Issues](https://github.com/Masataka-Nakamura-ggs/IshifukuScraping/issues)
- 💬 [Discussions](https://github.com/Masataka-Nakamura-ggs/IshifukuScraping/discussions)

## 📞 サポート

問題や質問がある場合：

1. [Issues](https://github.com/Masataka-Nakamura-ggs/IshifukuScraping/issues) で報告
2. [Discussions](https://github.com/Masataka-Nakamura-ggs/IshifukuScraping/discussions) で質問
3. ログファイルを添付して詳細を提供

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) を参照してください。

---

**Ishifuku Gold Price Scraper v2.0** - Professional Web Scraping Solution with Monitoring & CI/CD  
**v2.0リリース** - 2025年8月22日 🎉  
リファクタリングにより、保守性・拡張性・品質が大幅に向上しました！
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

AWS Lambda環境では、`src/main_lambda.py`を使用してサーバーレス実行が可能です。

#### 前提条件
- AWS CLI v2
- Python 3.9+
- boto3 ライブラリ

#### 基本的なデプロイ手順
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
