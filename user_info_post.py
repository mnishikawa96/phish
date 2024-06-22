import asyncio
import nodriver as uc
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

async def process_user(url, user, pw):
    if proxy_server:
        browser = await uc.start(headless=False, browser_args=[f'--proxy-server={proxy_server}', "--window-size=550,968"])
    else:
        browser = await uc.start(headless=False, browser_args=["--window-size=950,968"])

    try:
        tab = await browser.get('data:,', new_tab=True)
        await tab.send(uc.cdp.emulation.set_user_agent_override(
            user_agent=iphone_user_agent,
            user_agent_metadata=None
        ))
        tab = await tab.get(url)
        await asyncio.sleep(3)
        bt = await tab.find("規制解除")
        if bt:
            await bt.click()
        select_no = await tab.select("#txbCustNo", timeout=30)
        select_pw = await tab.select("#txbCustPws", timeout=30)
        await select_no.send_keys(user)
        await select_pw.send_keys(pw)
        submit = await tab.select(".horizontal-actions > input:nth-child(1)")
        await submit.click()
        await asyncio.sleep(30)
    finally:
        await browser.close()

async def process_url(url, num_users):
    used_user_ids = set()  # 各URLごとにユーザIDを管理するセットを作成
    tasks = []

    for _ in range(num_users):
        user = generate_random_user(used_user_ids)
        pw = generate_random_password()
        print(user)
        tasks.append(asyncio.create_task(process_user(url, user, pw)))

    await asyncio.gather(*tasks)

async def main():
    num_users = 10000  # 各URLに対して使用するユーザIDの数を指定
    # TODO: これだとユーザを生成してからスタートになるため、先にファイルに投げるユーザIDを作成しておく方が良いかも
    tasks = []
    for url in urls:
        tasks.append(process_url(url, num_users))
    await asyncio.gather(*tasks)

uc.loop().run_until_complete(main())
