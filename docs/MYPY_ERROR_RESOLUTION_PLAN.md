# mypy エラー解決作業指示書

## 概要
52個のmypyエラーから42個を修正し、残り10個のエラーの解決方針を定義する。

## 現在の進捗
- ✅ 修正済み: 42個（81%改善）
- ⚠️ 残存エラー: 10個

## 残存エラー詳細分析

### 1. import-not-found エラー (5個) - 優先度: 高

#### 対象ファイル
- `src/main_local.py`: `from ishifuku import ...`
- `src/main_lambda.py`: `from ishifuku import ...`

#### 根本原因
- パッケージ構造が`src/ishifuku/`なのに、`ishifuku`として直接インポートしている
- mypy実行時のモジュール解決パスの問題

#### 解決策
1. **相対インポートに変更**
   ```python
   # 変更前
   from ishifuku import get_config, setup_logging
   from ishifuku.core import create_gold_price_scraper
   
   # 変更後  
   from .ishifuku import get_config, setup_logging
   from .ishifuku.core import create_gold_price_scraper
   ```

2. **pyproject.tomlでmypathを設定**
   ```toml
   [tool.mypy]
   mypy_path = "src"
   ```

3. **パッケージ構造の明確化**
   - `src/ishifuku/__init__.py`で必要な関数をエクスポート

### 2. arg-type エラー (1個) - 優先度: 中

#### 対象ファイル
- `src/ishifuku/core.py:184`

#### エラー内容
```
Argument 1 to "wait_for_element" of "WebDriverManager" has incompatible type "str"; expected "By"
```

#### 根本原因
- `wait_for_element(By.TAG_NAME, "table")`の呼び出し
- WebDriverManagerの型定義とSeleniumの型定義の齟齬

#### 解決策
1. **WebDriverManagerの型定義修正**
   ```python
   def wait_for_element(self, by: By, value: str, timeout: int = 10) -> None:
   ```

2. **呼び出し側の型キャスト**
   ```python
   self.webdriver_manager.wait_for_element(By.TAG_NAME, "table")  # type: ignore
   ```

### 3. optimized_core.py 関連エラー (3個) - 優先度: 高

#### エラー詳細
1. `"find_price_page_url" undefined in superclass`
2. `Signature of "scrape_gold_price" incompatible with supertype`
3. `Too many arguments for "scrape_gold_price"`

#### 根本原因
- `OptimizedGoldPriceScraper`が基底クラス`GoldPriceScraper`と互換性がない
- メソッドシグネチャの不一致

#### 解決策
1. **基底クラスにメソッド追加**
   ```python
   # core.py に追加
   def find_price_page_url(self, driver: Any) -> str:
       """価格ページURLを検索（基底実装）"""
       return self._find_price_page_url()
   ```

2. **メソッドシグネチャ統一**
   ```python
   # optimized_core.py 修正
   def scrape_gold_price(self) -> int:  # driverパラメータ削除
       """金価格を取得（パフォーマンス測定付き）"""
       with self.performance_monitor.measure_operation("extract_price"):
           return super().scrape_gold_price()
   ```

### 4. attr-defined エラー (1個) - 優先度: 中

#### 対象ファイル
- `src/main_monitoring.py:14`

#### エラー内容
```
Module "src.ishifuku.monitoring" has no attribute "create_monitoring_system"
```

#### 根本原因
- `create_monitoring_system`は`alerting.py`に存在するが、`monitoring/__init__.py`でエクスポートされていない

#### 解決策
1. **monitoring/__init__.pyに追加**
   ```python
   # monitoring/__init__.py
   from .alerting import create_monitoring_system
   
   __all__ = [
       "PerformanceMonitor",
       "WebDriverPerformanceMonitor", 
       "timing_decorator",
       "memory_profile",
       "create_monitoring_system",  # 追加
   ]
   ```

## 作業計画

### Phase 1: パッケージ構造の修正 (1-2時間)
1. `pyproject.toml`にmypy_path設定追加
2. `src/ishifuku/__init__.py`で必要な関数をエクスポート
3. main_local.py, main_lambda.pyのインポート修正

### Phase 2: クラス設計の修正 (2-3時間)
1. `core.py`に`find_price_page_url(driver)`メソッド追加
2. `optimized_core.py`のメソッドシグネチャ修正
3. 継承関係の整合性確保

### Phase 3: モジュールエクスポートの修正 (30分)
1. `monitoring/__init__.py`に`create_monitoring_system`追加
2. 型定義の最終確認

### Phase 4: 型定義の最適化 (30分)
1. WebDriverManagerの型定義修正
2. type: ignoreコメントの最適化

## 成功基準
- mypy エラー数: 0個
- 全ての機能テストが通過
- コードの可読性と保守性を維持

## リスク評価
- **低リスク**: モジュールエクスポート修正
- **中リスク**: パッケージ構造修正（実行時に影響する可能性）
- **高リスク**: クラス設計修正（既存の継承関係に影響）

## 注意事項
1. 修正後は必ず既存のテストを実行して回帰がないことを確認
2. optimized_core.pyの修正は段階的に実施し、各段階でテスト実行
3. パッケージ構造変更後は import文の動作確認を徹底

## 完了後の確認項目
- [ ] mypy --explicit-package-bases src/ がエラー0で終了
- [ ] 既存のテストスイートが全て通過  
- [ ] main_local.py, main_lambda.pyが正常実行
- [ ] optimized_core.pyのパフォーマンス機能が正常動作
