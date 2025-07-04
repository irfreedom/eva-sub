import requests
import json
import time
import os

# آدرس URL اندپوینت API
# نکته: این آدرس ممکن است نیاز به تغییر داشته باشد. من یک آدرس محتمل را قرار دادم.
API_URL = "https://api.evavpn.com/v1/user/servers"

# هدرهای ثابت درخواست
# نکته مهم: توکن Authorization تاریخ انقضا دارد. پس از مدتی باید آن را با توکن جدید جایگزین کنید.
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQ4OGUwYmFjLTE4YWYtNDkxMS1hODM5LTQ3M2M4MmE5MjdkYyIsImlhdCI6MTc1MTY1MjI3OSwiZXhwIjoxNzU0MjQ0Mjc5fQ.5fK26ONpBKJlr2rtKuat52Zk8AlYhYdp8j7P1iAOSy4",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "api.evavpn.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/4.9.2"
}

# بخش ثابت بدنه درخواست
BASE_BODY = {
  "d_t": "android",
  "d_id": "7f9c6d81-c852-4920-bdde-54ebbede4ddd"
}

# نام فایل خروجی
OUTPUT_FILE = "configs.txt"

def fetch_configs():
    """
    کانفیگ‌ها را از ۱ تا ۱۰۰ دریافت کرده و در یک لیست برمی‌گرداند.
    """
    valid_configs = []
    print("Starting to fetch configs...")

    # حلقه برای regionId از ۱ تا ۱۰۰
    for region_id in range(1, 101):
        try:
            # ساخت بدنه کامل درخواست برای هر regionId
            body = BASE_BODY.copy()
            body["regionId"] = region_id
            
            # تبدیل دیکشنری به رشته JSON
            json_body = json.dumps(body)
            
            # نکته: کتابخانه requests به طور خودکار Content-Length را محاسبه و تنظیم می‌کند
            print(f"Requesting config for Region ID: {region_id}")
            
            response = requests.post(API_URL, headers=HEADERS, data=json_body, timeout=20) # 20 ثانیه مهلت برای پاسخ
            
            # بررسی موفقیت آمیز بودن درخواست
            if response.status_code == 200:
                data = response.json()
                # بررسی اینکه خطا وجود نداشته باشد و محتوا موجود باشد
                if not data.get('isError') and data.get('content'):
                    config_url = data['content'].get('access_url')
                    if config_url:
                        print(f"  [SUCCESS] Found config for Region ID: {region_id}")
                        valid_configs.append(config_url)
                    else:
                        print(f"  [INFO] No 'access_url' found for Region ID: {region_id}")
                else:
                    # اگر isError برابر با True بود یا محتوایی وجود نداشت
                    error_message = data.get('content', 'Unknown error')
                    print(f"  [ERROR] API returned an error for Region ID {region_id}: {error_message}")
            else:
                print(f"  [HTTP ERROR] Failed to get data for Region ID {region_id}. Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"  [NETWORK ERROR] An error occurred for Region ID {region_id}: {e}")
        
        # انتظار به مدت ۱۰ ثانیه بین هر درخواست
        print("Waiting for 10 seconds...\n")
        time.sleep(10)

    return valid_configs

def save_configs_to_file(configs):
    """
    لیست کانفیگ‌ها را در فایل متنی ذخیره می‌کند.
    """
    # حذف فایل قبلی اگر وجود داشته باشد تا همیشه فایل جدید و به‌روز باشد
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for config in configs:
            f.write(config + "\n")
    
    print(f"\nSuccessfully saved {len(configs)} configs to {OUTPUT_FILE}")

if __name__ == "__main__":
    configs = fetch_configs()
    if configs:
        save_configs_to_file(configs)
    else:
        print("No valid configs were found. The output file will not be created or will be empty.")
