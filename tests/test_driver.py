#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebDriverモジュールのテスト
"""

from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.common.by import By

from src.ishifuku.config import WebDriverConfig
from src.ishifuku.scraping.driver import (
    ChromeDriverFactory,
    LambdaChromeDriverFactory,
    WebDriverManager,
    create_webdriver_factory,
    create_webdriver_manager,
)


class TestWebDriverConfig:
    """WebDriverConfigのテスト（追加）"""

    def test_custom_chrome_arguments(self):
        """カスタムChrome引数の設定を確認"""
        config = WebDriverConfig(
            headless=False, window_size="1280,720", user_agent="Custom Agent"
        )

        assert "--headless" not in config.chrome_arguments
        assert "--window-size=1280,720" in config.chrome_arguments
        assert "--user-agent=Custom Agent" in config.chrome_arguments


class TestChromeDriverFactory:
    """ChromeDriverFactoryのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.config = WebDriverConfig()
        self.factory = ChromeDriverFactory(self.config)

    def test_initialization(self):
        """初期化が正しく動作することを確認"""
        assert self.factory.config == self.config

    def test_initialization_default_config(self):
        """デフォルト設定での初期化を確認"""
        factory = ChromeDriverFactory()

        assert factory.config is not None
        assert isinstance(factory.config, WebDriverConfig)

    @patch("src.ishifuku.scraping.driver.webdriver.Chrome")
    @patch("src.ishifuku.scraping.driver.ChromeDriverManager")
    @patch("src.ishifuku.scraping.driver.Service")
    def test_create_driver_success(
        self, mock_service, mock_driver_manager, mock_chrome
    ):
        """WebDriver作成成功ケースを確認"""
        # モックの設定
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance

        # テスト実行
        driver = self.factory.create_driver()

        # 検証
        assert driver == mock_driver_instance
        mock_service.assert_called_once_with("/path/to/chromedriver")
        mock_chrome.assert_called_once()
        mock_driver_instance.set_page_load_timeout.assert_called_once_with(30)

    @patch("src.ishifuku.scraping.driver.webdriver.Chrome")
    @patch("src.ishifuku.scraping.driver.ChromeDriverManager")
    def test_create_driver_failure(self, mock_driver_manager, mock_chrome):
        """WebDriver作成失敗ケースを確認"""
        # エラーを発生させる
        mock_chrome.side_effect = Exception("Driver creation failed")

        # テスト実行
        with pytest.raises(Exception, match="WebDriver作成エラー"):
            self.factory.create_driver()

    def test_create_chrome_options(self):
        """Chromeオプション作成を確認"""
        options = self.factory._create_chrome_options()

        # 基本的な引数が含まれることを確認
        options_list = [options.arguments[i] for i in range(len(options.arguments))]
        assert "--headless" in options_list
        assert "--no-sandbox" in options_list


class TestLambdaChromeDriverFactory:
    """LambdaChromeDriverFactoryのテスト"""

    def setup_method(self):
        self.config = WebDriverConfig()
        self.factory = LambdaChromeDriverFactory(self.config)

    @patch("src.ishifuku.scraping.driver.webdriver.Chrome")
    @patch("src.ishifuku.scraping.driver.LambdaChromeDriverFactory._find_executable")
    def test_create_driver_success(self, mock_find_exec, mock_chrome):
        """chromedriver/chrome が見つかった成功ケース"""
        mock_find_exec.side_effect = [
            "/opt/bin/chromedriver",
            "/opt/bin/chrome",
        ]
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance

        driver = self.factory.create_driver()

        assert driver == mock_driver_instance
        assert mock_find_exec.call_count == 2
        mock_chrome.assert_called_once()
        mock_driver_instance.set_page_load_timeout.assert_called_once_with(30)

    @patch("src.ishifuku.scraping.driver.webdriver.Chrome")
    @patch("src.ishifuku.scraping.driver.LambdaChromeDriverFactory._find_executable")
    def test_create_driver_failure_chromedriver_not_found(self, mock_find_exec, mock_chrome):
        """chromedriver が見つからず例外が発生するケース"""
        mock_find_exec.return_value = None

        with pytest.raises(Exception, match="Lambda WebDriver作成エラー: '/opt'内で'chromedriver'が見つかりません"):
            self.factory.create_driver()
        mock_chrome.assert_not_called()


class TestWebDriverManager:
    """WebDriverManagerのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.mock_factory = MagicMock()
        self.mock_driver = MagicMock()
        self.mock_factory.create_driver.return_value = self.mock_driver
        self.manager = WebDriverManager(self.mock_factory)

    def test_initialization(self):
        """初期化が正しく動作することを確認"""
        assert self.manager.factory == self.mock_factory
        assert self.manager.driver is None

    def test_get_driver_creates_new(self):
        """新しいWebDriverが作成されることを確認"""
        driver = self.manager.get_driver()

        assert driver == self.mock_driver
        assert self.manager.driver == self.mock_driver
        self.mock_factory.create_driver.assert_called_once()

    def test_get_driver_reuses_existing(self):
        """既存のWebDriverが再利用されることを確認"""
        # 最初の呼び出し
        driver1 = self.manager.get_driver()

        # 2回目の呼び出し
        driver2 = self.manager.get_driver()

        assert driver1 == driver2
        assert driver1 == self.mock_driver
        # ファクトリは1回だけ呼ばれる
        self.mock_factory.create_driver.assert_called_once()

    def test_navigate_to(self):
        """ページ遷移が正しく動作することを確認"""
        with (
            patch("src.ishifuku.scraping.driver.WebDriverWait") as mock_wait,
            patch("src.ishifuku.scraping.driver.time.sleep") as mock_sleep,
        ):

            # モックの設定
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance

            # テスト実行
            self.manager.navigate_to("https://example.com", wait_time=3)

            # 検証
            driver = self.manager.get_driver()
            driver.get.assert_called_once_with("https://example.com")
            mock_wait.assert_called_once()
            mock_sleep.assert_called_once_with(3)

    def test_get_page_source(self):
        """ページソース取得が正しく動作することを確認"""
        self.mock_driver.page_source = "<html>test</html>"

        source = self.manager.get_page_source()

        assert source == "<html>test</html>"
        # get_driver()が呼ばれてdriverが設定される
        assert self.manager.driver == self.mock_driver

    def test_wait_for_element(self):
        """要素待機が正しく動作することを確認"""
        with patch("src.ishifuku.scraping.driver.WebDriverWait") as mock_wait:
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance

            # テスト実行
            self.manager.wait_for_element(By.TAG_NAME, "table", timeout=15)

            # 検証
            mock_wait.assert_called_once()
            mock_wait_instance.until.assert_called_once()

    def test_find_element_by_xpath_success(self):
        """XPath要素検索成功ケースを確認"""
        # モックの設定
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "https://example.com"
        self.mock_driver.find_elements.return_value = [mock_element]

        # テスト実行
        href = self.manager.find_element_by_xpath("//a[@href]")

        # 検証
        assert href == "https://example.com"
        self.mock_driver.find_elements.assert_called_once_with(By.XPATH, "//a[@href]")
        mock_element.get_attribute.assert_called_once_with("href")

    def test_find_element_by_xpath_no_element(self):
        """XPath要素検索で要素が見つからない場合を確認"""
        self.mock_driver.find_elements.return_value = []

        href = self.manager.find_element_by_xpath("//a[@href]")

        assert href is None

    def test_find_element_by_xpath_exception(self):
        """XPath要素検索で例外が発生した場合を確認"""
        self.mock_driver.find_elements.side_effect = Exception("Element not found")

        href = self.manager.find_element_by_xpath("//a[@href]")

        assert href is None

    def test_close(self):
        """WebDriverクローズが正しく動作することを確認"""
        # driverを設定
        self.manager.get_driver()

        # クローズ実行
        self.manager.close()

        # 検証
        self.mock_driver.quit.assert_called_once()
        assert self.manager.driver is None

    def test_close_no_driver(self):
        """driverが未設定の場合のクローズを確認"""
        # クローズ実行（例外が発生しないことを確認）
        self.manager.close()

        # 検証
        assert self.manager.driver is None

    def test_context_manager(self):
        """コンテキストマネージャーが正しく動作することを確認"""
        with self.manager as manager:
            assert manager == self.manager
            # with文内でdriverが使用可能
            driver = manager.get_driver()
            assert driver == self.mock_driver

        # with文を抜けたらcloseが呼ばれる
        self.mock_driver.quit.assert_called_once()
        assert self.manager.driver is None


class TestWebDriverFactoryFunctions:
    """WebDriverファクトリ関数のテスト"""

    def test_create_webdriver_factory_local(self):
        """ローカル環境用ファクトリ作成を確認"""
        factory = create_webdriver_factory("local")

        assert isinstance(factory, ChromeDriverFactory)

    def test_create_webdriver_factory_lambda(self):
        """Lambda環境用ファクトリ作成を確認"""
        factory = create_webdriver_factory("lambda")

        assert isinstance(factory, LambdaChromeDriverFactory)

    def test_create_webdriver_factory_with_config(self):
        """カスタム設定でのファクトリ作成を確認"""
        config = WebDriverConfig(headless=False)
        factory = create_webdriver_factory("local", config)

        assert isinstance(factory, ChromeDriverFactory)
        assert factory.config == config

    def test_create_webdriver_manager_local(self):
        """ローカル環境用マネージャー作成を確認"""
        manager = create_webdriver_manager("local")

        assert isinstance(manager, WebDriverManager)
        assert isinstance(manager.factory, ChromeDriverFactory)

    def test_create_webdriver_manager_lambda(self):
        """Lambda環境用マネージャー作成を確認"""
        manager = create_webdriver_manager("lambda")

        assert isinstance(manager, WebDriverManager)
        assert isinstance(manager.factory, LambdaChromeDriverFactory)

    def test_create_webdriver_manager_with_config(self):
        """カスタム設定でのマネージャー作成を確認"""
        config = WebDriverConfig(headless=False)
        manager = create_webdriver_manager("local", config)

        assert isinstance(manager, WebDriverManager)
        assert manager.factory.config == config
