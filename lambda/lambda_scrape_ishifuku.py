#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Lambda + Selenium Layer対応版: 石福金属興業金価格スクレイピング

このスクリプトはAWS Lambdaで実行するために最適化されています。
Chrome/ChromeDriverのLambda Layerが必要です。
"""

import csv
import datetime
import json
import logging
import os
import re
import time
from io import StringIO

import boto3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def lambda_handler(event, context):
    """
    Lambda関数のエントリーポイント

    Args:
        event: Lambda イベント
        context: Lambda コンテキスト

    Returns:
        dict: 実行結果
    """

    # Lambda環境用のロガー設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        logger.info("Lambda Selenium スクレイピング処理を開始")

        # 金価格を取得
        gold_price = scrape_gold_price_selenium()

        # 現在の日時を取得
        date_str, datetime_str, date_for_filename = get_current_datetime()

        # CSVデータを作成
        csv_data = create_csv_data(date_str, gold_price, datetime_str)

        # S3に保存
        s3_key = None
        if os.environ.get("S3_BUCKET"):
            s3_key = save_to_s3(csv_data, f"ishihuku-gold-{date_for_filename}.csv")

        # CloudWatch Logsに記録
        logger.info(
            f"スクレイピング処理が正常に完了 - 価格: {gold_price}円/g, ファイル: ishihuku-gold-{date_for_filename}.csv"
        )

        # 成功レスポンス
        response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(
                {
                    "message": "スクレイピング処理が正常に完了",
                    "status": "success",
                    "data": {
                        "date": date_str,
                        "gold_price": gold_price,
                        "datetime": datetime_str,
                        "filename": f"ishihuku-gold-{date_for_filename}.csv",
                        "s3_key": s3_key,
                    },
                    "csv_data": csv_data,
                },
                ensure_ascii=False,
            ),
        }

        return response

    except Exception as e:
        error_msg = str(e)
        logger.error(f"エラー: {error_msg}")

        # エラー時も空のCSVファイルをS3に保存
        try:
            date_str, _, date_for_filename = get_current_datetime()
            if os.environ.get("S3_BUCKET"):
                save_to_s3("", f"ishihuku-gold-{date_for_filename}.csv", is_error=True)
        except:
            pass

        # エラーレスポンス
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(
                {
                    "message": "スクレイピング処理でエラーが発生",
                    "status": "error",
                    "error": error_msg,
                },
                ensure_ascii=False,
            ),
        }


def scrape_gold_price_selenium():
    """
    Seleniumを使用して金価格を取得
    Lambda Layer内のChrome/ChromeDriverを使用

    Returns:
        int: 金の小売価格
    """
    driver = None
    try:
        # Chrome オプションを設定（Lambda最適化）
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--window-size=1280x1696")
        chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        chrome_options.add_argument("--data-path=/tmp/chrome-data")
        chrome_options.add_argument("--disk-cache-dir=/tmp/chrome-cache")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Lambda Layer内のChrome/ChromeDriverを使用
        chrome_options.binary_location = "/opt/chrome/chrome"

        # WebDriverを初期化
        service = Service("/opt/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)  # Lambda用に延長

        logging.info("WebDriver初期化完了")

        # 価格ページに直接アクセス
        price_url = "https://retail.ishifuku-kinzoku.co.jp/price/"
        logging.info(f"価格ページにアクセス中: {price_url}")

        driver.get(price_url)

        # ページが完全に読み込まれるまで待機
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # JavaScriptが実行されるまで追加で待機
        time.sleep(8)  # Lambda環境では長めに設定

        # テーブルが読み込まれるまで待機
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except:
            logging.warning("テーブル要素の待機がタイムアウト、処理を続行")

        # 追加の安全な待機時間
        time.sleep(5)

        # 現在のページのHTMLを取得
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        logging.info("ページソース取得完了")

        # 金の価格を抽出
        gold_price = extract_gold_price_from_soup(soup)

        if not gold_price:
            # デバッグ情報をログに出力
            logging.warning("=== デバッグ情報 ===")
            title = soup.find("title")
            if title:
                logging.info(f"ページタイトル: {title.get_text(strip=True)}")

            tables = soup.find_all("table")
            logging.info(f"見つかったテーブル数: {len(tables)}")

            for i, table in enumerate(tables[:2]):  # 最初の2つのテーブルのみ
                rows = table.find_all("tr")
                logging.info(f"テーブル {i+1}: {len(rows)} 行")
                for j, row in enumerate(rows[:3]):  # 最初の3行のみ
                    cells = row.find_all(["td", "th"])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    logging.info(f"  行{j+1}: {cell_texts}")

            raise Exception("金の小売価格が見つかりません")

        logging.info(f"金の小売価格を取得しました: {gold_price}円/g")
        return gold_price

    except Exception as e:
        raise Exception(f"Seleniumスクレイピングエラー: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("WebDriver終了完了")
            except:
                pass


def extract_gold_price_from_soup(soup):
    """
    BeautifulSoupから金価格を抽出

    Args:
        soup: BeautifulSoupオブジェクト

    Returns:
        int: 金価格、見つからない場合はNone
    """
    # テーブル内で「金」を含む行を検索
    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                first_cell_text = cells[0].get_text(strip=True)

                # 「金」を含む行を検索（「金(g)」など）
                if "金" in first_cell_text and (
                    "g" in first_cell_text or len(first_cell_text) <= 5
                ):
                    # 価格セルを順次チェック（2番目から）
                    for i in range(1, len(cells)):
                        price_text = cells[i].get_text(strip=True)
                        gold_price = extract_price_from_text(price_text)
                        if gold_price:
                            logging.info(
                                f"テーブルから価格抽出成功: {price_text} -> {gold_price}"
                            )
                            return gold_price

    # テーブルで見つからない場合の代替検索
    logging.info("テーブルから価格が見つからないため、代替検索を実行")

    # 数値パターンを含む要素を検索（カンマ区切りの数値）
    price_patterns = [
        r"\d{1,2},\d{3}",  # 例: 17,550
        r"\d{2,3},\d{3}",  # 例: 175,500
    ]

    all_text = soup.get_text()
    for pattern in price_patterns:
        matches = re.findall(pattern, all_text)
        for match in matches:
            potential_price = extract_price_from_text(match)
            # 妥当な金価格の範囲をチェック（10,000～30,000円/g）
            if potential_price and 10000 <= potential_price <= 30000:
                logging.info(f"代替検索で価格発見: {match} -> {potential_price}")
                return potential_price

    return None


def extract_price_from_text(price_text):
    """
    価格テキストから数値を抽出

    Args:
        price_text: 価格を含むテキスト

    Returns:
        int: 抽出された価格、失敗時はNone
    """
    if not price_text:
        return None

    # まず括弧内の部分を除去 (例: "+117" や "-50" など)
    cleaned_text = re.sub(r"\([^)]*\)", "", price_text.strip())

    # カンマ区切りの数値パターンを抽出
    match = re.search(r"(\d{1,3}(?:,\d{3})*)", cleaned_text)
    if match:
        price_str = match.group(1)
        # カンマを除去
        clean_price = price_str.replace(",", "")
        try:
            return int(clean_price)
        except ValueError:
            return None

    return None


def get_current_datetime():
    """
    現在の日時を取得

    Returns:
        tuple: (日付文字列, 日時文字列, ファイル名用日付)
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_for_filename = now.strftime("%Y%m%d")
    return date_str, datetime_str, date_for_filename


def create_csv_data(date_str, gold_price, datetime_str):
    """
    CSVデータを文字列として作成

    Args:
        date_str: 日付文字列
        gold_price: 金価格
        datetime_str: 日時文字列

    Returns:
        str: CSV形式の文字列
    """
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([date_str, gold_price, datetime_str])
    return output.getvalue()


def save_to_s3(csv_data, filename, is_error=False):
    """
    S3にCSVファイルを保存

    Args:
        csv_data: CSVデータ文字列
        filename: ファイル名
        is_error: エラー時のファイルかどうか

    Returns:
        str: S3キー
    """
    try:
        s3_client = boto3.client("s3")
        bucket_name = os.environ.get("S3_BUCKET")

        if not bucket_name:
            raise Exception("S3_BUCKET環境変数が設定されていません")

        # S3キーを設定
        folder = "error" if is_error else "data"
        s3_key = f"ishifuku-{folder}/{filename}"

        # メタデータを設定
        metadata = {
            "scraping-status": "error" if is_error else "success",
            "created-at": datetime.datetime.now().isoformat(),
        }

        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=csv_data,
            ContentType="text/csv",
            Metadata=metadata,
        )

        logging.info(f"S3に保存完了: s3://{bucket_name}/{s3_key}")
        return s3_key

    except Exception as e:
        logging.error(f"S3保存エラー: {e}")
        raise


# ローカル実行用（テスト）
if __name__ == "__main__":
    # 環境変数を設定（テスト用）
    os.environ["S3_BUCKET"] = "test-bucket"

    # Lambda関数を実行
    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2, ensure_ascii=False))
