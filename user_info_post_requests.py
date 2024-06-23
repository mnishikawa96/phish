import requests
import random
import string
import json

# URLを取得する
with open('url.txt', 'r') as file:
    domains = [line.strip() for line in file.readlines()]

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

# 口座番号がないパターン(仮)
def post_request(url, user, pw):
    post_data = {
        "Origin": "ブランド名",
        "Val1": user,
        "Val2": pw,
        "Page": "login"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(post_data), headers=headers)
    print(response.json())

def process_domain(domain, num_users):
    used_user_ids = set()  # 各ドメインごとにユーザIDを管理するセットを作成
    url = f"https://{domain}/public/submit"

    for _ in range(num_users):
        user = generate_random_user(used_user_ids)
        pw = generate_random_password()
        print(f"User: {user}, Password: {pw}")
        post_request(url, user, pw)

def main():
    num_users = 10000  # 各ドメインに対して使用するユーザIDの数を指定
    for domain in domains:
        process_domain(domain, num_users)

if __name__ == "__main__":
    main()
