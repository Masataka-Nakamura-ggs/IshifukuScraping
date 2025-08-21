#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
価格抽出モジュール

HTML内から金価格を抽出する処理を提供します。
"""

import re
from abc import ABC, abstractmethod
from typing import Optional

from bs4 import BeautifulSoup

from ..config import ScrapingConfig


class PriceExtractor(ABC):
    """価格抽出の抽象基底クラス"""

    @abstractmethod
    def extract_price(self, html: str) -> Optional[int]:
        """
        HTMLから価格を抽出

        Args:
            html: 解析対象のHTML文字列

        Returns:
            Optional[int]: 抽出された価格（円/g）。見つからない場合はNone
        """
        pass


class GoldPriceExtractor(PriceExtractor):
    """金価格抽出クラス"""

    def __init__(self, config: Optional[ScrapingConfig] = None):
        """
        初期化

        Args:
            config: スクレイピング設定。Noneの場合はデフォルト設定を使用
        """
        self.config = config or ScrapingConfig()

    def extract_price(self, html: str) -> Optional[int]:
        """
        HTMLから金価格を抽出

        Args:
            html: 解析対象のHTML文字列

        Returns:
            Optional[int]: 抽出された金価格（円/g）。見つからない場合はNone
        """
        soup = BeautifulSoup(html, "html.parser")

        # テーブルから金価格を検索
        gold_price = self._extract_from_table(soup)

        # テーブルで見つからない場合は別の方法で検索
        if not gold_price:
            gold_price = self._extract_from_text_patterns(soup)

        return gold_price

    def _extract_from_table(self, soup: BeautifulSoup) -> Optional[int]:
        """
        テーブルから金価格を抽出

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[int]: 抽出された金価格。見つからない場合はNone
        """
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:  # 最低3列必要
                    first_cell_text = cells[0].get_text(strip=True)

                    # 「金」を含む行を検索（「金(g)」など）
                    if self._is_gold_row(first_cell_text):
                        # 2番目のセル（小売価格）を取得
                        price_text = cells[1].get_text(strip=True)
                        gold_price = self._extract_price_from_text(price_text)

                        # 2番目がダメなら3番目を試す
                        if not gold_price and len(cells) >= 3:
                            price_text = cells[2].get_text(strip=True)
                            gold_price = self._extract_price_from_text(price_text)

                        if gold_price:
                            return gold_price

        return None

    def _extract_from_text_patterns(self, soup: BeautifulSoup) -> Optional[int]:
        """
        テキストパターンから金価格を抽出

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[int]: 抽出された金価格。見つからない場合はNone
        """
        # 数値パターンを含む要素を検索（カンマ区切りの数値）
        price_patterns = [
            r"\d{1,2},\d{3}",  # 例: 17,550
            r"\d{2,3},\d{3}",  # 例: 175,500
            r"\d{1,3},\d{3}",  # 例: 1,750 または 17,550
        ]

        all_text = soup.get_text()

        for pattern in price_patterns:
            matches = re.findall(pattern, all_text)
            for match in matches:
                potential_price = self._extract_price_from_text(match)
                # 妥当な金価格の範囲をチェック
                if self._is_valid_price(potential_price):
                    return potential_price

        return None

    def _is_gold_row(self, text: str) -> bool:
        """
        テキストが金に関する行かどうかを判定

        Args:
            text: 判定対象のテキスト

        Returns:
            bool: 金に関する行の場合True
        """
        return "金" in text and ("g" in text or len(text) <= 5)

    def _extract_price_from_text(self, price_text: Optional[str]) -> Optional[int]:
        """
        価格テキストから数値を抽出

        Args:
            price_text: 価格テキスト

        Returns:
            Optional[int]: 抽出された価格。抽出できない場合はNone
        """
        if not price_text:
            return None

        # まず括弧内の部分を除去 (例: "+117" や "-50" など)
        cleaned_text = re.sub(r"\([^)]*\)", "", price_text.strip())

        # 数値パターンを検索（カンマ区切りまたは連続数字）
        # カンマ区切りの数値を優先
        match = re.search(r"(\d{1,3}(?:,\d{3})+)", cleaned_text)
        if match:
            price_str = match.group(1)
            # カンマを除去
            clean_price = price_str.replace(",", "")
            try:
                return int(clean_price)
            except ValueError:
                return None

        # カンマ区切りが見つからない場合は連続する数字を検索
        match = re.search(r"(\d+)", cleaned_text)
        if match:
            price_str = match.group(1)
            try:
                return int(price_str)
            except ValueError:
                return None

        return None

    def _is_valid_price(self, price: Optional[int]) -> bool:
        """
        価格が妥当な範囲内かチェック

        Args:
            price: チェック対象の価格

        Returns:
            bool: 妥当な価格の場合True
        """
        if price is None:
            return False

        return self.config.min_valid_price <= price <= self.config.max_valid_price


def extract_price_from_text(price_text: Optional[str]) -> Optional[int]:
    """
    価格テキストから数値を抽出（後方互換性のための関数）

    Args:
        price_text: 価格テキスト

    Returns:
        Optional[int]: 抽出された価格。抽出できない場合はNone
    """
    extractor = GoldPriceExtractor()
    return extractor._extract_price_from_text(price_text)


def create_price_extractor(config: Optional[ScrapingConfig] = None) -> PriceExtractor:
    """
    価格抽出器のファクトリ関数

    Args:
        config: スクレイピング設定

    Returns:
        PriceExtractor: 価格抽出器インスタンス
    """
    return GoldPriceExtractor(config)
