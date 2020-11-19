import sys
import os
import requests
import json
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")

parser = argparse.ArgumentParser(description="Starhub API processor.")
group = parser.add_argument_group("Login approach")
group.add_argument("--uid", dest="uid", action="store",
                   help="Username for Starhub")
group.add_argument("--pw", dest="pw", action="store",
                   help="Password for Starhub")
parser.add_argument("--save_utoken", dest="save_utoken", action="store",
                    help="Save utoken to file")
group = parser.add_argument_group("Utoken approach")
parser.add_argument("--utoken", dest="utoken", action="store",
                    help="Read utoken from argument")
parser.add_argument("--utoken_file", dest="utoken_file", action="store",
                    help="Read utoken from file")


args = parser.parse_args()

if ((args.uid is None or args.pw is None) and
   (args.utoken is None and args.utoken_file is None)):
    sys.exit("Please provide both uid and pw, or either"
             "utoken or utoken_file as an argument.")

if (args.utoken is not None and args.utoken_file is not None):
    sys.exit("Cannot have both utoken or utoken_file as an argument.")
elif (args.uid is not None and
      (args.utoken is not None or args.utoken_file is not None)):
    sys.exit("Cannot use both login and utoken approach at the same time.")

if (args.utoken_file is not None and not os.path.exists(args.utoken_file)):
    sys.exit("{args.utoken_file} does not exist.")


class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


class StarhubApi():

    def __init__(self):
        pass

    def get_vctk3_dict(self, uid, pw):
        driver = webdriver.Chrome('chromedriver.exe',
                                  chrome_options=chrome_options)
        driver.get('https://login.starhubgee.com.sg/VCRLS/login.cgi')

        uid_input = driver.find_element_by_css_selector('[name="loginform"] #fake_uid')
        uid_input.send_keys(uid)

        pw_input = driver.find_element_by_id('password')
        pw_input.send_keys(pw)
        pw_input.submit()

        driver.get('https://secure.starhub.com/myaccountmgr/#/')
        driver_cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
        driver.quit()

        out = {
            "vctk3": driver_cookies["vctk3"],
            "uid": driver_cookies["uid"]
        }

        return out

    def get_utoken(self, uid, vctk3):
        endpoint = "https://secure.starhub.com/myaccountmgr/essoLogin"
        cookies = {
            "uid": uid,
            "vctk3": vctk3
        }
        resp = requests.post(endpoint, cookies=cookies)

        if (resp.status_code != 200):
            raise ApiError(resp.status_code)

        return resp.json()["userDetails"]["utoken"]

    def get_mobile_overview(self, utoken):
        endpoint = "https://secure.starhub.com/myaccountmgr/fapi/usage/data"

        headers = {
            "Accept": "application/json",
            "X-User-Agent": "39955632c1b718a3c8082c9c58cb4771",
            "Authorization": utoken,
            "x-forwarded-proto": "https"
        }
        resp = requests.get(endpoint, headers=headers)
        if (resp.status_code != 200):
            if (resp.status_code == 401):
                sys.exit("Failed authorization.")
            else:
                raise ApiError(resp.status_code)

        overview_json = resp.json()

        return overview_json["mainContext"]["present"]["any"][0]["dataUsages"]["usageDetail"]


api = StarhubApi()

if (args.utoken is not None):
    utoken = args.utoken
elif (args.utoken_file is not None):
    f = open(args.utoken_file, "r")
    utoken = f.read()
    f.close()
else:
    vctk3 = api.get_vctk3_dict(args.uid, args.pw)
    utoken = api.get_utoken(vctk3["uid"], vctk3["vctk3"])
    if (args.save_utoken is not None):
        f = open(args.save_utoken, "w")
        f.write(utoken)
        f.close()

mobiles_overview_json = api.get_mobile_overview(utoken)
print(mobiles_overview_json)
# time.sleep(99999)

# driver.quit()
