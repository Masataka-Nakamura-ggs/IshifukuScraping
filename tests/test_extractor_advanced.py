#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extractor.pyの追加テストケース - カバレッジ向上のため
"""

import pytest

from src.ishifuku.config import ScrapingConfig
from src.ishifuku.scraping.extractor import (
    GoldPriceExtractor,
    PriceExtractor,
    create_price_extractor,
    extract_price_from_text,
)


class TestGoldPriceExtractorAdvanced:
    """GoldPriceExtractorの高度なテストケース"""

    def setup_method(self):
        """テスト前の準備"""
        self.extractor = GoldPriceExtractor()

    def test_extract_from_table_complex_structure(self):
        """複雑なテーブル構造から価格を抽出"""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <th>商品</th>
                    <th>小売価格</th>
                    <th>備考</th>
                </tr>
                <tr>
                    <td>金(g)</td>
                    <td>17,530</td>
                    <td>前日比+50</td>
                </tr>
                <tr>
                    <td>銀(g)</td>
                    <td>230</td>
                    <td>前日比-5</td>
                </tr>
            </table>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530

    def test_extract_from_multiple_tables(self):
        """複数のテーブルがある場合の価格抽出"""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>銀(g)</td>
                    <td>230</td>
                </tr>
            </table>
            <table>
                <tr>
                    <td>金(g)</td>
                    <td>17,530</td>
                </tr>
            </table>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530

    def test_extract_from_table_with_insufficient_columns(self):
        """列数が不足している場合の処理"""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>金(g)</td>
                    <td>17,530</td>
                </tr>
                <tr>
                    <td>不完全な行</td>
                </tr>
            </table>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530  # 正常な行から価格を抽出

    def test_extract_with_gold_row_edge_cases(self):
        """金行判定のエッジケース"""
        # 金を含むが条件を満たさない行
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>金属製品の説明文がとても長い場合のテスト(金含む)</td>
                    <td>17,530</td>
                    <td>備考</td>
                </tr>
            </table>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        # テーブル内の金行判定は失敗するが、テキストパターンから価格が抽出される
        assert price == 17530

    def test_extract_price_from_text_patterns_multiple_patterns(self):
        """複数のパターンがマッチする場合のテスト"""
        html = """
        <html>
        <body>
            <div>
                <p>無効な価格: 5,000 円/g</p>  <!-- 最小値未満 -->
                <p>有効な価格: 17,530 円/g</p>  <!-- 有効 -->
                <p>無効な価格: 50,000 円/g</p>  <!-- 最大値超過 -->
            </div>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530  # 有効な価格のみ返される

    def test_extract_price_from_text_patterns_no_valid_matches(self):
        """すべてのパターンが無効な場合"""
        html = """
        <html>
        <body>
            <div>
                <p>無効な価格1: 5,000 円/g</p>  <!-- 最小値未満 -->
                <p>無効な価格2: 50,000 円/g</p>  <!-- 最大値超過 -->
            </div>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price is None

    def test_extract_price_from_text_with_different_number_patterns(self):
        """異なる数値パターンでのテスト"""
        test_cases = [
            ("99,999", 99999),  # 5桁
            ("1,000", 1000),  # 4桁
            ("100,000", 100000),  # 6桁
            ("9,999", 9999),  # 4桁（最小ケース）
        ]

        for html_text, expected in test_cases:
            html = f"""
            <html>
            <body>
                <p>価格: {html_text} 円/g</p>
            </body>
            </html>
            """

            # カスタム設定で範囲を広げる
            config = ScrapingConfig(min_valid_price=1000, max_valid_price=150000)
            extractor = GoldPriceExtractor(config)

            price = extractor.extract_price(html)
            assert price == expected

    def test_is_gold_row_detailed(self):
        """金行判定の詳細テスト"""
        extractor = GoldPriceExtractor()

        # 有効なケース（金 + g または文字数5以下）
        valid_cases = [
            "金(g)",
            "金",
            "金 g",
            "金/g",
            "金g",
        ]

        for case in valid_cases:
            assert extractor._is_gold_row(
                case
            ), f"'{case}' should be recognized as gold row"

        # 無効なケース
        invalid_cases = [
            "銀(g)",
            "プラチナ(g)",
            "金属製品の長い説明文がここに来る場合",  # 金は含むが長すぎる
            "金融商品について",  # 金は含むがgがなく長い
            "",
        ]

        for case in invalid_cases:
            assert not extractor._is_gold_row(
                case
            ), f"'{case}' should not be recognized as gold row"

    def test_extract_price_from_text_edge_cases(self):
        """価格テキスト抽出のエッジケース"""
        extractor = GoldPriceExtractor()

        test_cases = [
            # 括弧を含む複雑なケース
            ("17,530(+100)(-50)", 17530),
            ("17,530 (+変動)", 17530),
            # 複数の数値が含まれる場合
            ("前日比: 100 本日: 17,530 明日予想: 200", 17530),
            # カンマなしの数値
            ("17530", 17530),
            # 無効なパターン
            ("abc", None),
            ("", None),
            ("価格情報なし", None),
        ]

        for input_text, expected in test_cases:
            result = extractor._extract_price_from_text(input_text)
            assert (
                result == expected
            ), f"Input: {input_text}, Expected: {expected}, Got: {result}"

    def test_extract_price_from_text_regex_patterns(self):
        """正規表現パターンの詳細テスト"""
        extractor = GoldPriceExtractor()

        # カンマ区切り優先のテスト
        assert extractor._extract_price_from_text("17,530と12345") == 17530

        # カンマなし数値の抽出
        assert extractor._extract_price_from_text("価格12345円") == 12345

        # 先頭の数値を取得
        assert extractor._extract_price_from_text("12345と67890") == 12345

    def test_extract_from_table_exception_handling(self):
        """テーブル処理での例外ハンドリング"""
        # 不正な構造のHTMLでもエラーにならないことを確認
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>金(g)
                    <td>17,530
                </tr>
            </table>
        </body>
        </html>
        """

        # 例外が発生せず、何かしらの結果が返されることを確認
        price = self.extractor.extract_price(html)
        # BeautifulSoupは寛容なので、価格が抽出される可能性もある
        assert price is None or isinstance(price, int)

    def test_custom_config_with_different_price_ranges(self):
        """カスタム設定での価格範囲テスト"""
        # 広い範囲の設定
        config_wide = ScrapingConfig(min_valid_price=1000, max_valid_price=100000)
        extractor_wide = GoldPriceExtractor(config_wide)

        # 狭い範囲の設定
        config_narrow = ScrapingConfig(min_valid_price=15000, max_valid_price=20000)
        extractor_narrow = GoldPriceExtractor(config_narrow)

        html = """
        <html>
        <body>
            <div>価格: 17,530 円/g</div>
        </body>
        </html>
        """

        # 両方で有効
        assert extractor_wide.extract_price(html) == 17530
        assert extractor_narrow.extract_price(html) == 17530

        # 範囲外のテスト
        html_out_of_range = """
        <html>
        <body>
            <div>価格: 25,000 円/g</div>
        </body>
        </html>
        """

        # 広い範囲では有効、狭い範囲では無効
        assert extractor_wide.extract_price(html_out_of_range) == 25000
        assert extractor_narrow.extract_price(html_out_of_range) is None


class TestPriceExtractorAbstractBase:
    """PriceExtractor抽象クラスのテスト"""

    def test_price_extractor_is_abstract(self):
        """PriceExtractorが抽象クラスであることを確認"""
        with pytest.raises(TypeError):
            # 抽象クラスは直接インスタンス化できない
            PriceExtractor()


class TestEdgeCasesAndErrorHandling:
    """エッジケースとエラーハンドリングのテスト"""

    def test_extract_price_with_empty_html(self):
        """空のHTMLでの処理"""
        extractor = GoldPriceExtractor()

        empty_html_cases = [
            "",
            "<html></html>",
            "<html><body></body></html>",
            "   ",  # 空白のみ
        ]

        for html in empty_html_cases:
            price = extractor.extract_price(html)
            assert price is None

    def test_extract_price_with_malformed_html(self):
        """不正なHTMLでの処理"""
        extractor = GoldPriceExtractor()

        malformed_html_cases = [
            # 閉じタグ不足
            "<html><body><table><tr><td>金(g)<td>17,530</tr></table></body></html>",
            "金(g) 17,530",  # HTMLタグなし
            "<div>金(g)</div><span>17,530</span>",  # htmlタグなし
        ]

        for html in malformed_html_cases:
            # 例外が発生しないことを確認
            try:
                price = extractor.extract_price(html)
                assert price is None or isinstance(price, int)
            except Exception as e:
                pytest.fail(f"Exception should not be raised for malformed HTML: {e}")

    def test_performance_with_large_html(self):
        """大きなHTMLでのパフォーマンステスト"""
        extractor = GoldPriceExtractor()

        # 大量のダミーデータを含むHTML
        large_html = "<html><body>"
        large_html += "<table>" * 100  # 大量のテーブル
        for i in range(1000):
            large_html += f"<tr><td>ダミー{i}</td><td>{i}</td></tr>"
        large_html += "</table>" * 100

        # 実際の金価格データを最後に追加
        large_html += """
        <table>
            <tr>
                <td>金(g)</td>
                <td>17,530</td>
            </tr>
        </table>
        """
        large_html += "</body></html>"

        # タイムアウトしないことを確認
        import time

        start_time = time.time()
        price = extractor.extract_price(large_html)
        end_time = time.time()

        assert price == 17530
        assert end_time - start_time < 10.0  # 10秒以内に完了


class TestAdditionalFactoryAndUtilityFunctions:
    """ファクトリ関数とユーティリティ関数の追加テスト"""

    def test_extract_price_from_text_function_comprehensive(self):
        """extract_price_from_text関数の包括的テスト"""
        test_cases = [
            # 標準的なケース
            ("17,530", 17530),
            ("17530", 17530),
            # 特殊文字を含むケース
            ("¥17,530", 17530),
            ("$17,530", 17530),
            ("17,530円", 17530),
            # 複雑な括弧
            ("17,530(前日比+100)(税込)", 17530),
            # 前後に文字がある場合
            ("価格は17,530円です", 17530),
            ("本日の金価格17,530円/g(税抜)", 17530),
            # エラーケース
            ("価格未定", None),
            ("TBD", None),
            ("---", None),
        ]

        for input_text, expected in test_cases:
            result = extract_price_from_text(input_text)
            assert (
                result == expected
            ), f"Input: '{input_text}', Expected: {expected}, Got: {result}"

    def test_create_price_extractor_returns_correct_interface(self):
        """ファクトリ関数が正しいインターフェースを返すことを確認"""
        extractor = create_price_extractor()

        # PriceExtractorインターフェースを実装していることを確認
        assert isinstance(extractor, PriceExtractor)
        assert hasattr(extractor, "extract_price")
        assert callable(extractor.extract_price)

        # 実際にGoldPriceExtractorインスタンスであることを確認
        assert isinstance(extractor, GoldPriceExtractor)
