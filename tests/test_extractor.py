#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいアーキテクチャのテストファイル - 価格抽出モジュール
"""

from src.ishifuku.config import ScrapingConfig
from src.ishifuku.scraping.extractor import (
    GoldPriceExtractor,
    create_price_extractor,
    extract_price_from_text,
)


class TestGoldPriceExtractor:
    """GoldPriceExtractorのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.extractor = GoldPriceExtractor()

    def test_extract_price_from_table(self):
        """テーブルから価格を抽出できることを確認"""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>金(g)</td>
                    <td>17,530</td>
                    <td>買取価格</td>
                </tr>
            </table>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530

    def test_extract_price_from_table_third_column(self):
        """テーブルの3列目から価格を抽出できることを確認"""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>金(g)</td>
                    <td>説明</td>
                    <td>17,530</td>
                </tr>
            </table>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530

    def test_extract_price_with_parentheses(self):
        """括弧付きの価格を正しく抽出できることを確認"""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>金(g)</td>
                    <td>17,530(+100)</td>
                    <td>その他</td>
                </tr>
            </table>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530

    def test_extract_price_from_text_patterns(self):
        """テキストパターンから価格を抽出できることを確認"""
        html = """
        <html>
        <body>
            <div>
                <p>本日の金価格は 17,530 円/gです。</p>
            </div>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price == 17530

    def test_extract_price_not_found(self):
        """価格が見つからない場合にNoneを返すことを確認"""
        html = """
        <html>
        <body>
            <div>
                <p>価格情報はありません。</p>
            </div>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price is None

    def test_extract_price_invalid_range(self):
        """無効な範囲の価格を除外することを確認"""
        html = """
        <html>
        <body>
            <div>
                <p>価格: 5,000 円/g</p>  <!-- 最小値未満 -->
                <p>価格: 50,000 円/g</p>  <!-- 最大値超過 -->
            </div>
        </body>
        </html>
        """

        price = self.extractor.extract_price(html)
        assert price is None

    def test_is_gold_row(self):
        """金に関する行の判定が正しく動作することを確認"""
        extractor = GoldPriceExtractor()

        assert extractor._is_gold_row("金(g)")
        assert extractor._is_gold_row("金")
        assert not extractor._is_gold_row("銀(g)")
        assert not extractor._is_gold_row("プラチナ")

    def test_is_valid_price(self):
        """価格の妥当性判定が正しく動作することを確認"""
        extractor = GoldPriceExtractor()

        assert extractor._is_valid_price(15000)
        assert extractor._is_valid_price(10000)  # 最小値
        assert extractor._is_valid_price(30000)  # 最大値
        assert not extractor._is_valid_price(5000)  # 最小値未満
        assert not extractor._is_valid_price(50000)  # 最大値超過
        assert not extractor._is_valid_price(None)


class TestExtractPriceFromText:
    """extract_price_from_text関数のテスト"""

    def test_extract_simple_number(self):
        """シンプルな数値の抽出を確認"""
        assert extract_price_from_text("17530") == 17530

    def test_extract_comma_separated(self):
        """カンマ区切り数値の抽出を確認"""
        assert extract_price_from_text("17,530") == 17530

    def test_extract_with_parentheses(self):
        """括弧付き数値の抽出を確認"""
        assert extract_price_from_text("17,530(+100)") == 17530

    def test_extract_none_input(self):
        """None入力時の処理を確認"""
        assert extract_price_from_text(None) is None

    def test_extract_empty_string(self):
        """空文字入力時の処理を確認"""
        assert extract_price_from_text("") is None

    def test_extract_no_numbers(self):
        """数値が含まれない文字列の処理を確認"""
        assert extract_price_from_text("価格情報なし") is None

    def test_extract_invalid_format(self):
        """無効な形式の数値の処理を確認"""
        assert extract_price_from_text("abc123def") == 123


class TestPriceExtractorFactory:
    """価格抽出器ファクトリのテスト"""

    def test_create_price_extractor_default(self):
        """デフォルト設定での価格抽出器作成を確認"""
        extractor = create_price_extractor()

        assert isinstance(extractor, GoldPriceExtractor)
        assert extractor.config is not None

    def test_create_price_extractor_with_config(self):
        """カスタム設定での価格抽出器作成を確認"""
        config = ScrapingConfig(min_valid_price=5000, max_valid_price=50000)
        extractor = create_price_extractor(config)

        assert isinstance(extractor, GoldPriceExtractor)
        assert extractor.config.min_valid_price == 5000
        assert extractor.config.max_valid_price == 50000
