# Ishifuku Gold Price Scraper v2 - 完全版ガイド

## 📋 プロジェクト概要

石福金属からの金価格スクレイピングツールの完全リファクタリング版です。高いテストカバレッジ（84%）、CI/CD統合、パフォーマンス監視、アラート機能を備えた本格的なアプリケーションとして生まれ変わりました。

## ✨ 主要な改善点

### 🏗️ アーキテクチャの完全刷新
- **モジュラー設計**: 機能別に分離された明確な責任境界
- **依存性注入**: テスタブルで拡張可能な設計
- **ファクトリパターン**: 環境別の最適化されたインスタンス生成
- **抽象基底クラス**: インターフェースの明確化

### 🧪 包括的テストスイート
- **テストカバレッジ84%**: 高品質なコード保証
- **160+テストケース**: 全機能の動作確認
- **モック・スタブ活用**: 外部依存の分離
- **統合テスト**: 実際のワークフローの検証

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

### 🔔 監視・アラート機能
- **エラー追跡**: 包括的な例外監視
- **メトリクス収集**: システム健康状態の可視化
- **自動アラート**: しきい値ベースの通知
- **メール・Slack通知**: 複数チャネル対応

## 🏛️ アーキテクチャ構成

```
src/ishifuku/
├── config.py              # 統一設定管理
├── core.py                 # メインスクレイピングロジック
├── optimized_core.py       # パフォーマンス最適化版
├── scraping/               # スクレイピング機能
│   ├── driver.py           # WebDriver管理
│   ├── parser.py           # HTML解析
│   └── extractor.py        # 価格抽出
├── storage/                # データ永続化
│   ├── csv_handler.py      # CSVストレージ
│   └── s3_handler.py       # S3ストレージ
├── utils/                  # ユーティリティ
│   ├── datetime_utils.py   # 日時処理
│   └── logging_utils.py    # ログ管理
└── monitoring/             # 監視機能
    ├── __init__.py         # パフォーマンス監視
    └── alerting.py         # アラート管理
```

## 🔧 設定管理

### 環境別設定

```python
# ローカル環境
config = ApplicationConfig.get_config("local")

# Lambda環境  
config = ApplicationConfig.get_config("lambda")
```

### 設定項目

```python
@dataclass
class ApplicationConfig:
    scraping: ScrapingConfig      # スクレイピング設定
    webdriver: WebDriverConfig    # WebDriver設定
    storage: StorageConfig        # ストレージ設定
    log_level: str = "INFO"       # ログレベル
    log_file: str = "logs/app.log"  # ログファイル
    environment: str = "local"    # 実行環境
```

## 🚀 使用方法

### 基本的な使用法

```python
from src.ishifuku.core import create_gold_price_scraper

# スクレイパー作成・実行
with create_gold_price_scraper() as scraper:
    success, error = scraper.scrape_and_save()
    if success:
        print("✅ 金価格の取得に成功しました")
    else:
        print(f"❌ エラー: {error}")
```

### 最適化版の使用

```python
from src.ishifuku.optimized_core import create_optimized_scraper

# キャッシュ・監視機能付き
with create_optimized_scraper(
    environment="local",
    enable_cache=True,
    cache_ttl=300
) as scraper:
    success, error = scraper.scrape_and_save()
```

### コマンドライン実行

```bash
# 基本スクレイピング
python -m src.main_monitoring scrape

# キャッシュ無効化
python -m src.main_monitoring scrape --no-cache

# Lambda環境用
python -m src.main_monitoring scrape --environment lambda

# キャッシュ管理
python -m src.main_monitoring cache info
python -m src.main_monitoring cache clear
python -m src.main_monitoring cache warmup

# 監視状態確認
python -m src.main_monitoring monitor
```

## 🧪 テスト実行

### 全テスト実行

```bash
# カバレッジ付きテスト実行
python -m pytest tests/ --cov=src/ishifuku --cov-report=html -v

# 特定モジュールのテスト
python -m pytest tests/test_core.py -v

# 並列実行（高速化）
python -m pytest tests/ -n auto
```

### テスト構成

```
tests/
├── test_config.py          # 設定管理テスト
├── test_core.py            # コア機能テスト
├── test_extractor.py       # 価格抽出テスト
├── test_parser.py          # HTML解析テスト
├── test_driver.py          # WebDriverテスト
├── test_storage.py         # ストレージテスト
├── test_s3_storage.py      # S3ストレージテスト
├── test_utils.py           # ユーティリティテスト
├── test_monitoring.py      # 監視機能テスト
├── test_scrape_ishifuku.py # レガシー互換テスト
└── test_scraping_functions.py # 統合テスト
```

## 📊 パフォーマンス最適化

### キャッシュ機能

```python
# キャッシュ有効化（デフォルト5分）
scraper = create_optimized_scraper(
    enable_cache=True,
    cache_ttl=300  # 5分
)

# キャッシュ情報確認
cache_info = scraper.get_cache_info()
print(f"キャッシュ有効: {cache_info['is_valid']}")
print(f"経過時間: {cache_info['age_seconds']}秒")

# キャッシュクリア
scraper.clear_cache()
```

### パフォーマンス測定

```python
from src.ishifuku.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_monitoring()

# 処理実行
with monitor.measure_operation("scraping"):
    # スクレイピング処理
    pass

results = monitor.stop_monitoring()
print(f"実行時間: {results['total_execution_time']:.2f}秒")
print(f"ピークメモリ: {results['memory_peak']/1024/1024:.1f}MB")
```

## 🔔 監視・アラート設定

### 基本監視

```python
from src.ishifuku.monitoring.alerting import create_monitoring_system

# 監視システム初期化
monitoring = create_monitoring_system()

# 実行データ追跡
execution_data = {
    "execution_time": 15.0,
    "memory_peak": 100000000,
    "success": True
}
monitoring.track_execution(execution_data)

# アラートチェック
alerts = monitoring.check_and_send_alerts()

# システム健康状態
health = monitoring.get_health_status()
print(f"状態: {health['status']}")
```

### アラートルール設定

```python
# カスタムアラートルール
alert_manager.add_alert_rule({
    "name": "高エラー率アラート",
    "condition": "error_count",
    "threshold": 5,
    "severity": "critical",
    "message": "エラーが頻発しています"
})

alert_manager.add_alert_rule({
    "name": "長時間実行アラート", 
    "condition": "execution_time",
    "threshold": 60.0,
    "severity": "warning",
    "message": "実行時間が長すぎます"
})
```

### メール通知設定

```bash
# 環境変数でメール設定
export ALERT_EMAIL_ENABLED=true
export ALERT_EMAIL_FROM=noreply@example.com
export ALERT_EMAIL_TO=admin@example.com
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USE_TLS=true
export SMTP_USERNAME=your_username
export SMTP_PASSWORD=your_password
```

## 🚀 CI/CD パイプライン

### GitHub Actions ワークフロー

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12, 3.13]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest-cov pytest-mock
    
    - name: Run tests with coverage
      run: |
        pytest tests/ \
          --cov=src/ishifuku \
          --cov-fail-under=80 \
          --junitxml=pytest-results.xml
```

### 品質ゲート

- **テストカバレッジ**: 80%以上必須
- **Linting**: flake8, black, isort
- **型チェック**: mypy
- **セキュリティ**: bandit, safety

## 📦 デプロイ

### ローカル環境

```bash
# 依存関係インストール
pip install -r requirements.txt

# 設定確認
python -c "from src.ishifuku.config import ApplicationConfig; print(ApplicationConfig.get_config('local'))"

# 実行
python -m src.main_monitoring scrape
```

### AWS Lambda

```bash
# Lambda パッケージ作成
cd lambda/
pip install -r requirements.txt -t .
zip -r ../lambda-function.zip . -x "*.pyc" "__pycache__/*"

# デプロイ（AWS CLI）
aws lambda update-function-code \
  --function-name ishifuku-scraper \
  --zip-file fileb://../lambda-function.zip
```

### Docker化

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY tests/ tests/

# Chrome インストール
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver

CMD ["python", "-m", "src.main_monitoring", "scrape"]
```

## 📈 メトリクス・KPI

### パフォーマンス指標

- **実行時間**: 平均15-20秒（キャッシュ無し）
- **メモリ使用量**: ピーク100-200MB
- **成功率**: 99%以上
- **応答時間**: ページロード3秒以下

### 品質指標

- **テストカバレッジ**: 84%（目標95%）
- **コード複雑度**: 関数あたり10以下
- **バグ密度**: 月次5件以下
- **可用性**: 99.9%

## 🔧 トラブルシューティング

### よくある問題

#### ChromeDriverエラー
```bash
# ChromeDriverバージョン確認
chromedriver --version

# 手動インストール
pip install webdriver-manager
```

#### メモリ不足
```python
# メモリ使用量最適化
config = WebDriverConfig(
    chrome_arguments=[
        "--memory-pressure-off",
        "--disable-dev-shm-usage",
        "--no-sandbox"
    ]
)
```

#### ネットワークタイムアウト
```python
# タイムアウト設定調整
config = ScrapingConfig(
    base_url="https://ishifuku.co.jp",
    timeout=30,  # 30秒に延長
    retry_count=3
)
```

### ログ分析

```bash
# エラーログ確認
tail -f logs/scraping_error.log

# 特定エラーの検索
grep "TimeoutException" logs/scraping_error.log

# パフォーマンスログ分析
grep "実行時間" logs/scraping_info.log | tail -10
```

## 📚 開発ガイド

### 新機能追加手順

1. **要件定義**: 機能仕様の明確化
2. **設計**: アーキテクチャへの組み込み方検討
3. **テスト作成**: TDD アプローチでテスト先行
4. **実装**: 既存パターンに従った実装
5. **テスト実行**: カバレッジ維持の確認
6. **ドキュメント更新**: 使用方法の文書化

### コード規約

```python
# 型ヒント必須
def extract_price(text: str) -> Optional[int]:
    """価格を抽出"""
    pass

# ドキュメント文字列
def scrape_data(url: str) -> Dict[str, Any]:
    """
    データをスクレイピング
    
    Args:
        url: スクレイピング対象URL
        
    Returns:
        Dict[str, Any]: スクレイピング結果
        
    Raises:
        TimeoutException: タイムアウト時
    """
    pass

# ログ出力
from .utils import log_info, log_error

log_info("処理を開始します")
log_error("エラーが発生しました", exception)
```

### テスト作成指針

```python
# モック活用
@patch('src.ishifuku.scraping.driver.webdriver.Chrome')
def test_webdriver_creation(self, mock_chrome):
    """WebDriver作成テスト"""
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver
    
    factory = ChromeDriverFactory()
    driver = factory.create_driver()
    
    assert driver == mock_driver
    mock_chrome.assert_called_once()

# 例外テスト
def test_error_handling(self):
    """エラーハンドリングテスト"""
    scraper = GoldPriceScraper()
    
    with pytest.raises(TimeoutException):
        scraper.scrape_with_invalid_url()
```

## 🎯 今後の拡張計画

### Phase 3: 高度な機能
- **機械学習**: 価格予測・異常検知
- **分散処理**: Celery/Redis による並列化
- **リアルタイム**: WebSocket によるライブ更新
- **API化**: FastAPI による REST API 提供

### Phase 4: 企業対応
- **マルチテナント**: 複数顧客対応
- **RBAC**: ロールベースアクセス制御
- **監査ログ**: 完全な操作履歴
- **SLA**: サービスレベル保証

## 👥 貢献者ガイド

### 開発環境セットアップ

```bash
# プロジェクトクローン
git clone https://github.com/your-org/ishifuku.git
cd ishifuku

# 仮想環境作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 開発依存関係インストール
pip install -r requirements.txt
pip install -r requirements-dev.txt

# pre-commit フック設定
pre-commit install
```

### プルリクエスト手順

1. **Issue作成**: 修正・機能追加の内容を説明
2. **ブランチ作成**: `feature/issue-123-description`
3. **実装**: テスト込みで実装
4. **テスト実行**: 全テストパス確認
5. **プルリクエスト**: 詳細な説明付きで作成
6. **レビュー**: コードレビュー対応
7. **マージ**: CI/CD パス後にマージ

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

---

**Ishifuku Gold Price Scraper v2** - Professional Web Scraping Solution with Monitoring & CI/CD
