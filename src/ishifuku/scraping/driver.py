#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebDriverモジュール

Seleniumドライバーの管理と設定を提供します。
"""

import os
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
from ..utils import log_info


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
    """【ローカル環境用】のChromeDriverファクトリクラス"""

    def __init__(self, config: Optional[WebDriverConfig] = None):
        """
        初期化
        """
        self.config = config or WebDriverConfig()

    def create_driver(self) -> webdriver.Chrome:
        """
        ChromeDriverインスタンスを作成
        """
        try:
            chrome_options = self._create_chrome_options()
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise Exception(f"WebDriver作成エラー: {e}") from e

    def _create_chrome_options(self) -> Options:
        """
        Chromeオプションを作成
        """
        chrome_options = Options()
        for arg in self.config.chrome_arguments:
            chrome_options.add_argument(arg)
        return chrome_options


class LambdaChromeDriverFactory(ChromeDriverFactory):
    """【Lambda環境用】のChromeDriverファクトリクラス"""

    def _find_executable(self, name: str, search_path: str = "/opt") -> Optional[str]:
        """指定されたパスで実行可能ファイルを再帰的に検索する"""
        for root, dirs, files in os.walk(search_path):
            if name in files:
                path = os.path.join(root, name)
                if os.path.exists(path) and os.access(path, os.X_OK):
                    log_info(f"実行可能ファイルを発見: {path}")
                    return path
        return None

    def create_driver(self) -> webdriver.Chrome:
        """
        Lambda環境用ChromeDriverインスタンスを作成
        """
        try:
            log_info("Lambda用WebDriverの作成を開始...")
            chrome_options = self._create_chrome_options()

            # Lambda Layer内の実行可能ファイルを動的に検索
            log_info("chromedriverを/opt内で検索中...")
            chromedriver_path = self._find_executable("chromedriver")

            log_info("chrome or headless-chromiumを/opt内で検索中...")
            chrome_path = self._find_executable("chrome") or self._find_executable(
                "headless-chromium"
            )

            if not chromedriver_path:
                opt_content = (
                    str(os.listdir("/opt")) if os.path.exists("/opt") else "N/A"
                )
                raise FileNotFoundError(
                    f"'/opt'内で'chromedriver'が見つかりません。/optの内容: {opt_content}"
                )
            if not chrome_path:
                opt_content = (
                    str(os.listdir("/opt")) if os.path.exists("/opt") else "N/A"
                )
                raise FileNotFoundError(
                    f"'/opt'内で'chrome'または'headless-chromium'が見つかりません。/optの内容: {
                        opt_content
                    }"
                )

            chrome_options.binary_location = chrome_path
            service = Service(executable_path=chromedriver_path)

            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            log_info("Lambda用WebDriverの作成に成功しました")
            return driver

        except Exception as e:
            debug_message = f"Lambda WebDriver作成エラー: {e}"
            raise Exception(debug_message) from e


class WebDriverManager:
    """WebDriverの管理クラス"""

    def __init__(self, factory: WebDriverFactory):
        """
        初期化
        """
        self.factory = factory
        self.driver: Optional[webdriver.Chrome] = None

    def get_driver(self) -> webdriver.Chrome:
        """
        WebDriverインスタンスを取得
        """
        if self.driver is None:
            self.driver = self.factory.create_driver()
        return self.driver

    def navigate_to(self, url: str, wait_time: int = 5) -> None:
        """
        指定されたURLに遷移
        """
        driver = self.get_driver()
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(wait_time)

    def get_page_source(self) -> str:
        """
        現在のページのHTMLソースを取得
        """
        driver = self.get_driver()
        page_source = driver.page_source
        return str(page_source) if page_source is not None else ""

    def wait_for_element(self, by: By, value: str, timeout: int = 10) -> None:
        """
        要素の出現を待機
        """
        driver = self.get_driver()
        from typing import Tuple, cast

        locator: Tuple[str, str] = cast(Tuple[str, str], (by, value))
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

    def find_element_by_xpath(self, xpath: str) -> Optional[str]:
        """
        XPathで要素を検索してhref属性を取得
        """
        try:
            driver = self.get_driver()
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                href = elements[0].get_attribute("href")
                return str(href) if href else None
        except Exception:
            pass
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
    """
    factory = create_webdriver_factory(environment, config)
    return WebDriverManager(factory)
