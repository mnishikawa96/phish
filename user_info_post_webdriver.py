import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import random
import string

# proxy_server = "http://172.16.105.35:8080"
proxy_server = False
iphone_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1"

# URLを取得する
with open('url.txt', 'r') as file:
    urls = [line.strip() for line in file.readlines()]

# ユーザ番号とパスワードをランダムに生成する関数
def generate_random_user(existing_users):
    ranges = [(2000000000, 4999999999), (6000000000, 9999999999)]
    while True:
        user_range = random.choice(ranges)
        user_id = str(random.randint(user_range[0], user_range[1]))
        if user_id not in existing_users:
            existing_users.add(user_id)
            return user_id

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def process_user(url, user, pw):
    chrome_options = Options()
    if proxy_server:
        chrome_options.add_argument(f'--proxy-server={proxy_server}')
    chrome_options.add_argument("--window-size=950,968")
    chrome_options.add_argument(f'user-agent={iphone_user_agent}')
    chrome_service = Service()

    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        browser.get(url)
        time.sleep(3)
        bt = browser.find_element(By.LINK_TEXT, "規制解除")
        if bt:
            bt.click()
        select_no = browser.find_element(By.ID, "txbCustNo")
        select_pw = browser.find_element(By.ID, "txbCustPws")
        select_no.send_keys(user)
        select_pw.send_keys(pw)
        submit = browser.find_element(By.CSS_SELECTOR, ".horizontal-actions > input:nth-child(1)")
        submit.click()
        time.sleep(30)
    finally:
        browser.quit()

def process_url(url, num_users):
    used_user_ids = set()  # 各URLごとにユーザIDを管理するセットを作成
    tasks = []

    for _ in range(num_users):
        user = generate_random_user(used_user_ids)
        pw = generate_random_password()
        print(user)
        process_user(url, user, pw)

def main():
    num_users = 10000  # 各URLに対して使用するユーザIDの数を指定
    for url in urls:
        process_url(url, num_users)

if __name__ == "__main__":
    main()
