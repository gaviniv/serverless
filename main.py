import os
from datetime import datetime

import pymysql
import requests

from email_template import email_body

MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DB = os.environ.get("MYSQL_DB")
MYSQL_HOST = os.environ.get("MYSQL_HOST")

MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")


# Global variable to store the database connection
db_connection = None


def get_database_connection():
    global db_connection
    if db_connection is None:
        db_connection = pymysql.connect(
            host=os.environ.get("MYSQL_HOST"),
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DB"),
        )
    return db_connection


def update_database(email):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(f"UPDATE user SET email_sent_time = {current_time}, verified = {False} WHERE email = {email}")
    connection.commit()


def send_email(email):
    recipient_name = email.split("@")[0]
    verification_link = f"http://ngavini.me:8000/v1/verify_user?email={email}"
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": f"hello@{MAILGUN_DOMAIN}",
        "to": email,
        "subject": "Email Verification",
        "text": email_body.format(
            recipient=recipient_name,
            domain_name=MAILGUN_DOMAIN,
            verification_link=verification_link
        )
    }
    response = requests.post(url, auth=auth, data=data)
    if response.status_code == 200:
        print("Email sent successfully")
    else:
        print(f"Failed to send email: {response.text}")


def process_message(email):
    try:
        #send_email(email)
        update_database(email)
    except Exception as e:
        print(f"Error processing message: {e}")


def pubsub_listener(event, context):
    email_id = event.get('data', {}).get('emailId')
    if email_id:
        process_message(email_id)
    else:
        print(f"no email found, payload: {event}")


# Entry point
if __name__ == "__main__":
    event = {
        "data":  {
            "emailId": "gavini.n@northeastern.edu"
        }
    }
    pubsub_listener(event, None)
