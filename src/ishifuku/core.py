#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金価格スクレイピングコアクラス

統合されたスクレイピング処理を提供します。
"""

import time
from typing import Any, Optional

from selenium.webdriver.common.by import By

from .config import ApplicationConfig
from .scraping import (
    WebDriverManager,
    create_html_parser,
    create_price_extractor,
    create_webdriver_manager,
)
from .storage import DataStorage, create_csv_storage
from .utils import get_current_datetime, log_error, log_info


class GoldPriceScraper:
    """金価格スクレイピングのメインクラス"""

    def __init__(
        self,
        config: Optional[ApplicationConfig] = None,
        webdriver_manager: Optional[WebDriverManager] = None,
        storage: Optional[DataStorage] = None,
    ):
        """
        初期化

        Args:
            config: アプリケーション設定
            webdriver_manager: WebDriverマネージャー（注入可能）
            storage: ストレージインスタンス（注入可能）
        """
        self.config = config or ApplicationConfig()

        # 依存性注入またはデフォルト生成
        self.webdriver_manager = webdriver_manager or create_webdriver_manager(
            self.config.environment, self.config.webdriver
        )

        self.storage = storage or create_csv_storage(self.config.storage)

        # 各種ヘルパーを作成
        self.html_parser = create_html_parser(self.config.scraping)
        self.price_extractor = create_price_extractor(self.config.scraping)

    def scrape_gold_price(self) -> int:
        """
        金価格をスクレイピング

        Returns:
            int: 取得された金価格（円/g）

        Raises:
            Exception: スクレイピングに失敗した場合
        """
        try:
            log_info("金価格スクレイピングを開始")

            # トップページにアクセス
            self._navigate_to_top_page()

            # 価格ページのリンクを検索
            price_url = self._find_price_page_url()

            # 価格ページに移動
            self._navigate_to_price_page(price_url)

            # HTMLを取得して価格を抽出
            html = self.webdriver_manager.get_page_source()
            gold_price = self.price_extractor.extract_price(html)

            if gold_price is None:
                # デバッグ情報を出力
                self._output_debug_info(html)
                raise Exception("金の小売価格が見つかりません")

            log_info(f"金価格を取得しました: {gold_price}円/g")
            return gold_price

        except Exception as e:
            log_error(f"スクレイピングエラー: {e}", e)
            raise

    def scrape_and_save(self) -> dict:
        """
        金価格をスクレイピングして保存

        Returns:
            dict: 実行結果
                - success: 成功フラグ
                - gold_price: 金価格（成功時）
                - filepath: 保存先パス（成功時）
                - error: エラーメッセージ（失敗時）
        """
        date_str, datetime_str, date_for_filename = get_current_datetime()

        try:
            # 金価格を取得
            gold_price = self.scrape_gold_price()

            # データを保存
            data = {
                "date_str": date_str,
                "gold_price": gold_price,
                "datetime_str": datetime_str,
                "date_for_filename": date_for_filename,
            }

            filepath = self.storage.save(data)

            result = {
                "success": True,
                "gold_price": gold_price,
                "filepath": filepath,
                "date_str": date_str,
                "datetime_str": datetime_str,
            }

            log_info(
                f"スクレイピング処理が正常に完了 - 価格: {gold_price}円/g, ファイル: {filepath}"
            )
            return result

        except Exception as e:
            # エラー時は空ファイルを作成
            try:
                if hasattr(self.storage, "create_empty_file"):
                    self.storage.create_empty_file(date_for_filename)
                else:
                    # S3Storage等に上記メソッドがない場合のフォールバック処理として、
                    # Lambda用の設定を使って/tmp以下にCSVの空ファイルを作成する
                    log_info("フォールバック: /tmpに空のCSVファイルを作成します")
                    # self.config.storageにはLambda用の設定が含まれている
                    csv_storage_fallback = create_csv_storage(self.config.storage)
                    csv_storage_fallback.create_empty_file(date_for_filename)
            except Exception as create_err:
                # 空ファイル作成もエラーの場合はログに残して無視
                log_error(f"空ファイルの作成に失敗しました: {create_err}", create_err)
                pass
            except Exception:
                pass  # 空ファイル作成もエラーの場合は無視

            result = {
                "success": False,
                "error": str(e),
                "date_str": date_str,
                "datetime_str": datetime_str,
            }

            log_error(f"スクレイピング処理が失敗しました: {e}", e)
            return result

    def _navigate_to_top_page(self) -> None:
        """トップページに移動"""
        log_info("石福金属興業のトップページにアクセス中...")
        self.webdriver_manager.navigate_to(
            self.config.scraping.base_url, self.config.scraping.wait_time_medium
        )

    def _find_price_page_url(self) -> str:
        """価格ページのURLを検索"""
        html = self.webdriver_manager.get_page_source()
        price_url = self.html_parser.find_price_link_patterns(html)

        # リンクが見つからない場合は直接価格ページを使用
        if not price_url:
            log_info("価格ページへの直接リンクが見つからないため、直接URLを使用します")
            price_url = self.config.scraping.direct_price_url

        log_info(f"価格ページURL: {price_url}")
        return price_url

    def find_price_page_url(self, driver: Any = None) -> str:
        """価格ページのURLを検索（パブリックメソッド）

        Args:
            driver: WebDriverインスタンス（互換性のため、使用されません）

        Returns:
            str: 価格ページのURL
        """
        return self._find_price_page_url()

    def _navigate_to_price_page(self, price_url: str) -> None:
        """価格ページに移動"""
        log_info(f"価格ページにアクセス中: {price_url}")
        self.webdriver_manager.navigate_to(
            price_url, self.config.scraping.wait_time_medium
        )

        # テーブルの読み込みを待機
        self.webdriver_manager.wait_for_element(
            By.TAG_NAME, "table"  # type: ignore[arg-type]
        )

        # 追加の待機時間（価格データが動的に読み込まれる場合）
        time.sleep(self.config.scraping.wait_time_short)

    def _output_debug_info(self, html: str) -> None:
        """デバッグ情報を出力"""
        log_info("=== デバッグ情報 ===")
        debug_info = self.html_parser.get_debug_info(html)

        log_info(f"ページタイトル: {debug_info['page_title']}")
        log_info(f"テーブル数: {debug_info['table_count']}")

        for table_info in debug_info["table_info"]:
            log_info(f"\n--- テーブル {table_info['table_index']} ---")
            for i, row in enumerate(table_info["sample_rows"]):
                log_info(f"行{i + 1}: {row}")

    def close(self) -> None:
        """リソースをクリーンアップ"""
        if self.webdriver_manager:
            self.webdriver_manager.close()

    def __enter__(self) -> "GoldPriceScraper":
        """コンテキストマネージャー入口"""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """コンテキストマネージャー出口"""
        self.close()


def create_gold_price_scraper(
    environment: str = "local", config: Optional[ApplicationConfig] = None
) -> GoldPriceScraper:
    """
    金価格スクレイパーのファクトリ関数

    Args:
        environment: 実行環境（"local" または "lambda"）
        config: アプリケーション設定

    Returns:
        GoldPriceScraper: 金価格スクレイパーインスタンス
    """
    if config is None:
        from .config import get_config

        config = get_config(environment)

    return GoldPriceScraper(config)


# 後方互換性のための関数
def scrape_gold_price() -> int:
    """
    金価格をスクレイピング（後方互換性のための関数）

    Returns:
        int: 取得された金価格（円/g）
    """
    with create_gold_price_scraper() as scraper:
        return scraper.scrape_gold_price()
