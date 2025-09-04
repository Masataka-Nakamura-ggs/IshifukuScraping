# 石福金属興業 金価格スクレイピングツール v2.0

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen.svg)](tests/)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)
[![Type Check: mypy](https://img.shields.io/badge/type%20check-mypy-blue.svg)](http://mypy-lang.org/)

石福金属興業のウェブサイトから金の小売価格を自動取得し、CSVファイルに保存するPythonツールです。

## 📋 主要機能

- 🏅 **金価格自動取得**: 石福金属興業サイトからの価格スクレイピング
- 💾 **データ保存**: CSV/S3への自動保存
- ☁️ **AWS Lambda対応**: サーバーレス実行環境（**AWS環境では動作未確認**）
- 👀 **基本的な監視**: 実行時間・エラー記録
- 🚀 **CI/CDパイプライン**: GitHub Actions による自動化

## 🏛️ アーキテクチャ構成

```
ishifuku/
├── src/
│   ├── ishifuku/                 # 📦 メインライブラリ
│   │   ├── config.py             # ⚙️  統一設定管理
│   │   ├── core.py               # 🎯 メインスクレイピング処理
│   │   ├── optimized_core.py     # 🚀 パフォーマンス最適化版
│   │   ├── scraping/             # 🕷️ スクレイピング機能
│   │   │   ├── driver.py         #    WebDriver管理
│   │   │   ├── parser.py         #    HTML解析
│   │   │   └── extractor.py      #    価格抽出
│   │   ├── storage/              # 💾 データ保存
│   │   │   ├── csv_handler.py    #    CSV操作
│   │   │   └── s3_handler.py     #    S3操作（Lambda用）
│   │   └── utils/                # 🛠️ ユーティリティ
│   │       ├── datetime_utils.py #    日時処理
│   │       └── logging_utils.py  #    ログ管理
│   ├── main_local.py             # 🖥️ ローカル実行用
│   └── main_lambda.py            # ☁️ Lambda実行用
├── tests/                        # 🧪 テストスイート（160+テスト）
├── docs/                         # 📚 ドキュメント
│   ├── ARCHITECTURE_v2.md        #    アーキテクチャ仕様書
│   └── issue/                    #    設計文書
├── .github/                      #    GitHub Actions
│   └── workflows/
│       ├── ci.yml                # CI/CDパイプライン
│       └── release.yml           # リリース自動化
├── result/                       # 出力データ
├── logs/                         # ログファイル
└── [設定ファイル群]                # pyproject.toml, pytest.ini等
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
logs/ishifuku_YYYYMMDD.log         # 実行ログ
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
```

### コード品質チェック

```bash
# フォーマットチェック
black --check src/ tests/

# フォーマット適用
black src/ tests/

# インポート整理
isort src/ tests/

# 構文チェック
flake8 src/ tests/

# 型チェック
mypy src/
```

## ☁️ AWS Lambda デプロイ

**注意**: 現在Lambda用のServerless Framework設定は準備段階です。

### Lambda実行用ファイル

```bash
# Lambda用のメインファイルが用意されています
src/main_lambda.py  # Lambda実行用エントリーポイント
```

### パッケージング

```bash
# 必要な依存関係をパッケージに含める
pip install -t lambda_package/ -r requirements.txt
cp -r src/ lambda_package/
```

## 📊 基本的な監視機能

### 実行ログ

- 実行結果の記録（成功/失敗）
- エラー詳細の記録
- 実行時間の記録
- 取得した価格データの記録

### ログファイル

```bash
logs/ishifuku_YYYYMMDD.log  # 日次実行ログ
result/ishihuku-gold-YYYYMMDD.csv  # 価格データ
```

**注意**: CloudWatchアラートやSlack通知などの高度な監視機能は現在未実装です。

## 🔧 設定オプション

### 基本設定

設定は `src/ishifuku/config.py` で管理されています。

```python
# 主要な設定項目
class ScrapingConfig:
    base_url = "https://www.ishifukushop.com/"
    price_url = "https://retail.ishifuku-kinzoku.co.jp/price/"
    page_load_timeout = 30
    max_retries = 3
    min_valid_price = 10000  # 円/g
    max_valid_price = 30000  # 円/g
```

### 出力設定

```python
class StorageConfig:
    output_dir = "result"
    csv_filename_template = "ishihuku-gold-{date}.csv"
    log_dir = "logs"
```

## 📈 パフォーマンス

現在は基本的な実行時間の記録のみ実装されています。

- **実行時間**: 12-18秒（ネットワーク状況による）
- **メモリ使用量**: 約50MB（Chrome WebDriverを含む）
- **CPU使用率**: 15-20%（WebDriver起動時）

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
- **標準CSVライブラリ**: データ処理

### テスト・品質
- **pytest**: テストフレームワーク
- **coverage.py**: コードカバレッジ測定
- **mypy**: 静的型チェック
- **black/flake8**: コードフォーマット

### インフラ・DevOps
- **AWS Lambda**: サーバーレス実行環境
- **Amazon S3**: ファイルストレージ
- **GitHub Actions**: CI/CD
