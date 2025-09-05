#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石福金属興業スクレイピングライブラリ

リファクタリングされた石福金属興業から金価格を取得するためのライブラリ
"""

from .config import (
    ApplicationConfig,
    ScrapingConfig,
    StorageConfig,
    WebDriverConfig,
    get_config,
    get_scraping_config,
    get_storage_config,
    get_webdriver_config,
)
from .models import ProductPrice
from .scraping import (
    ChromeDriverFactory,
    GoldPriceExtractor,
    HTMLParser,
    LambdaChromeDriverFactory,
    PriceExtractor,
    WebDriverFactory,
    WebDriverManager,
    create_html_parser,
    create_price_extractor,
    create_webdriver_factory,
    create_webdriver_manager,
    extract_price_from_text,
)
from .storage import (
    CSVStorage,
    DataStorage,
    LegacyCSVHandler,
    create_csv_storage,
    create_empty_csv,
    create_legacy_csv_handler,
    save_to_csv,
)
from .utils import (
    get_current_datetime,
    get_current_datetime_string,
    get_filename_date_string,
    log_error,
    log_info,
    setup_lambda_logging,
    setup_logging,
)

# バージョン情報
__version__ = "2.0.0"
__author__ = "Ishifuku Scraping Project"

__all__ = [
    # バージョン情報
    "__version__",
    "__author__",
    # 設定関連
    "ApplicationConfig",
    "ScrapingConfig",
    "WebDriverConfig",
    "StorageConfig",
    "get_config",
    "get_scraping_config",
    "get_webdriver_config",
    "get_storage_config",
    # スクレイピング関連
    "WebDriverFactory",
    "ChromeDriverFactory",
    "LambdaChromeDriverFactory",
    "WebDriverManager",
    "PriceExtractor",
    "GoldPriceExtractor",
    "HTMLParser",
    "create_webdriver_factory",
    "create_webdriver_manager",
    "create_price_extractor",
    "create_html_parser",
    "extract_price_from_text",
    # ストレージ関連
    "DataStorage",
    "CSVStorage",
    "LegacyCSVHandler",
    "create_csv_storage",
    "create_legacy_csv_handler",
    "save_to_csv",
    "create_empty_csv",
    # モデル
    "ProductPrice",
    # ユーティリティ関連
    "get_current_datetime",
    "get_current_datetime_string",
    "get_filename_date_string",
    "setup_logging",
    "setup_lambda_logging",
    "log_info",
    "log_error",
]
