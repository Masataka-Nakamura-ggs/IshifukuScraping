#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTMLパーサーモジュール

HTMLの解析と情報抽出を提供します。
"""

from typing import List, Optional

from bs4 import BeautifulSoup

from ..config import ScrapingConfig
from ..utils import log_error


class HTMLParser:
    """HTML解析クラス"""

    def __init__(self, config: Optional[ScrapingConfig] = None):
        """
        初期化

        Args:
            config: スクレイピング設定。Noneの場合はデフォルト設定を使用
        """
        self.config = config or ScrapingConfig()

    def parse(self, html: str) -> BeautifulSoup:
        """
        HTMLを解析してBeautifulSoupオブジェクトを作成

        Args:
            html: 解析対象のHTML文字列

        Returns:
            BeautifulSoup: 解析されたBeautifulSoupオブジェクト
        """
        return BeautifulSoup(html, "html.parser")

    def find_price_link_patterns(self, html: str) -> Optional[str]:
        """
        価格ページへのリンクを検索

        Args:
            html: 検索対象のHTML文字列

        Returns:
            Optional[str]: 見つかったリンクのURL。見つからない場合はNone
        """
        soup = self.parse(html)

        for pattern in self.config.link_patterns:
            # XPathパターンを簡単なテキスト検索に変換
            link = self._find_link_by_pattern(soup, pattern)
            if link:
                return link

        return None

    def _find_link_by_pattern(self, soup: BeautifulSoup, pattern: str) -> Optional[str]:
        """
        パターンに基づいてリンクを検索

        Args:
            soup: BeautifulSoupオブジェクト
            pattern: 検索パターン（簡略化されたXPath）

        Returns:
            Optional[str]: 見つかったリンクのURL。見つからない場合はNone
        """
        try:
            if "contains(text()," in pattern:
                # テキスト内容による検索
                text_content = self._extract_text_from_pattern(pattern)
                if text_content:
                    links = soup.find_all("a")
                    for link in links:
                        if text_content in link.get_text():
                            href = link.get("href")
                            if href:
                                return str(href)

            elif "contains(@href," in pattern:
                # href属性による検索
                href_content = self._extract_href_from_pattern(pattern)
                if href_content:
                    links = soup.find_all("a", href=lambda x: x and href_content in x)
                    if links:
                        href_val = links[0].get("href")
                        return str(href_val) if href_val else None

        except Exception as ex_inner:
            log_error(f"要素の取得に失敗しました: {ex_inner}", ex_inner)

        return None

    def _extract_text_from_pattern(self, pattern: str) -> Optional[str]:
        """
        パターンからテキスト内容を抽出

        Args:
            pattern: XPathパターン

        Returns:
            Optional[str]: 抽出されたテキスト内容
        """
        import re

        match = re.search(r"contains\(text\(\), ['\"]([^'\"]+)['\"]", pattern)
        return match.group(1) if match else None

    def _extract_href_from_pattern(self, pattern: str) -> Optional[str]:
        """
        パターンからhref内容を抽出

        Args:
            pattern: XPathパターン

        Returns:
            Optional[str]: 抽出されたhref内容
        """
        import re

        match = re.search(r"contains\(@href, ['\"]([^'\"]+)['\"]", pattern)
        return match.group(1) if match else None

    def extract_table_data(self, html: str) -> List[List[str]]:
        """
        HTMLからテーブルデータを抽出

        Args:
            html: 解析対象のHTML文字列

        Returns:
            List[List[str]]: テーブルデータのリスト
        """
        soup = self.parse(html)
        tables = soup.find_all("table")
        all_table_data = []

        for table in tables:
            rows = table.find_all("tr")
            table_data = []

            for row in rows:
                cells = row.find_all(["td", "th"])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                if cell_texts:  # 空でない行のみ追加
                    table_data.append(cell_texts)

            if table_data:
                all_table_data.extend(table_data)

        return all_table_data

    def get_page_title(self, html: str) -> Optional[str]:
        """
        ページタイトルを取得

        Args:
            html: 解析対象のHTML文字列

        Returns:
            Optional[str]: ページタイトル。見つからない場合はNone
        """
        soup = self.parse(html)
        title_element = soup.find("title")
        return title_element.get_text() if title_element else None

    def get_debug_info(self, html: str) -> dict:
        """
        デバッグ用の情報を取得

        Args:
            html: 解析対象のHTML文字列

        Returns:
            dict: デバッグ情報
        """
        soup = self.parse(html)

        # ページタイトル
        title = self.get_page_title(html)

        # テーブル情報
        tables = soup.find_all("table")
        table_info = []

        for i, table in enumerate(tables):
            rows = table.find_all("tr")
            table_rows = []

            for j, row in enumerate(rows[:3]):  # 最初の3行のみ
                cells = row.find_all(["td", "th"])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                table_rows.append(cell_texts)

            table_info.append(
                {
                    "table_index": i + 1,
                    "row_count": len(rows),
                    "sample_rows": table_rows,
                }
            )

        return {
            "page_title": title,
            "table_count": len(tables),
            "table_info": table_info,
        }


def create_html_parser(config: Optional[ScrapingConfig] = None) -> HTMLParser:
    """
    HTMLパーサーのファクトリ関数

    Args:
        config: スクレイピング設定

    Returns:
        HTMLParser: HTMLパーサーインスタンス
    """
    return HTMLParser(config)
