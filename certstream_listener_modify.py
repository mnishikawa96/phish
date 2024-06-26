import certstream
import json
import requests
from pymsteams import connectorcard
import json
from datetime import datetime, timedelta
import os
import time

# プロキシ設定
proxy_set = False
proxies = {
    "http": "",
    "https": ""
}

# 特定の文字列
target_string = "FTP"

# ファイル名を生成する関数
def generate_unique_filename(base_filename):
    counter = 1
    filename = base_filename
    while os.path.exists(filename):
        filename = f"{base_filename.rsplit('.', 1)[0]}_{counter}.txt"
        counter += 1
    return filename

# ファイルに出力するための関数
def write_to_file(data):
    try:
        filename = generate_unique_filename('certificates.txt')
        with open(filename, 'a') as f:
            f.write(json.dumps(data, indent=2))
            f.write("\n\n")
        print(f"Data written to file {filename}.")
    except Exception as e:
        print(f"Failed to write to file: {e}")

def print_callback(message, context):
    try:
        if message['message_type'] == "certificate_update":
            data = message['data']
            cert_chain = data['leaf_cert']
            subject = cert_chain['subject']
            issuer = cert_chain['issuer']
            all_domains = cert_chain.get('all_domains', [])
            not_before = cert_chain.get('not_before')

            # 現在の日時を取得
            current_time_utc = datetime.utcnow()
            current_time_jst = current_time_utc + timedelta(hours=9)

            # データ受信時間を取得（現在の時刻）
            received_time_utc = datetime.utcnow()
            received_time_jst = received_time_utc + timedelta(hours=9)

            # 証明書の有効開始日時を確認
            if not_before:
                # not_before は秒単位のタイムスタンプ
                not_before_date_utc = datetime.utcfromtimestamp(not_before)
                not_before_date_jst = not_before_date_utc + timedelta(hours=9)

                # 2024/06/24 以降に発行された証明書か確認
                if not_before_date_utc >= datetime(2024, 6, 24):
                    # 条件に合致するか確認
                    if (issuer.get('O') == "Let's Encrypt" and 
                        (issuer.get('CN') == "R10" or issuer.get('CN') == "R11") and
                            any(domain.count('.') == 2 and domain.endswith('.duckdns.org') for domain in all_domains)):
                        
                        # ドメインをhttps://形式に変換
                        urls = [f"https://{domain}" for domain in all_domains]
                        cert_info_with_urls = {
                            "subject": subject,
                            "issuer": issuer,
                            "all_domains": all_domains,
                            "urls": urls,
                            "not_before_utc": not_before_date_utc.isoformat(),
                            "not_before_jst": not_before_date_jst.isoformat(),
                            "received_time_utc": received_time_utc.isoformat(),
                            "received_time_jst": received_time_jst.isoformat(),
                            "current_time_utc": current_time_utc.isoformat(),
                            "current_time_jst": current_time_jst.isoformat()
                        }
                        
                        # 最初のURLを使用してコンテンツを取得
                        url_to_check = urls[0]
                        try:
                            if proxy_set:
                                response = requests.get(url_to_check, proxies=proxies, timeout=60)
                            else:
                                response = requests.get(url_to_check, timeout=60)
                                
                            content = response.text
                            if target_string in content:
                                write_to_file(cert_info_with_urls)
                                print("Certificate written to file.")
                            else:
                                pass
                        except requests.RequestException as e:
                            pass
                        
    except Exception as e:
        print(f"Error in callback: {e}")

def on_open():
    print("Connection successfully established!")

def on_error(exception):
    print(f"Exception in CertStreamClient! -> {exception}")

certstream.listen_for_events(print_callback, on_open=on_open, on_error=on_error, url='wss://certstream.calidog.io/')
