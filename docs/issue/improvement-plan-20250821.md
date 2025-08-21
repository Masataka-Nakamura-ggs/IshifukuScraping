# 石福金属興業スクレイピングツール 改善指示書
## 型安全性向上・カバレッジ向上・コード品質改善

**作成日**: 2025年8月21日  
**対象バージョン**: v1.0.0  
**現在の状況**: カバレッジ66%、mypy型チェックエラー37件

---

## 📊 現状分析

### 1. テストカバレッジ分析（現在66%）

#### 低カバレッジモジュール（優先改善対象）
```
src/ishifuku/optimized_core.py       0%    (122/122 未テスト)
src/main_lambda.py                   0%    (41/41 未テスト)
src/main_local.py                    0%    (28/28 未テスト)
src/main_monitoring.py              0%    (116/116 未テスト)
src/ishifuku/storage/s3_handler.py  20%   (71/89 未テスト)
src/ishifuku/monitoring/__init__.py 64%   (41/113 未テスト)
src/ishifuku/storage/__init__.py    54%   (6/13 未テスト)
```

#### 高カバレッジモジュール（維持対象）
```
src/ishifuku/scraping/driver.py     99%   ✅
src/ishifuku/storage/csv_handler.py 99%   ✅
src/ishifuku/scraping/parser.py     97%   ✅
src/ishifuku/config.py              96%   ✅
src/ishifuku/scraping/extractor.py  93%   ✅
scrape_ishifuku.py                  92%   ✅
```

### 2. mypy型チェックエラー分析（37件）

#### エラー分類
1. **型アノテーション不足**: 7件
   - 辞書型の型パラメータ未指定
   - 変数の型注釈不足

2. **型の不一致**: 15件
   - `None`と他の型の代入エラー
   - 戻り値型の不一致

3. **属性アクセスエラー**: 10件
   - BeautifulSoup4の`Union`型による属性エラー
   - Selenium型定義の不一致

4. **その他**: 5件
   - 継承関係のエラー
   - モジュール参照エラー

---

## 🎯 改善目標

### 数値目標
- **テストカバレッジ**: 66% → **73%以上**
- **mypy型チェック**: 37エラー → **0エラー**
- **型アノテーション率**: 推定60% → **90%以上**

### 品質目標
- 段階的な型安全性向上
- CI/CDでの型チェック自動化
- コードレビュー品質向上

---

## 📋 実行計画

### Phase 1: 型安全性基盤構築 (1-2日)

#### 1.1 mypy設定強化
```toml
# pyproject.toml の [tool.mypy] セクション更新
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true      # 段階的に有効化
disallow_incomplete_defs = true   # 段階的に有効化
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# モジュール別設定
[[tool.mypy.overrides]]
module = [
    "src.ishifuku.optimized_core",
    "src.main_lambda",
    "src.main_local",
    "src.main_monitoring"
]
# 未テストモジュールは段階的に厳格化
disallow_untyped_defs = false
```

#### 1.2 型スタブファイル追加
```bash
# 必要な型スタブをインストール
pip install types-beautifulsoup4 types-requests types-selenium
```

#### 1.3 最優先修正エラー（10件）
1. **config.py の型不一致エラー**
   ```python
   # Before
   self.enabled_features: list[str] = config.get("enabled_features")  # None エラー
   
   # After
   self.enabled_features: list[str] = config.get("enabled_features", [])
   ```

2. **main_lambda.py の型アノテーション追加**
   ```python
   # Before
   test_event = {
   
   # After
   test_event: Dict[str, Any] = {
   ```

3. **BeautifulSoup4 型エラー修正**
   ```python
   # Before
   element.get("href")  # Union型エラー
   
   # After
   if isinstance(element, Tag):
       return element.get("href")
   ```

### Phase 2: テストカバレッジ向上 (2-3日)

#### 2.1 未テストモジュールのテスト追加

##### A. `src/main_lambda.py` テスト作成
```python
# tests/test_main_lambda.py (新規作成)
import pytest
from unittest.mock import Mock, patch
from src.main_lambda import lambda_handler, create_scraper_with_config

class TestMainLambda:
    """main_lambda.py のテスト"""
    
    @patch('src.main_lambda.GoldPriceScraper')
    def test_lambda_handler_success(self, mock_scraper_class):
        """正常なLambda実行をテスト"""
        # モックの設定
        mock_scraper = Mock()
        mock_scraper.scrape_gold_price.return_value = 17530
        mock_scraper_class.return_value = mock_scraper
        
        # テスト実行
        event = {"test": True}
        context = Mock()
        result = lambda_handler(event, context)
        
        # 検証
        assert result["statusCode"] == 200
        assert "price" in result["body"]

    def test_create_scraper_with_config(self):
        """スクレイパー設定作成をテスト"""
        # テスト実装
        pass
```

##### B. `src/main_local.py` テスト作成
```python
# tests/test_main_local.py (新規作成)
import pytest
from unittest.mock import Mock, patch
from src.main_local import main, setup_local_environment

class TestMainLocal:
    """main_local.py のテスト"""
    
    @patch('src.main_local.GoldPriceScraper')
    def test_main_execution(self, mock_scraper_class):
        """メイン実行をテスト"""
        # テスト実装
        pass
```

##### C. `src/ishifuku/storage/s3_handler.py` テスト追加
```python
# tests/test_s3_handler.py への追加
class TestS3HandlerEdgeCases:
    """S3Handler の境界ケーステスト"""
    
    def test_upload_with_network_error(self):
        """ネットワークエラー時のハンドリング"""
        pass
    
    def test_download_nonexistent_file(self):
        """存在しないファイルのダウンロード"""
        pass
    
    def test_connection_timeout(self):
        """接続タイムアウトのテスト"""
        pass
```

#### 2.2 統合テスト強化
```python
# tests/test_integration_extended.py (新規作成)
class TestEndToEndWorkflow:
    """エンドツーエンド統合テスト"""
    
    def test_complete_scraping_workflow(self):
        """完全なスクレイピングワークフローをテスト"""
        # 実際のHTMLパターンを使用した統合テスト
        pass
    
    def test_error_recovery_workflow(self):
        """エラー回復ワークフローをテスト"""
        pass
```

#### 2.3 カバレッジ計測の強化
```bash
# より詳細なカバレッジレポート
pytest tests/ \
    --cov=src \
    --cov=scrape_ishifuku \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --cov-report=json:coverage.json \
    --cov-fail-under=73
```

### Phase 3: コード品質改善 (1-2日)

#### 3.1 型アノテーション追加・改善

##### 優先度A: 公開インターフェース
```python
# 例: src/ishifuku/core.py
from typing import Optional, Dict, Any, List, Union

class GoldPriceScraper:
    def __init__(
        self,
        config: Optional[ApplicationConfig] = None,
        webdriver_manager: Optional[WebDriverManager] = None,
        storage: Optional[DataStorage] = None,
    ) -> None:
        """型アノテーション完全版"""
        
    def scrape_gold_price(self) -> Optional[int]:
        """戻り値型を明確化"""
        
    def get_debug_info(self) -> Dict[str, Any]:
        """デバッグ情報の型定義"""
```

##### 優先度B: 内部メソッド
```python
# 例: src/ishifuku/scraping/parser.py
class HTMLParser:
    def find_price_link_patterns(self, html: str) -> Optional[str]:
        """より具体的な型アノテーション"""
        
    def extract_table_data(self, html: str) -> List[List[str]]:
        """ネストしたリスト型の明確化"""
```

#### 3.2 型ガード関数の追加
```python
# src/ishifuku/utils/type_utils.py (新規作成)
from typing import TypeGuard
from bs4 import Tag, NavigableString, PageElement

def is_tag(element: PageElement) -> TypeGuard[Tag]:
    """Tag型のチェック関数"""
    return hasattr(element, 'get')

def is_navigable_string(element: PageElement) -> TypeGuard[NavigableString]:
    """NavigableString型のチェック関数"""
    return isinstance(element, NavigableString)
```

#### 3.3 プロトコル定義の追加
```python
# src/ishifuku/protocols.py (新規作成)
from typing import Protocol, Optional

class PriceExtractorProtocol(Protocol):
    """価格抽出器のプロトコル定義"""
    
    def extract_price(self, html: str) -> Optional[int]:
        """価格抽出メソッド"""
        ...

class StorageProtocol(Protocol):
    """ストレージのプロトコル定義"""
    
    def save_data(self, data: dict) -> bool:
        """データ保存メソッド"""
        ...
```

### Phase 4: CI/CD統合 (1日)

#### 4.1 GitHub Actions ワークフロー更新
```yaml
# .github/workflows/ci-cd.yml に追加
- name: Type checking with mypy
  run: |
    python -m mypy src/ --config-file pyproject.toml
    
- name: Coverage check
  run: |
    python -m pytest tests/ --cov=src --cov-fail-under=73
    
- name: Type coverage report
  run: |
    python -m mypy src/ --html-report mypy-report/
```

#### 4.2 pre-commit フック設定
```yaml
# .pre-commit-config.yaml (新規作成)
repos:
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        args: [--config-file=pyproject.toml]
        
      - id: pytest-coverage
        name: pytest-coverage
        entry: pytest
        language: system
        args: [--cov=src, --cov-fail-under=73]
        pass_filenames: false
```

---

## 📝 詳細作業手順

### 手順1: 環境準備
```bash
# 1. 型チェックツールの更新
pip install --upgrade mypy types-beautifulsoup4 types-requests

# 2. カバレッジツールの準備
pip install --upgrade pytest-cov coverage

# 3. pre-commit設定（オプション）
pip install pre-commit
pre-commit install
```

### 手順2: 段階的修正アプローチ

#### Week 1: 基盤修正
- [ ] mypy設定更新
- [ ] 最優先エラー10件修正
- [ ] 型スタブ追加

#### Week 2: テスト拡充
- [ ] main_lambda.py テスト追加（目標: 80%カバレッジ）
- [ ] main_local.py テスト追加（目標: 80%カバレッジ）
- [ ] s3_handler.py テスト追加（目標: 60%カバレッジ）

#### Week 3: 品質向上
- [ ] 型アノテーション追加
- [ ] プロトコル定義実装
- [ ] CI/CD統合

### 手順3: 進捗管理

#### 毎日の確認項目
```bash
# mypy エラー数確認
python -m mypy src/ --config-file pyproject.toml | grep "Found" | tail -1

# カバレッジ確認
python -m pytest tests/ --cov=src --cov-report=term | grep "TOTAL"

# 型アノテーション率確認（手動）
find src/ -name "*.py" -exec grep -l ":" {} \; | wc -l
```

#### マイルストーン確認
- **1週間後**: mypy エラー 37 → 20以下
- **2週間後**: カバレッジ 66% → 70%以上
- **3週間後**: mypy エラー 0、カバレッジ 73%以上

---

## 🚨 注意事項・リスク

### 技術的リスク
1. **BeautifulSoup4型エラー**: `Union[Tag, NavigableString]`型の扱いに注意
2. **Selenium型定義**: WebDriverの型定義が不安定
3. **テスト環境**: Lambda環境とローカル環境の違い

### 作業リスク
1. **既存機能への影響**: 段階的修正で最小化
2. **テスト追加時間**: 予想より時間がかかる可能性
3. **mypy設定**: 厳格化による新規エラーの発生

### 対策
- 小さな変更で頻繁にテスト実行
- 型エラー修正は1つずつ確実に
- 既存テストの継続パスを確認

---

## 📈 成功指標

### 定量指標
- [x] **現在のカバレッジ**: 66%
- [ ] **目標カバレッジ**: 73%以上
- [x] **現在のmypyエラー**: 37件
- [ ] **目標mypyエラー**: 0件
- [ ] **型アノテーション率**: 90%以上

### 定性指標
- [ ] コードレビューでの型関連指摘の減少
- [ ] 新機能開発時の型安全性確保
- [ ] チーム開発での型情報活用

---

## 📚 参考資料

### 型ヒント関連
- [Python typing module documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

### テスト関連
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python.org/3/library/unittest.html)

### プロジェクト固有
- `./docs/ARCHITECTURE_v2.md`: アーキテクチャ詳細
- `./README_COMPLETE.md`: 包括的なプロジェクトガイド
- `./tests/`: 既存テスト実装例

---

**最終更新**: 2025年8月21日  
**次回レビュー予定**: 2025年8月28日
