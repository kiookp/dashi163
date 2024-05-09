from flask import Flask, request, jsonify
import os
import re
import sqlite3
import time
import win32gui
import pyautogui
import ctypes
import pygetwindow as gw
app = Flask(__name__)


def find_str_in_list_full_string(list_str, find_str):
    for index, str in enumerate(list_str):
        if find_str in str:
            break
    return str


def find_continuous_data(string, number):
    result = re.findall(r"\b\d{" + number + "}\b", string)
    return result

def extract_verification_code(email_content):
    result = re.findall(r"\b\d{6}\b", email_content)
    return result[0] if result else None


def find_verification_code(type, email):
    mailbox_rootpath = 'D:\MailMasterData'
    retry_count = 0
    while retry_count < 10:
        # 等待5秒再刷新邮箱
        time.sleep(5)
        # 模拟按F2键刷新邮箱
        window_title = "网易邮箱大师"
        press_f2_in_window(window_title)

        email_name_list = os.listdir(mailbox_rootpath)
        email_dir_name = find_str_in_list_full_string(email_name_list, email)

        db_path = '{}\{}\search.db'.format(mailbox_rootpath, email_dir_name)
        sql = 'select * from Search_content'

        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute(sql)
            person_all = cur.fetchall()
            last_text = ''
            for data in person_all:
                if 'AWS' in data[1]:
                    verification_code = extract_verification_code(data[6])
                    if verification_code:
                        print('Found verification code for {}: {}'.format(email, verification_code))
                        return verification_code

            if last_text:
                print('Found verification code for {}: {}'.format(email, last_text))
                return last_text
            else:
                print('No verification code found for {}. Retrying...'.format(email))
        except Exception as e:
            print('Error finding verification code for {}: {}. Retrying...'.format(email, e))
        finally:
            cur.close()
            con.close()

        retry_count += 1

    # 如果已达到重试限制，则返回“未找到验证码”消息
    return None


def press_f2_in_window(window_title):

    hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
    if hwnd == 0:
        print(f"没有找到标题为 {window_title} 的窗口")
        return

    ctypes.windll.user32.SetForegroundWindow(hwnd)

    time.sleep(1)

    pyautogui.press('F2')


@app.route('/api/find_verification_code', methods = ['POST'])
def get_verification_code():
    type = request.json['type']
    email = request.json['email']
    verification_code = find_verification_code(type, email)
    if verification_code:
        response = {'verification_code': verification_code}
        return jsonify(response)
    else:
        return 'Verification code not found for {} after 10 retries'.format(email), 404


if __name__ == '__main__':
    app.run("0.0.0.0", 9988)
