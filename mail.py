# !/usr/bin/env python
# coding=utf-8

import datetime
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt

MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_PORT = os.environ.get("MAIL_PORT")
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
MAIL_SENDER = os.environ.get("MAIL_SENDER")
# user@qq.com,user2@qq.com
MAIL_RECEIVER = os.environ.get("MAIL_RECEIVER", "").split(",")

START_URL = "https://github.com/ruanyf/weekly"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}

def send_email(subject, html_body):
    msg = MIMEMultipart()
    msg["From"] = MAIL_SENDER
    msg["To"] = ", ".join(MAIL_RECEIVER)
    msg["Subject"] = subject

    # Attach the HTML content
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL(MAIL_HOST, int(MAIL_PORT)) as server:
            # server.set_debuglevel(1)
            server.login(MAIL_USER, MAIL_PASS)
            server.sendmail(MAIL_SENDER, MAIL_RECEIVER, msg.as_string())
            print("Email sent successfully.")
            try:
                server.quit()
            except smtplib.SMTPServerDisconnected:
                pass  # Ignore disconnection errors
    except Exception as e:
        print(f"Error sending email: {e}")

@retry(stop=stop_after_attempt(3))
def get_mail_content():
    """
    获取邮件内容
    """
    resp = requests.get(START_URL, headers=HEADERS).text
    result = re.findall(r'<a href=\"(.*?issue-\d*\.md)\">(.*?)</a>', resp)
    url, num = result[0]

    readme_url = "https://github.com" + url
    readme_content = requests.get(readme_url, headers=HEADERS).text

    bs = BeautifulSoup(readme_content, "lxml").find("article")

    html = """
        <html lang="en">
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <div>
                <a href="{0}">阮一峰技术周刊{1} 📅</a></br></br>
                {2}
            <div>
        </body>
        </html>
    """
    return html.format(readme_url, num, bs)


def ruan_blog():
    if datetime.datetime.now().weekday() != 4:
        return

    content = get_mail_content()
    send_email("My Github Action mail Subscribe", content)


if __name__ == "__main__":
    ruan_blog()
