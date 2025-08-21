#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrape_ishifuku.py のスクレイピング機能テストファイル
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrape_ishifuku import scrape_gold_price


class TestScrapeGoldPrice:
    """scrape_gold_price関数のテスト"""
    
    @patch('scrape_ishifuku.ChromeDriverManager')
    @patch('scrape_ishifuku.webdriver.Chrome')
    @patch('scrape_ishifuku.WebDriverWait')
    @patch('scrape_ishifuku.BeautifulSoup')
    def test_scrape_gold_price_success(self, mock_soup, mock_wait, mock_chrome, mock_driver_manager):
        """スクレイピング成功のテスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        # ページソースのモック
        mock_driver.page_source = """
        <html>
            <body>
                <table>
                    <tr>
                        <td>金(g)</td>
                        <td>17,530(+117)</td>
                        <td>16,000(-50)</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        # BeautifulSoupのモック
        mock_table = MagicMock()
        mock_row = MagicMock()
        mock_cells = [
            MagicMock(),  # 金(g)
            MagicMock(),  # 17,530(+117)
            MagicMock()   # 16,000(-50)
        ]
        
        mock_cells[0].get_text.return_value = "金(g)"
        mock_cells[1].get_text.return_value = "17,530(+117)"
        mock_cells[2].get_text.return_value = "16,000(-50)"
        
        mock_row.find_all.return_value = mock_cells
        mock_table.find_all.return_value = [mock_row]
        
        mock_soup_instance = MagicMock()
        mock_soup_instance.find_all.return_value = [mock_table]
        mock_soup.return_value = mock_soup_instance
        
        # WebDriverWaitのモック
        mock_wait.return_value.until.return_value = True
        
        # テスト実行
        result = scrape_gold_price()
        
        # 結果の確認
        assert result == 17530
        
        # WebDriverが正しく呼ばれているか確認
        mock_driver.get.assert_called()
        mock_driver.quit.assert_called_once()
    
    @patch('scrape_ishifuku.ChromeDriverManager')
    @patch('scrape_ishifuku.webdriver.Chrome')
    def test_scrape_gold_price_network_error(self, mock_chrome, mock_driver_manager):
        """ネットワークエラーのテスト"""
        # ドライバーで例外発生をシミュレート
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Network timeout")
        
        # テスト実行
        with pytest.raises(Exception) as exc_info:
            scrape_gold_price()
        
        assert "スクレイピングエラー" in str(exc_info.value)
        
        # WebDriverが適切にクリーンアップされているか確認
        mock_driver.quit.assert_called_once()
    
    @patch('scrape_ishifuku.ChromeDriverManager')
    @patch('scrape_ishifuku.webdriver.Chrome')
    @patch('scrape_ishifuku.WebDriverWait')
    @patch('scrape_ishifuku.BeautifulSoup')
    def test_scrape_gold_price_no_data_found(self, mock_soup, mock_wait, mock_chrome, mock_driver_manager):
        """価格データが見つからない場合のテスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        mock_driver.page_source = "<html><body><p>No data</p></body></html>"
        
        # BeautifulSoupのモック（テーブルが見つからない）
        mock_soup_instance = MagicMock()
        mock_soup_instance.find_all.return_value = []  # テーブルなし
        mock_soup_instance.get_text.return_value = "No relevant data"
        mock_soup_instance.find.return_value = MagicMock()
        mock_soup_instance.find.return_value.get_text.return_value = "Test Page"
        mock_soup.return_value = mock_soup_instance
        
        # WebDriverWaitのモック
        mock_wait.return_value.until.return_value = True
        
        # テスト実行
        with pytest.raises(Exception) as exc_info:
            scrape_gold_price()
        
        assert "金の小売価格が見つかりません" in str(exc_info.value)
        mock_driver.quit.assert_called_once()
    
    @patch('scrape_ishifuku.ChromeDriverManager')
    @patch('scrape_ishifuku.webdriver.Chrome')
    @patch('scrape_ishifuku.WebDriverWait')
    @patch('scrape_ishifuku.BeautifulSoup')
    @patch('scrape_ishifuku.re.findall')
    def test_scrape_gold_price_fallback_search(self, mock_findall, mock_soup, mock_wait, mock_chrome, mock_driver_manager):
        """フォールバック検索のテスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        mock_driver.page_source = "<html><body><p>Gold price: 18,500 yen</p></body></html>"
        
        # BeautifulSoupのモック（テーブルから見つからない）
        mock_soup_instance = MagicMock()
        mock_soup_instance.find_all.return_value = []  # テーブルなし
        mock_soup_instance.get_text.return_value = "Gold price: 18,500 yen per gram"
        mock_soup.return_value = mock_soup_instance
        
        # WebDriverWaitのモック
        mock_wait.return_value.until.return_value = True
        
        # 正規表現のモック（フォールバック検索で価格を発見）
        mock_findall.return_value = ["18,500"]
        
        # テスト実行
        result = scrape_gold_price()
        
        # 結果の確認
        assert result == 18500
        mock_driver.quit.assert_called_once()


class TestSeleniumIntegration:
    """Selenium統合テスト"""
    
    @patch('scrape_ishifuku.scrape_gold_price')
    @patch('scrape_ishifuku.setup_logging')
    @patch('scrape_ishifuku.get_current_datetime')
    @patch('scrape_ishifuku.save_to_csv')
    def test_main_function_success(self, mock_save_csv, mock_get_datetime, mock_setup_logging, mock_scrape):
        """main関数の成功テスト"""
        # モックの設定
        mock_get_datetime.return_value = ("2025-08-21", "2025-08-21 15:30:45", "20250821")
        mock_scrape.return_value = 17530
        
        # main関数をインポートして実行
        from scrape_ishifuku import main
        
        with patch('builtins.print') as mock_print:
            main()
        
        # 各関数が適切に呼ばれているか確認
        mock_setup_logging.assert_called_once()
        mock_get_datetime.assert_called_once()
        mock_scrape.assert_called_once()
        mock_save_csv.assert_called_once_with(
            "2025-08-21", 17530, "2025-08-21 15:30:45", "ishihuku-gold-20250821.csv"
        )
        
        # 成功メッセージが出力されているか確認
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("処理が正常に完了しました" in call for call in print_calls)
    
    @patch('scrape_ishifuku.scrape_gold_price')
    @patch('scrape_ishifuku.setup_logging')
    @patch('scrape_ishifuku.get_current_datetime')
    @patch('scrape_ishifuku.create_empty_csv')
    @patch('scrape_ishifuku.logging')
    def test_main_function_error(self, mock_logging, mock_create_empty, mock_get_datetime, mock_setup_logging, mock_scrape):
        """main関数のエラーテスト"""
        # モックの設定
        mock_get_datetime.return_value = ("2025-08-21", "2025-08-21 15:30:45", "20250821")
        mock_scrape.side_effect = Exception("Network error")
        
        # main関数をインポートして実行
        from scrape_ishifuku import main
        
        with patch('builtins.print') as mock_print:
            main()
        
        # エラーハンドリングが適切に動作しているか確認
        mock_logging.error.assert_called_once()
        mock_create_empty.assert_called_once_with("ishihuku-gold-20250821.csv")
        
        # エラーメッセージが出力されているか確認
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("エラーが発生しました" in call for call in print_calls)
        assert any("エラー処理が完了しました" in call for call in print_calls)


if __name__ == "__main__":
    pytest.main([__file__])
