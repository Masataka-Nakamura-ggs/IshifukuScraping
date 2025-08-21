#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいアーキテクチャのテストファイル - 設定モジュール
"""

import os

from src.ishifuku.config import (
    ApplicationConfig,
    ScrapingConfig,
    StorageConfig,
    WebDriverConfig,
    get_config,
)


class TestScrapingConfig:
    """ScrapingConfigのテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されることを確認"""
        config = ScrapingConfig()

        assert config.base_url == "https://www.ishifukushop.com/"
        assert config.price_url == "https://retail.ishifuku-kinzoku.co.jp/price/"
        assert config.wait_time_short == 3
        assert config.wait_time_medium == 5
        assert config.wait_time_long == 10
        assert config.max_retries == 3
        assert config.min_valid_price == 10000
        assert config.max_valid_price == 30000

    def test_link_patterns_initialization(self):
        """リンクパターンが正しく初期化されることを確認"""
        config = ScrapingConfig()

        assert config.link_patterns is not None
        assert len(config.link_patterns) > 0
        assert "//a[contains(text(), '本日の小売価格')]" in config.link_patterns


class TestWebDriverConfig:
    """WebDriverConfigのテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されることを確認"""
        config = WebDriverConfig()

        assert config.headless is True
        assert config.window_size == "1920,1080"
        assert "Mozilla/5.0" in config.user_agent

    def test_chrome_arguments_initialization(self):
        """Chrome引数が正しく初期化されることを確認"""
        config = WebDriverConfig()

        assert config.chrome_arguments is not None
        assert "--headless" in config.chrome_arguments
        assert "--no-sandbox" in config.chrome_arguments
        assert "--window-size=1920,1080" in config.chrome_arguments

    def test_headless_false(self):
        """ヘッドレスモード無効時の動作を確認"""
        config = WebDriverConfig(headless=False)

        assert "--headless" not in config.chrome_arguments
        assert "--no-sandbox" in config.chrome_arguments


class TestStorageConfig:
    """StorageConfigのテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されることを確認"""
        config = StorageConfig()

        assert config.result_dir == "result"
        assert config.logs_dir == "logs"
        assert config.csv_filename_template == "ishihuku-gold-{date}.csv"
        assert config.s3_bucket_name is None

    def test_get_csv_filename(self):
        """CSVファイル名生成が正しく動作することを確認"""
        config = StorageConfig()
        filename = config.get_csv_filename("20250821")

        assert filename == "ishihuku-gold-20250821.csv"

    def test_get_log_filename(self):
        """ログファイル名生成が正しく動作することを確認"""
        config = StorageConfig()
        filename = config.get_log_filename("error", "20250821")

        assert filename == "scraping_error_20250821.log"


class TestApplicationConfig:
    """ApplicationConfigのテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されることを確認"""
        config = ApplicationConfig()

        assert config.environment == "local"
        assert config.debug is False
        assert isinstance(config.scraping, ScrapingConfig)
        assert isinstance(config.webdriver, WebDriverConfig)
        assert isinstance(config.storage, StorageConfig)

    def test_lambda_environment(self):
        """Lambda環境設定が正しく動作することを確認"""
        # 環境変数を設定
        os.environ["S3_BUCKET_NAME"] = "test-bucket"

        try:
            config = ApplicationConfig(environment="lambda")

            assert config.environment == "lambda"
            assert config.storage.s3_bucket_name == "test-bucket"
            assert "--single-process" in config.webdriver.chrome_arguments
        finally:
            # 環境変数をクリア
            if "S3_BUCKET_NAME" in os.environ:
                del os.environ["S3_BUCKET_NAME"]


class TestConfigFactory:
    """設定ファクトリ関数のテスト"""

    def test_get_config_local(self):
        """ローカル環境設定取得が正しく動作することを確認"""
        config = get_config("local")

        assert isinstance(config, ApplicationConfig)
        assert config.environment == "local"

    def test_get_config_lambda(self):
        """Lambda環境設定取得が正しく動作することを確認"""
        config = get_config("lambda")

        assert isinstance(config, ApplicationConfig)
        assert config.environment == "lambda"

    def test_get_config_default(self):
        """デフォルト設定取得が正しく動作することを確認"""
        config = get_config()

        assert isinstance(config, ApplicationConfig)
        assert config.environment == "local"
