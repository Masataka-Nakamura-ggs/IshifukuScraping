# 石福金属興業スクレイピングツール リファクタリング指示書

**作成日**: 2025年8月21日  
**対象プロジェクト**: IshifukuScraping  
**リファクタリング担当**: GitHub Copilot

## 1. プロジェクトの概要

* **目的・用途**: 石福金属興業のウェブサイトから金の小売価格を自動取得し、CSVファイルに保存するバッチ処理ツール。ローカル実行とAWS Lambda両方に対応。
* **プロジェクトの規模**: メインファイル1個、Lambda用ファイル1個、テストファイル2個の小規模なツール（約15ファイル）
* **主要な技術スタック**: Python 3.13, Selenium, BeautifulSoup, requests, pytest, AWS Lambda, GitHub Actions
* **チームの状況**: 個人開発プロジェクト（将来的な拡張・保守性向上が目標）

## 2. 現状の課題と目標

### 感じている課題

* **単一ファイルへのコード集中**: `scrape_ishifuku.py`（347行）と`lambda_scrape_ishifuku.py`（394行）に機能が集中しすぎている
* **コードの重複**: ローカル版とLambda版で同様の処理が重複している（価格抽出、CSV保存など）
* **関数の責務が不明確**: 一つの関数で複数の処理（スクレイピング + HTML解析 + 価格抽出）を行っている
* **定数・設定値のハードコード**: URL、待機時間、ファイルパスがコード内に散在している
* **型アノテーションの不完全**: 一部の関数で型アノテーションが不足している
* **エラーハンドリングの統一性不足**: printとloggingが混在し、エラー処理の一貫性がない
* **テスト容易性の課題**: Seleniumを直接使用しているため、モック化が困難

### この依頼で達成したい目標

* **保守性の向上**: 機能ごとにモジュールを分離し、修正影響範囲を限定する
* **再利用性の向上**: ローカル版とLambda版で共通処理を統一する
* **テスト容易性の向上**: 依存関係を注入可能にし、ユニットテストを充実させる
* **設定管理の改善**: 定数・設定値を一元管理し、環境ごとに切り替え可能にする
* **コード品質の向上**: 型安全性、エラーハンドリング、ドキュメンテーションを強化する

## 3. 提供する情報

### ソースコード構成
```
ishifuku/
├── scrape_ishifuku.py             # メインスクリプト（347行）
├── lambda/lambda_scrape_ishifuku.py # Lambda版（394行）
├── tests/test_*.py                # テストファイル（2ファイル）
├── pyproject.toml                 # プロジェクト設定
├── requirements.txt               # 依存関係
└── docs/                          # ドキュメント
```

### 現在の依存関係
- **コア**: requests, beautifulsoup4, selenium, webdriver-manager
- **開発**: pytest, pytest-cov, pytest-mock, black, flake8, mypy
- **インフラ**: boto3（Lambda用）

## 4. 依頼したい具体的な作業

### [✓] コードレビュー
- **PEP 8準拠性の確認**: コーディング規約違反の洗い出し
- **複雑すぎるロジックの特定**: `scrape_gold_price()`関数（~150行）の分析
- **Pythonicでない書き方の修正**: リスト内包表記、with文の活用など
- **パフォーマンス上の懸念点**: 無駄な待機時間、重複処理の特定

### [✓] リファクタリング提案
- **ファイル分割戦略**: 機能別モジュール設計（設定、スクレイピング、データ処理、ファイル操作）
- **デザインパターンの適用**: Factory Pattern（WebDriverの生成）、Strategy Pattern（価格抽出）
- **具体的な修正前後のコード例**: 関数分割、クラス設計の提案

### [✓] テスト戦略の立案と実装支援
- **テスト優先順位の提案**: コア機能（価格抽出、CSV保存）から開始
- **モック戦略**: Seleniumのモック化、外部依存の分離
- **テストカバレッジ目標**: 現在92% → 95%以上へ向上

### [✓] ドキュメンテーションの改善
- **API仕様書**: 各関数・クラスのインターフェース定義
- **Docstring標準化**: Google Style Docstringの統一
- **アーキテクチャ図**: モジュール依存関係図（Mermaid記法）

### [✓] 依存関係の整理
- **requirements.txtの最適化**: バージョン固定戦略の見直し
- **セキュリティ監査**: 脆弱性のあるライブラリの確認
- **Poetry移行検討**: 依存関係管理の近代化

### [✓] 自動化の導入支援
- **既存CI/CDの強化**: GitHub Actionsの最適化
- **コード品質ツールの統合**: pre-commit hooks、自動フォーマット
- **静的解析の強化**: mypy設定の改善、ruffの導入検討

## 5. リファクタリング計画

### フェーズ1: 設計・分析（1-2日）
1. **現状コードの詳細分析**
   - 機能マップの作成
   - 依存関係の可視化
   - コード複雑度の測定

2. **アーキテクチャ設計**
   - モジュール分割設計
   - インターフェース定義
   - 設定管理戦略

### フェーズ2: コア機能の抽出（2-3日）
1. **共通処理の抽出**
   ```python
   # 提案構造
   ishifuku/
   ├── src/
   │   ├── ishifuku/
   │   │   ├── __init__.py
   │   │   ├── config.py           # 設定管理
   │   │   ├── scraping/           # スクレイピング機能
   │   │   │   ├── __init__.py
   │   │   │   ├── driver.py       # WebDriver管理
   │   │   │   ├── parser.py       # HTML解析
   │   │   │   └── extractor.py    # 価格抽出
   │   │   ├── storage/            # データ保存
   │   │   │   ├── __init__.py
   │   │   │   ├── csv_handler.py  # CSV操作
   │   │   │   └── s3_handler.py   # S3操作
   │   │   └── utils/              # ユーティリティ
   │   │       ├── __init__.py
   │   │       ├── logging.py      # ログ設定
   │   │       └── datetime.py     # 日時処理
   │   ├── main_local.py           # ローカル実行用
   │   └── main_lambda.py          # Lambda実行用
   ```

2. **設定管理の統一**
   ```python
   # config.py の例
   from dataclasses import dataclass
   from typing import Optional
   
   @dataclass
   class ScrapingConfig:
       base_url: str = "https://www.ishifukushop.com/"
       price_url: str = "https://retail.ishifuku-kinzoku.co.jp/price/"
       wait_time_short: int = 5
       wait_time_long: int = 10
       max_retries: int = 3
       timeout: int = 30
   ```

### フェーズ3: インターフェース統一（1-2日）
1. **抽象基底クラスの導入**
   ```python
   from abc import ABC, abstractmethod
   
   class PriceExtractor(ABC):
       @abstractmethod
       def extract_price(self, html: str) -> Optional[int]:
           pass
   
   class DataStorage(ABC):
       @abstractmethod
       def save(self, data: dict) -> str:
           pass
   ```

2. **依存性注入の実装**
   ```python
   class GoldPriceScraper:
       def __init__(
           self,
           driver_factory: WebDriverFactory,
           price_extractor: PriceExtractor,
           storage: DataStorage,
           config: ScrapingConfig
       ):
           self.driver_factory = driver_factory
           self.price_extractor = price_extractor
           self.storage = storage
           self.config = config
   ```

### フェーズ4: テスト強化（2-3日）
1. **モック戦略の実装**
   ```python
   # 例: WebDriverのモック化
   class MockWebDriver:
       def __init__(self, mock_html: str):
           self.mock_html = mock_html
       
       def get(self, url: str) -> None:
           pass
       
       @property
       def page_source(self) -> str:
           return self.mock_html
   ```

2. **統合テストの追加**
   - エンドツーエンドテスト
   - エラーシナリオテスト
   - パフォーマンステスト

### フェーズ5: ドキュメント・自動化（1日）
1. **API仕様書の作成**
2. **アーキテクチャ図の作成**
3. **CI/CD パイプラインの最適化**

## 6. 期待される効果

### 保守性の向上
- **修正影響範囲の限定**: 機能別モジュール化により、特定機能の修正が他に影響しない
- **可読性の向上**: 各モジュールの責務が明確になり、新規メンバーの理解が容易
- **テスト容易性**: モック化により、外部依存なしでのユニットテスト実行

### 拡張性の向上
- **新機能の追加**: インターフェースが統一されているため、新しい価格抽出方法やストレージの追加が容易
- **環境対応**: 設定管理が統一されているため、新しい実行環境への対応が簡単

### 品質の向上
- **型安全性**: 型アノテーションの徹底により、実行時エラーの早期発見
- **エラーハンドリング**: 統一されたエラー処理により、障害対応が迅速化

## 7. リスク評価とその対策

### リスク
1. **既存機能の動作不良**: リファクタリング中の機能破綻
2. **Lambda環境での動作確認**: 環境依存の問題発生
3. **テスト工数の増加**: 新しいアーキテクチャに対応したテスト作成

### 対策
1. **段階的な移行**: 既存コードを残しつつ、段階的に新アーキテクチャへ移行
2. **継続的テスト**: 各フェーズでの動作確認とテスト実行
3. **ロールバック計画**: 問題発生時の迅速な復旧手順

## 8. 成功指標

### 定量的指標
- **コード行数**: メインファイル 347行 → 各モジュール 100行以下
- **テストカバレッジ**: 92% → 95%以上
- **型チェック**: mypy 100% パス
- **ライブラリ脆弱性**: セキュリティ問題 0件

### 定性的指標
- **可読性**: 新規メンバーが1日で理解可能
- **拡張性**: 新機能追加時の修正ファイル数 3個以下
- **保守性**: バグ修正時の影響範囲特定が容易

## 9. 次のアクション

1. **フェーズ1開始**: 現状分析とアーキテクチャ設計
2. **プロトタイプ作成**: 新アーキテクチャでの動作確認
3. **段階的移行**: 既存機能を保持しつつ新構造へ移行
4. **継続的改善**: 運用開始後のフィードバック反映

---

このリファクタリング計画により、石福金属興業スクレイピングツールは保守性・拡張性・品質すべての面で大幅な改善が期待されます。
