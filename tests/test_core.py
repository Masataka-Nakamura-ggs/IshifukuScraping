#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいアーキテクチャのテストファイル - コアスクレイピング機能
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.ishifuku.config import ApplicationConfig, StorageConfig
from src.ishifuku.core import (
    GoldPriceScraper,
    create_gold_price_scraper,
    scrape_gold_price,
)
from src.ishifuku.storage import CSVStorage


class TestGoldPriceScraper:
    """GoldPriceScraperのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        # テスト用の設定を作成
        self.config = ApplicationConfig()

        # モックオブジェクトを作成
        self.mock_webdriver_manager = MagicMock()
        self.mock_storage = MagicMock()

        # スクレイパーを作成
        self.scraper = GoldPriceScraper(
            config=self.config,
            webdriver_manager=self.mock_webdriver_manager,
            storage=self.mock_storage,
        )

    def test_initialization(self):
        """初期化が正しく動作することを確認"""
        assert self.scraper.config == self.config
        assert self.scraper.webdriver_manager == self.mock_webdriver_manager
        assert self.scraper.storage == self.mock_storage
        assert self.scraper.html_parser is not None
        assert self.scraper.price_extractor is not None

    def test_initialization_with_defaults(self):
        """デフォルト設定での初期化を確認"""
        scraper = GoldPriceScraper()

        assert scraper.config is not None
        assert scraper.webdriver_manager is not None
        assert scraper.storage is not None

    @patch("src.ishifuku.utils.log_info")
    def test_scrape_gold_price_success(self, mock_log_info):
        """金価格スクレイピングの成功ケースを確認"""
        # HTMLと価格の準備
        mock_html = """
        <html>
            <table>
                <tr><td>金(g)</td><td>17,530</td></tr>
            </table>
        </html>
        """

        # モックの設定
        self.mock_webdriver_manager.get_page_source.return_value = mock_html
        self.scraper.html_parser.find_price_link_patterns = MagicMock(
            return_value="https://example.com/price"
        )

        # テスト実行
        price = self.scraper.scrape_gold_price()

        # 検証
        assert price == 17530
        assert (
            self.mock_webdriver_manager.navigate_to.call_count == 2
        )  # トップページ + 価格ページ
        assert self.mock_webdriver_manager.get_page_source.called

    @patch("src.ishifuku.core.log_error")
    def test_scrape_gold_price_failure(self, mock_log_error):
        """金価格スクレイピングの失敗ケースを確認"""
        # エラーを発生させる
        self.mock_webdriver_manager.navigate_to.side_effect = Exception("Network error")

        # テスト実行
        with pytest.raises(Exception, match="Network error"):
            self.scraper.scrape_gold_price()

        # エラーログが記録されることを確認
        mock_log_error.assert_called()

    def test_scrape_and_save_success(self):
        """スクレイピングと保存の成功ケースを確認"""
        # モックの設定
        self.scraper.scrape_gold_price = MagicMock(return_value=17530)
        self.mock_storage.save.return_value = "result/test.csv"

        # テスト実行
        result = self.scraper.scrape_and_save()

        # 検証
        assert result["success"] is True
        assert result["gold_price"] == 17530
        assert result["filepath"] == "result/test.csv"
        assert "date_str" in result
        assert "datetime_str" in result

    def test_scrape_and_save_failure(self):
        """スクレイピングと保存の失敗ケースを確認"""
        # エラーを発生させる
        self.scraper.scrape_gold_price = MagicMock(
            side_effect=Exception("Scraping failed")
        )

        # テスト実行
        result = self.scraper.scrape_and_save()

        # 検証
        assert result["success"] is False
        assert "error" in result
        assert "Scraping failed" in result["error"]

    def test_find_price_page_url_with_link(self):
        """価格ページURLの検索（リンク発見）を確認"""
        # モックの設定
        self.mock_webdriver_manager.get_page_source.return_value = "<html></html>"
        self.scraper.html_parser.find_price_link_patterns = MagicMock(
            return_value="https://example.com/price"
        )

        # テスト実行
        url = self.scraper._find_price_page_url()

        # 検証
        assert url == "https://example.com/price"

    def test_find_price_page_url_fallback(self):
        """価格ページURLの検索（フォールバック）を確認"""
        # モックの設定
        self.mock_webdriver_manager.get_page_source.return_value = "<html></html>"
        self.scraper.html_parser.find_price_link_patterns = MagicMock(return_value=None)

        # テスト実行
        url = self.scraper._find_price_page_url()

        # 検証
        assert url == self.config.scraping.price_url

    def test_close(self):
        """リソースクリーンアップが正しく動作することを確認"""
        self.scraper.close()
        self.mock_webdriver_manager.close.assert_called_once()

    def test_context_manager(self):
        """コンテキストマネージャーが正しく動作することを確認"""
        with self.scraper as scraper:
            assert scraper == self.scraper

        self.mock_webdriver_manager.close.assert_called_once()


class TestGoldPriceScraperIntegration:
    """GoldPriceScraperの統合テスト"""

    def test_real_csv_storage(self):
        """実際のCSVストレージとの統合テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用設定
            storage_config = StorageConfig(result_dir=temp_dir)
            config = ApplicationConfig(storage=storage_config)

            # モックWebDriverManagerを使用
            mock_webdriver_manager = MagicMock()
            mock_html = """
            <html>
                <table>
                    <tr><td>金(g)</td><td>17,530</td></tr>
                </table>
            </html>
            """
            mock_webdriver_manager.get_page_source.return_value = mock_html

            # 実際のCSVストレージを使用
            storage = CSVStorage(storage_config)

            # スクレイパーを作成
            scraper = GoldPriceScraper(
                config=config, webdriver_manager=mock_webdriver_manager, storage=storage
            )

            # スクレイピング処理（価格抽出部分のみモック化）
            scraper.html_parser.find_price_link_patterns = MagicMock(
                return_value="https://example.com/price"
            )

            # テスト実行
            result = scraper.scrape_and_save()

            # 検証
            assert result["success"] is True
            assert result["gold_price"] == 17530
            assert os.path.exists(result["filepath"])

            # ファイル内容の確認
            with open(result["filepath"], "r", encoding="utf-8") as f:
                content = f.read()
                assert "17530" in content


class TestFactory:
    """ファクトリ関数のテスト"""

    def test_create_gold_price_scraper_default(self):
        """デフォルト設定でのスクレイパー作成を確認"""
        scraper = create_gold_price_scraper()

        assert isinstance(scraper, GoldPriceScraper)
        assert scraper.config.environment == "local"

    def test_create_gold_price_scraper_lambda(self):
        """Lambda環境でのスクレイパー作成を確認"""
        scraper = create_gold_price_scraper("lambda")

        assert isinstance(scraper, GoldPriceScraper)
        assert scraper.config.environment == "lambda"

    def test_create_gold_price_scraper_with_config(self):
        """カスタム設定でのスクレイパー作成を確認"""
        config = ApplicationConfig(debug=True)
        scraper = create_gold_price_scraper(config=config)

        assert isinstance(scraper, GoldPriceScraper)
        assert scraper.config.debug is True


class TestBackwardCompatibility:
    """後方互換性のテスト"""

    @patch("src.ishifuku.core.create_gold_price_scraper")
    def test_scrape_gold_price_function(self, mock_create_scraper):
        """scrape_gold_price関数の後方互換性を確認"""
        # モックスクレイパーを設定
        mock_scraper = MagicMock()
        mock_scraper.scrape_gold_price.return_value = 17530
        mock_scraper.__enter__.return_value = mock_scraper
        mock_scraper.__exit__.return_value = None
        mock_create_scraper.return_value = mock_scraper

        # テスト実行
        price = scrape_gold_price()

        # 検証
        assert price == 17530
        mock_create_scraper.assert_called_once()
        mock_scraper.scrape_gold_price.assert_called_once()
