#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スクレイピングモジュール

スクレイピング関連機能の公開インターフェース
"""

from .driver import (
    ChromeDriverFactory,
    LambdaChromeDriverFactory,
    WebDriverFactory,
    WebDriverManager,
    create_webdriver_factory,
    create_webdriver_manager,
)
from .extractor import (
    GoldPriceExtractor,
    PriceExtractor,
    create_price_extractor,
    extract_price_from_text,
)
from .parser import HTMLParser, create_html_parser

__all__ = [
    # driver
    "WebDriverFactory",
    "ChromeDriverFactory",
    "LambdaChromeDriverFactory",
    "WebDriverManager",
    "create_webdriver_factory",
    "create_webdriver_manager",
    # extractor
    "PriceExtractor",
    "GoldPriceExtractor",
    "create_price_extractor",
    "extract_price_from_text",
    # parser
    "HTMLParser",
    "create_html_parser",
]
