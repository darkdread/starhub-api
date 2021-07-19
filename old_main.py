import requests
import json
from datetime import datetime


class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


TESTING_POST = False
session = requests.Session()
date_formatted: str = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

headers: dict = {
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://login.starhubgee.com.sg",
    "referer": "https://login.starhubgee.com.sg/VCRLS/login.cgi?cb=https%3A%2F%2Flogin.starhubgee.com.sg%2Fsso%2Fssoredirect.jsp%3Fcallback%3Dhttps://www.starhub.com/content/starhub/en/dev/login/auth.html?back=https%3A%2F%2Fwww.starhub.com%2Fcontent%2Fstarhub1%2Fen%2Fpersonal.html"
}
form: dict = {
    "cberr": "https://login.starhubgee.com.sg/sso/loginerr.jsp?cb=https://login.starhubgee.com.sg/sso/ssoredirect.jsp?callback=https://www.starhub.com/content/starhub/en/dev/login/auth.html?back=https://www.starhub.com/content/starhub1/en/personal.html",
    "cb": "https://login.starhubgee.com.sg/sso/ssoredirect.jsp?callback=https://www.starhub.com/content/starhub/en/dev/login/auth.html?back=https://www.starhub.com/content/starhub1/en/personal.html",
    "vcid": "shsso",
    "view": "<!--view-->",
    "uid": "REMOVED@gmail.com@uuid",
    "domain": "uuid",
    "fake_uid": "REMOVED@gmail.com",
    "password": "REMOVED"
}

# https://postman-echo.com/post
# https://login.starhubgee.com.sg/eam/login2

endpoint: str = "https://login.starhubgee.com.sg/VCRLS/login.cgi?cb=https%3A%2F%2Flogin.starhubgee.com.sg%2Fsso%2Fssoredirect.jsp%3Fcallback%3Dhttps://www.starhub.com/content/starhub/en/dev/login/auth.html?back=https%3A%2F%2Fwww.starhub.com%2Fcontent%2Fstarhub1%2Fen%2Fpersonal.html"
resp = session.get(endpoint)

session.headers.update(headers)

# Login
endpoint = "https://postman-echo.com/post" if TESTING_POST else "https://login.starhubgee.com.sg/eam/login2"
resp = session.post(endpoint, data=form,
                    headers=headers)
if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError(resp.status_code)

if TESTING_POST:
    print(json.dumps(resp.json(), indent=4))
    exit(200)
else:
    f = open("starhub.html", "w")
    f.write(str(resp.content, 'utf-8'))
    f.close()

    # Get redirection params
    print(resp.headers)

# Main Page
endpoint = "https://secure.starhub.com/myaccountmgr/#/services/summary/"
resp = session.get(endpoint, headers=headers)

f = open("mobile.html", "w")
f.write(str(resp.content, 'utf-8'))
f.close()
