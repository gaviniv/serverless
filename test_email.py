import requests


def send_simple_message():
	res = requests.post("https://api.mailgun.net/v3/ngavini.me/messages",
						 auth=("api", "<API-KEY-HERE>"),
						 data={"from": "hello@ngavini.me",
							   "to": ["gavini.n@northeastern.edu"],
							   "subject": "Hello",
							   "text": "Testing some Mailgun awesomeness!"}
						 )
	return res


res = send_simple_message()
print(res.content)
