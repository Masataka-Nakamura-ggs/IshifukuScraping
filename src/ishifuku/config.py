#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理モジュール

アプリケーション全体で使用する設定値を一元管理します。
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ScrapingConfig:
    """スクレイピング関連の設定"""

    # URL設定
    base_url: str = "https://www.ishifukushop.com/"
    price_url: str = "https://retail.ishifuku-kinzoku.co.jp/price/"
    direct_price_url: str = "https://retail.ishifuku-kinzoku.co.jp/price/"

    # 待機時間設定（秒）
    wait_time_short: int = 3
    wait_time_medium: int = 5
    wait_time_long: int = 10
    page_load_timeout: int = 30

    # リトライ設定
    max_retries: int = 3
    retry_delay: int = 2

    # 価格範囲設定（円/g）
    min_valid_price: int = 10000
    max_valid_price: int = 30000

    # XPath パターン
    link_patterns: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """初期化後の処理"""
        if not self.link_patterns:
            self.link_patterns = [
                "//a[contains(text(), '本日の小売価格')]",
                "//a[contains(text(), '小売価格')]",
                "//a[contains(text(), '相場')]",
                "//a[contains(text(), '金相場')]",
                "//a[contains(@href, 'price')]",
                "//a[contains(@href, 'rate')]",
            ]


@dataclass
class WebDriverConfig:
    """WebDriver関連の設定"""

    # Chrome オプション
    headless: bool = True
    window_size: str = "1920,1080"
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )

    # Chrome引数
    chrome_arguments: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """初期化後の処理"""
        if not self.chrome_arguments:
            self.chrome_arguments = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
            ]

            if self.headless:
                self.chrome_arguments.append("--headless")

            if self.window_size:
                self.chrome_arguments.append(f"--window-size={self.window_size}")

            if self.user_agent:
                self.chrome_arguments.append(f"--user-agent={self.user_agent}")


@dataclass
class StorageConfig:
    """ストレージ関連の設定"""

    # ディレクトリ設定
    result_dir: str = "result"
    logs_dir: str = "logs"

    # ファイル名設定
    csv_filename_template: str = "ishihuku-gold-{date}.csv"
    log_filename_template: str = "scraping_{level}_{date}.log"

    # S3設定（Lambda用）
    s3_bucket_name: Optional[str] = None
    s3_key_prefix: str = "gold-prices/"

    def get_csv_filename(self, date_str: str) -> str:
        """CSVファイル名を生成"""
        return self.csv_filename_template.format(date=date_str)

    def get_log_filename(self, level: str, date_str: str) -> str:
        """ログファイル名を生成"""
        return self.log_filename_template.format(level=level, date=date_str)


@dataclass
class ApplicationConfig:
    """アプリケーション全体の設定"""

    # 環境設定
    environment: str = "local"  # local, lambda
    debug: bool = False

    # 個別設定
    scraping: ScrapingConfig = field(default_factory=lambda: ScrapingConfig())
    webdriver: WebDriverConfig = field(default_factory=lambda: WebDriverConfig())
    storage: StorageConfig = field(default_factory=lambda: StorageConfig())

    def __post_init__(self) -> None:
        """初期化後の処理"""
        # Lambda環境の場合の調整
        if self.environment == "lambda":
            self._configure_for_lambda()

    def _configure_for_lambda(self) -> None:
        """Lambda環境用の設定調整"""
        # S3バケット名を環境変数から取得
        self.storage.s3_bucket_name = os.getenv("S3_BUCKET_NAME")

        # Lambdaでは/tmpディレクトリのみ書き込み可能
        self.storage.result_dir = "/tmp/result"
        self.storage.logs_dir = "/tmp/logs"
        
        # Lambda用のWebDriver設定
        self.webdriver.chrome_arguments.extend(
            [
                "--single-process",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
            ]
        )


def get_config(environment: str = "local") -> ApplicationConfig:
    """環境に応じた設定を取得"""
    return ApplicationConfig(environment=environment)


def get_scraping_config() -> ScrapingConfig:
    """スクレイピング設定を取得（後方互換性）"""
    return ScrapingConfig()


def get_webdriver_config() -> WebDriverConfig:
    """WebDriver設定を取得（後方互換性）"""
    return WebDriverConfig()


def get_storage_config() -> StorageConfig:
    """ストレージ設定を取得（後方互換性）"""
    return StorageConfig()
