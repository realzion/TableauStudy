import requests
import warnings
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime

# 경고 무시
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# 로그 설정 (파일명에 현재 날짜 추가)
current_date = datetime.now().strftime('%Y-%m-%d')
log_filename = f"tableau_checklicensekey_log_{current_date}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def send_email():
    sender_email = "your_email@example.com"  # 보내는 사람 이메일
    receiver_email = "realzion00@naver.com"  # 받는 사람 이메일
    password = "your_email_password"  # 이메일 계정 비밀번호

    subject = "분석프로그램 라이센스 이슈 테스트"
    body = "라이센스키를 다시 넣으세요"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.example.com", 465) as server:  # 이메일 서버 주소 및 포트 설정
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logging.info("이메일 전송 성공")
        print("이메일 전송 성공")
    except Exception as e:
        logging.error(f"이메일 전송 중 오류 발생: {e}")
        print(f"이메일 전송 중 오류 발생: {e}")


def login_and_fetch_product_keys():
    login_url = "https://ip-10-108-17-3.us-west-2.compute.internal:8850/api/0.5/login"
    login_data = {
        "authentication": {
            "name": "tbadmin",
            "password": "tbadmin"
        }
    }

    try:
        login_response = requests.post(login_url, json=login_data, verify=False)
        login_response.raise_for_status()
        if 'AUTH_COOKIE' not in login_response.cookies:
            logging.error("Login failed: AUTH_COOKIE not found.")
            print("Login failed: AUTH_COOKIE not found.")
            return
        auth_cookie = login_response.cookies['AUTH_COOKIE']
        logging.info("Login successful, AUTH_COOKIE obtained.")
        print(f"Login successful, AUTH_COOKIE: {auth_cookie}")
    except requests.RequestException as e:
        logging.error(f"An error occurred during login: {e}")
        print(f"An error occurred during login: {e}")
        return

    product_keys_url = "https://ip-10-108-17-3.us-west-2.compute.internal:8850/api/0.5/licensing/productKeys"
    cookies = {"AUTH_COOKIE": auth_cookie}

    try:
        product_keys_response = requests.get(product_keys_url, cookies=cookies, verify=False)
        product_keys_response.raise_for_status()
        product_keys_data = product_keys_response.json()

        product_keys_data_items = product_keys_data['productKeys']['items']
        df = pd.DataFrame(product_keys_data_items)

        if df.empty:
            logging.warning("No product keys found. Sending email...")
            print("No product keys found. Sending email...")
            send_email()
        else:
            logging.info("Product Keys fetched successfully.")
            print("Product Keys DataFrame:")
            print(df)
    except requests.RequestException as e:
        logging.error(f"An error occurred while fetching product keys: {e}")
        print(f"An error occurred while fetching product keys: {e}")


if __name__ == "__main__":
    logging.info("Program started")
    login_and_fetch_product_keys()
    logging.info("Program finished")

