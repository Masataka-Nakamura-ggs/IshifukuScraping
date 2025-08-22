#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTMLパーサーモジュールのテスト
"""

from src.ishifuku.config import ScrapingConfig
from src.ishifuku.scraping.parser import HTMLParser, create_html_parser


class TestHTMLParser:
    """HTMLParserのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.parser = HTMLParser()

    def test_initialization(self):
        """初期化が正しく動作することを確認"""
        assert self.parser.config is not None
        assert isinstance(self.parser.config, ScrapingConfig)

    def test_initialization_with_config(self):
        """カスタム設定での初期化を確認"""
        config = ScrapingConfig(wait_time_short=1)
        parser = HTMLParser(config)

        assert parser.config == config
        assert parser.config.wait_time_short == 1

    def test_parse_basic_html(self):
        """基本的なHTML解析を確認"""
        html = "<html><body><h1>Test</h1></body></html>"
        soup = self.parser.parse(html)

        assert soup.find("h1").get_text() == "Test"

    def test_find_price_link_patterns_with_text_content(self):
        """テキスト内容によるリンク検索を確認"""
        html = """
        <html>
        <body>
            <a href="/price">本日の小売価格</a>
            <a href="/other">その他</a>
        </body>
        </html>
        """

        link = self.parser.find_price_link_patterns(html)
        assert link == "/price"

    def test_find_price_link_patterns_with_href_content(self):
        """href属性によるリンク検索を確認"""
        html = """
        <html>
        <body>
            <a href="/rate/today">レート情報</a>
            <a href="/other">その他</a>
        </body>
        </html>
        """

        link = self.parser.find_price_link_patterns(html)
        assert link == "/rate/today"

    def test_find_price_link_patterns_multiple_matches(self):
        """複数マッチした場合の最初の結果を確認"""
        html = """
        <html>
        <body>
            <a href="/price1">小売価格</a>
            <a href="/price2">本日の小売価格</a>
        </body>
        </html>
        """

        link = self.parser.find_price_link_patterns(html)
        # 実装では「本日の小売価格」（より具体的なもの）が優先される
        assert link == "/price2"

    def test_find_price_link_patterns_no_match(self):
        """マッチしない場合の処理を確認"""
        html = """
        <html>
        <body>
            <a href="/contact">お問い合わせ</a>
            <a href="/about">会社概要</a>
        </body>
        </html>
        """

        link = self.parser.find_price_link_patterns(html)
        assert link is None

    def test_extract_text_from_pattern(self):
        """パターンからテキスト抽出を確認"""
        pattern = "//a[contains(text(), '本日の小売価格')]"
        text = self.parser._extract_text_from_pattern(pattern)
        assert text == "本日の小売価格"

    def test_extract_text_from_pattern_single_quote(self):
        """シングルクォートパターンの処理を確認"""
        pattern = "//a[contains(text(), '小売価格')]"
        text = self.parser._extract_text_from_pattern(pattern)
        assert text == "小売価格"

    def test_extract_text_from_pattern_no_match(self):
        """マッチしないパターンの処理を確認"""
        pattern = "//div[contains(@class, 'test')]"
        text = self.parser._extract_text_from_pattern(pattern)
        assert text is None

    def test_extract_href_from_pattern(self):
        """パターンからhref抽出を確認"""
        pattern = "//a[contains(@href, 'price')]"
        href = self.parser._extract_href_from_pattern(pattern)
        assert href == "price"

    def test_extract_href_from_pattern_single_quote(self):
        """シングルクォートhrefパターンの処理を確認"""
        pattern = "//a[contains(@href, 'rate')]"
        href = self.parser._extract_href_from_pattern(pattern)
        assert href == "rate"

    def test_extract_href_from_pattern_no_match(self):
        """マッチしないhrefパターンの処理を確認"""
        pattern = "//div[contains(@id, 'test')]"
        href = self.parser._extract_href_from_pattern(pattern)
        assert href is None

    def test_extract_table_data_simple(self):
        """シンプルなテーブルデータ抽出を確認"""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <th>項目</th>
                    <th>価格</th>
                </tr>
                <tr>
                    <td>金(g)</td>
                    <td>17,530</td>
                </tr>
            </table>
        </body>
        </html>
        """

        table_data = self.parser.extract_table_data(html)
        expected = [["項目", "価格"], ["金(g)", "17,530"]]
        assert table_data == expected

    def test_extract_table_data_multiple_tables(self):
        """複数テーブルからのデータ抽出を確認"""
        html = """
        <html>
        <body>
            <table>
                <tr><td>Table1</td><td>Data1</td></tr>
            </table>
            <table>
                <tr><td>Table2</td><td>Data2</td></tr>
            </table>
        </body>
        </html>
        """

        table_data = self.parser.extract_table_data(html)
        expected = [["Table1", "Data1"], ["Table2", "Data2"]]
        assert table_data == expected

    def test_extract_table_data_empty_rows(self):
        """空行を含むテーブルの処理を確認"""
        html = """
        <html>
        <body>
            <table>
                <tr><td>Data1</td><td>Data2</td></tr>
                <tr></tr>
                <tr><td></td><td></td></tr>
                <tr><td>Data3</td><td>Data4</td></tr>
            </table>
        </body>
        </html>
        """

        table_data = self.parser.extract_table_data(html)
        expected = [["Data1", "Data2"], ["", ""], ["Data3", "Data4"]]
        assert table_data == expected

    def test_extract_table_data_no_tables(self):
        """テーブルが存在しない場合の処理を確認"""
        html = """
        <html>
        <body>
            <p>テーブルはありません</p>
        </body>
        </html>
        """

        table_data = self.parser.extract_table_data(html)
        assert table_data == []

    def test_get_page_title(self):
        """ページタイトル取得を確認"""
        html = """
        <html>
        <head>
            <title>石福金属興業</title>
        </head>
        <body></body>
        </html>
        """

        title = self.parser.get_page_title(html)
        assert title == "石福金属興業"

    def test_get_page_title_no_title(self):
        """タイトルが存在しない場合の処理を確認"""
        html = "<html><body></body></html>"

        title = self.parser.get_page_title(html)
        assert title is None

    def test_get_debug_info(self):
        """デバッグ情報取得を確認"""
        html = """
        <html>
        <head>
            <title>テストページ</title>
        </head>
        <body>
            <table>
                <tr><td>Row1Col1</td><td>Row1Col2</td></tr>
                <tr><td>Row2Col1</td><td>Row2Col2</td></tr>
                <tr><td>Row3Col1</td><td>Row3Col2</td></tr>
                <tr><td>Row4Col1</td><td>Row4Col2</td></tr>
            </table>
            <table>
                <tr><td>Table2Data</td></tr>
            </table>
        </body>
        </html>
        """

        debug_info = self.parser.get_debug_info(html)

        assert debug_info["page_title"] == "テストページ"
        assert debug_info["table_count"] == 2
        assert len(debug_info["table_info"]) == 2

        # 最初のテーブル情報
        table1_info = debug_info["table_info"][0]
        assert table1_info["table_index"] == 1
        assert table1_info["row_count"] == 4
        assert len(table1_info["sample_rows"]) == 3  # 最初の3行のみ
        assert table1_info["sample_rows"][0] == ["Row1Col1", "Row1Col2"]

        # 2番目のテーブル情報
        table2_info = debug_info["table_info"][1]
        assert table2_info["table_index"] == 2
        assert table2_info["row_count"] == 1

    def test_find_link_by_pattern_exception_handling(self):
        """例外処理のテスト"""
        # 不正なHTMLでもエラーにならないことを確認
        html = "<html><body><a>Invalid HTML</body></html>"

        link = self.parser.find_price_link_patterns(html)
        # 例外が発生せず、Noneが返されることを確認
        assert link is None


class TestHTMLParserFactory:
    """HTMLパーサーファクトリのテスト"""

    def test_create_html_parser_default(self):
        """デフォルト設定でのパーサー作成を確認"""
        parser = create_html_parser()

        assert isinstance(parser, HTMLParser)
        assert parser.config is not None

    def test_create_html_parser_with_config(self):
        """カスタム設定でのパーサー作成を確認"""
        config = ScrapingConfig(wait_time_short=2)
        parser = create_html_parser(config)

        assert isinstance(parser, HTMLParser)
        assert parser.config == config
        assert parser.config.wait_time_short == 2
