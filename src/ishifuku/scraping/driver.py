#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebDriverモジュール

Seleniumドライバーの管理と設定を提供します。
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from ..config import WebDriverConfig
from ..utils import log_error


class WebDriverFactory(ABC):
    """WebDriverファクトリの抽象基底クラス"""

    @abstractmethod
    def create_driver(self) -> webdriver.Chrome:
        """
        WebDriverインスタンスを作成

        Returns:
            webdriver.Chrome: ChromeDriverインスタンス
        """
        pass


class ChromeDriverFactory(WebDriverFactory):
    """ChromeDriverファクトリクラス"""

    def __init__(self, config: Optional[WebDriverConfig] = None):
        """
        初期化

        Args:
            config: WebDriver設定。Noneの場合はデフォルト設定を使用
        """
        self.config = config or WebDriverConfig()

    def create_driver(self) -> webdriver.Chrome:
        """
        ChromeDriverインスタンスを作成

        Returns:
            webdriver.Chrome: ChromeDriverインスタンス

        Raises:
            Exception: ドライバー作成に失敗した場合
        """
        try:
            # Chrome オプションを設定
            chrome_options = self._create_chrome_options()

            # WebDriverを初期化
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(
                service=service, options=chrome_options
            )  # type: ignore[call-arg]

            # タイムアウト設定
            driver.set_page_load_timeout(30)

            return driver

        except Exception as e:
            raise Exception(f"WebDriver作成エラー: {e}") from e

    def _create_chrome_options(self) -> Options:
        """
        Chromeオプションを作成

        Returns:
            Options: Chromeオプション
        """
        chrome_options = Options()

        # 設定された引数を追加
        for arg in self.config.chrome_arguments:
            chrome_options.add_argument(arg)

        return chrome_options


class LambdaChromeDriverFactory(ChromeDriverFactory):
    """Lambda環境用ChromeDriverファクトリクラス"""

    def create_driver(self) -> webdriver.Chrome:
        """
        Lambda環境用ChromeDriverインスタンスを作成

        Returns:
            webdriver.Chrome: ChromeDriverインスタンス

        Raises:
            Exception: ドライバー作成に失敗した場合
        """
        try:
            # Chrome オプションを設定（Lambda用追加設定）
            chrome_options = self._create_lambda_chrome_options()

            # Lambda環境では事前にインストールされたドライバーを使用
            driver = webdriver.Chrome(options=chrome_options)

            # タイムアウト設定
            driver.set_page_load_timeout(30)

            return driver

        except Exception as e:
            raise Exception(f"Lambda WebDriver作成エラー: {e}") from e

    def _create_lambda_chrome_options(self) -> Options:
        """
        Lambda環境用Chromeオプションを作成

        Returns:
            Options: Chromeオプション
        """
        chrome_options = super()._create_chrome_options()

        # Lambda固有の設定
        lambda_specific_args = [
            "--single-process",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
        ]

        for arg in lambda_specific_args:
            chrome_options.add_argument(arg)

        return chrome_options


class WebDriverManager:
    """WebDriverの管理クラス"""

    def __init__(self, factory: WebDriverFactory):
        """
        初期化

        Args:
            factory: WebDriverファクトリ
        """
        self.factory = factory
        self.driver: Optional[webdriver.Chrome] = None

    def get_driver(self) -> webdriver.Chrome:
        """
        WebDriverインスタンスを取得（作成済みでなければ作成）

        Returns:
            webdriver.Chrome: WebDriverインスタンス
        """
        if self.driver is None:
            self.driver = self.factory.create_driver()
        return self.driver

    def navigate_to(self, url: str, wait_time: int = 5) -> None:
        """
        指定されたURLに遷移

        Args:
            url: 遷移先URL
            wait_time: 待機時間（秒）
        """
        driver = self.get_driver()
        driver.get(url)

        # ページが読み込まれるまで待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 追加の待機時間
        time.sleep(wait_time)

    def get_page_source(self) -> str:
        """
        現在のページのHTMLソースを取得

        Returns:
            str: HTMLソース
        """
        driver = self.get_driver()
        page_source = driver.page_source
        return str(page_source) if page_source is not None else ""

    def wait_for_element(self, by: By, value: str, timeout: int = 10) -> None:
        """
        要素の出現を待機

        Args:
            by: 要素の検索方法
            value: 検索値
            timeout: タイムアウト時間（秒）
        """
        driver = self.get_driver()
        from typing import Tuple, cast

        locator: Tuple[str, str] = cast(Tuple[str, str], (by, value))
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

    def find_element_by_xpath(self, xpath: str) -> Optional[str]:
        """
        XPathで要素を検索してhref属性を取得

        Args:
            xpath: XPath文字列

        Returns:
            Optional[str]: href属性の値。見つからない場合はNone
        """
        try:
            driver = self.get_driver()
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                href = elements[0].get_attribute("href")
                return str(href) if href else None
        except Exception as ex_inner:
            log_error(
                f"XPathで要素を検索してhref属性を取得するのに失敗しました: {ex_inner}",
                ex_inner,
            )
        return None

    def close(self) -> None:
        """WebDriverを終了"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self) -> "WebDriverManager":
        """コンテキストマネージャー入口"""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """コンテキストマネージャー出口"""
        self.close()


def create_webdriver_factory(
    environment: str = "local", config: Optional[WebDriverConfig] = None
) -> WebDriverFactory:
    """
    WebDriverファクトリを作成

    Args:
        environment: 実行環境（"local" または "lambda"）
        config: WebDriver設定

    Returns:
        WebDriverFactory: WebDriverファクトリインスタンス
    """
    if environment == "lambda":
        return LambdaChromeDriverFactory(config)
    else:
        return ChromeDriverFactory(config)


def create_webdriver_manager(
    environment: str = "local", config: Optional[WebDriverConfig] = None
) -> WebDriverManager:
    """
    WebDriverマネージャーを作成

    Args:
        environment: 実行環境（"local" または "lambda"）
        config: WebDriver設定

    Returns:
        WebDriverManager: WebDriverマネージャーインスタンス
    """
    factory = create_webdriver_factory(environment, config)
    return WebDriverManager(factory)
