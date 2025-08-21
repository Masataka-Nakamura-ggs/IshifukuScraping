#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石福金属興業ネットショップから金の小売価格を取得するスクリプト

このスクリプトは以下の処理を行います：
1. 石福金属興業のWebサイトにアクセス
2. 「本日の小売価格」ページに遷移
3. 金の小売価格を抽出
4. CSVファイルに保存
"""

import csv
import datetime
import logging
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def setup_logging():
    """ログ設定を初期化（日時ローテーション）"""
    # logsフォルダが存在しない場合は作成
    os.makedirs('logs', exist_ok=True)
    
    # 現在の日付を取得してログファイル名に使用
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    
    # エラーログ用（従来通り）
    error_log_filename = f'logs/scraping_error_{current_date}.log'
    
    # 実行ログ用（新規追加）
    info_log_filename = f'logs/scraping_info_{current_date}.log'
    
    # ログ設定をクリア
    logging.getLogger().handlers.clear()
    
    # エラーログ設定
    error_handler = logging.FileHandler(error_log_filename, mode='a', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # 実行ログ設定
    info_handler = logging.FileHandler(info_log_filename, mode='a', encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # ルートロガーに設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)


def get_current_datetime():
    """現在の日時を取得"""
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
    date_for_filename = now.strftime('%Y%m%d')
    return date_str, datetime_str, date_for_filename


def create_empty_csv(filename):
    """空のCSVファイルを作成"""
    try:
        # resultフォルダが存在しない場合は作成
        os.makedirs('result', exist_ok=True)
        
        # resultフォルダ内にファイルを作成
        filepath = os.path.join('result', filename)
        with open(filepath, 'w', encoding='utf-8'):
            pass  # 空ファイルを作成
        print(f"空のCSVファイルを作成しました: {filepath}")
    except Exception as e:
        logging.error(f"空ファイル作成エラー: {e}")


def extract_price_from_text(price_text):
    """価格テキストから数値を抽出"""
    if not price_text:
        return None
    
    # まず括弧内の部分を除去 (例: "+117" や "-50" など)
    cleaned_text = re.sub(r'\([^)]*\)', '', price_text.strip())
    
    # カンマや空白などの数値以外の文字を除去（ただし最初の数値部分のみ）
    # 例: "17,530" -> "17530"
    match = re.search(r'(\d{1,3}(?:,\d{3})*)', cleaned_text)
    if match:
        price_str = match.group(1)
        # カンマを除去
        clean_price = price_str.replace(',', '')
        try:
            return int(clean_price)
        except ValueError:
            return None
    
    return None


def scrape_gold_price():
    """石福金属興業から金の価格を取得（Selenium使用）"""
    driver = None
    try:
        # Chrome オプションを設定
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # ヘッドレスモード
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # WebDriverを初期化
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("石福金属興業のトップページにアクセス中...")
        
        # トップページにアクセス
        top_url = "https://www.ishifukushop.com/"
        driver.get(top_url)
        
        # ページが読み込まれるまで待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 価格ページのリンクを探す
        price_link = None
        
        # 複数のパターンでリンクを検索
        link_patterns = [
            "//a[contains(text(), '本日の小売価格')]",
            "//a[contains(text(), '小売価格')]",
            "//a[contains(text(), '相場')]",
            "//a[contains(text(), '金相場')]",
            "//a[contains(@href, 'price')]",
            "//a[contains(@href, 'rate')]"
        ]
        
        for pattern in link_patterns:
            try:
                elements = driver.find_elements(By.XPATH, pattern)
                if elements:
                    price_link = elements[0].get_attribute('href')
                    break
            except:
                continue
        
        # 直接価格ページにアクセス（リンクが見つからない場合）
        if not price_link:
            price_link = "https://retail.ishifuku-kinzoku.co.jp/price/"
        
        print(f"価格ページにアクセス中: {price_link}")
        
        # 価格ページに移動
        driver.get(price_link)
        
        # ページが完全に読み込まれるまで待機
        time.sleep(5)
        
        # JavaScriptが実行されるまで追加で待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # 追加の待機時間（価格データが動的に読み込まれる場合）
        time.sleep(3)
        
        # 現在のページのHTMLを取得
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 金の価格を含むテーブル行を探す
        gold_price = None
        
        # テーブル内で「金」を含む行を検索
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # 最低3列必要
                    first_cell_text = cells[0].get_text(strip=True)
                    
                    # 「金」を含む行を検索（「金(g)」など）
                    if '金' in first_cell_text and ('g' in first_cell_text or len(first_cell_text) <= 5):
                        # 2番目のセル（小売価格）を取得
                        price_text = cells[1].get_text(strip=True)
                        gold_price = extract_price_from_text(price_text)
                        
                        # 2番目がダメなら3番目を試す
                        if not gold_price and len(cells) >= 3:
                            price_text = cells[2].get_text(strip=True)
                            gold_price = extract_price_from_text(price_text)
                        
                        if gold_price:
                            print(f"金の小売価格を取得しました: {gold_price}円/g")
                            print(f"取得元テキスト: {price_text}")
                            break
            
            if gold_price:
                break
        
        # 別のアプローチ：価格データを直接検索
        if not gold_price:
            print("テーブルから価格が見つからないため、別の方法で検索中...")
            
            # 数値パターンを含む要素を検索（カンマ区切りの数値）
            price_patterns = [
                r'\d{1,2},\d{3}',  # 例: 17,550
                r'\d{2,3},\d{3}',  # 例: 175,500
                r'\d{1,3},\d{3}',  # 例: 1,750 または 17,550
            ]
            
            all_text = soup.get_text()
            for pattern in price_patterns:
                matches = re.findall(pattern, all_text)
                for match in matches:
                    potential_price = extract_price_from_text(match)
                    # 妥当な金価格の範囲をチェック（10,000～30,000円/g）
                    if potential_price and 10000 <= potential_price <= 30000:
                        print(f"価格候補を発見: {potential_price}円/g (元テキスト: {match})")
                        if not gold_price:  # 最初に見つかった妥当な価格を使用
                            gold_price = potential_price
        
        if not gold_price:
            # デバッグ情報を出力
            print("=== デバッグ情報 ===")
            print("ページタイトル:", soup.find('title').get_text() if soup.find('title') else "なし")
            
            tables = soup.find_all('table')
            print(f"テーブル数: {len(tables)}")
            
            for i, table in enumerate(tables):
                print(f"\n--- テーブル {i+1} ---")
                rows = table.find_all('tr')
                for j, row in enumerate(rows[:3]):  # 最初の3行のみ
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"行{j+1}: {cell_texts}")
            
            raise Exception("金の小売価格が見つかりません")
        
        return gold_price
        
    except Exception as e:
        raise Exception(f"スクレイピングエラー: {e}")
    finally:
        if driver:
            driver.quit()


def save_to_csv(date_str, gold_price, datetime_str, filename):
    """CSVファイルに価格データを保存"""
    try:
        # resultフォルダが存在しない場合は作成
        os.makedirs('result', exist_ok=True)
        
        # resultフォルダ内にファイルを作成
        filepath = os.path.join('result', filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([date_str, gold_price, datetime_str])
        print(f"データをCSVファイルに保存しました: {filepath}")
    except Exception as e:
        raise Exception(f"CSV保存エラー: {e}")


def main():
    """メイン処理"""
    # ログ設定を初期化
    setup_logging()
    
    # 現在の日時を取得
    date_str, datetime_str, date_for_filename = get_current_datetime()
    
    # CSVファイル名を生成
    csv_filename = f"ishihuku-gold-{date_for_filename}.csv"
    
    try:
        print("石福金属興業から金の価格を取得します...")
        logging.info("スクレイピング処理を開始")
        
        # 金の価格を取得
        gold_price = scrape_gold_price()
        
        # CSVファイルに保存
        save_to_csv(date_str, gold_price, datetime_str, csv_filename)
        
        print(f"処理が正常に完了しました。")
        print(f"取得日時: {datetime_str}")
        print(f"金の小売価格: {gold_price}円/g")
        print(f"保存ファイル: {csv_filename}")
        
        # 成功ログを記録
        logging.info(f"スクレイピング処理が正常に完了 - 価格: {gold_price}円/g, ファイル: {csv_filename}")
        
    except Exception as e:
        # エラーをログに記録
        error_message = f"エラーが発生しました: {e}"
        logging.error(error_message)
        print(error_message)
        
        # 空のCSVファイルを作成
        create_empty_csv(csv_filename)
        
        # 正常終了（終了コード0）
        print("エラー処理が完了しました。")


if __name__ == "__main__":
    main()
