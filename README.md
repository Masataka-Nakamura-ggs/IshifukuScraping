# 石福金属興業 金価格スクレイピングツール

石福金属興業のウェブサイトから金の小売価格を自動取得し、CSVファイルに保存するPythonスクリプトです。

## 📋 機能

- 石福金属興業のウェブサイトから金の小売価格を自動取得
- 価格データをCSVファイルに保存
- エラーハンドリングとログ記録
- 日時によるログローテーション
- 包括的なテストスイート

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
├── .venv/                          # Python仮想環境
├── docs/                           # ドキュメント
│   └── issue/20250821/
├── logs/                           # ログファイル
│   ├── scraping_error_YYYYMMDD.log # エラーログ
│   └── scraping_info_YYYYMMDD.log  # 実行ログ
├── result/                         # CSVファイル
│   └── ishihuku-gold-YYYYMMDD.csv  # 価格データ
├── tests/                          # テストファイル
│   ├── __init__.py
│   ├── test_scrape_ishifuku.py     # 基本機能テスト
│   └── test_scraping_functions.py  # スクレイピング機能テスト
├── requirements.txt                # 依存ライブラリ
├── pytest.ini                     # pytest設定
├── scrape_ishifuku.py             # メインスクリプト
└── README.md                      # このファイル
```

## 🔧 使用方法

### スクレイピングの実行

```bash
python scrape_ishifuku.py
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

```csv
2025-08-21,17530,2025-08-21 15:30:45
```

| フィールド | 説明 | 例 |
|-----------|------|-----|
| 日付 | 取得日 (YYYY-MM-DD) | 2025-08-21 |
| 金価格 | 金の小売価格 (円/g) | 17530 |
| 取得日時 | 取得日時 (YYYY-MM-DD HH:MM:SS) | 2025-08-21 15:30:45 |

## 🧪 テスト

### テストの実行

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

```
========================== 19 passed in 24.34s ==========================
Coverage: 92%
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

### Chrome WebDriver

Seleniumは自動的にChromeDriverをダウンロード・管理します。Chromeブラウザがインストールされている必要があります。

### タイムアウト設定

- ページ読み込みタイムアウト: 30秒
- WebDriverWait: 10秒
- 追加待機時間: 5秒 + 3秒

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

## 📝 ライセンス

このプロジェクトは内部使用を目的としています。

## 🤝 貢献

バグ報告や機能要求は、プロジェクトの課題として報告してください。

## ⚠️ 注意事項

- ウェブスクレイピングは対象サイトの利用規約を遵守してください
- 過度なアクセスはサーバーに負荷をかける可能性があります
- 価格データは参考情報として使用してください
