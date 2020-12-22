# Using the program

## Prerequisites

* Google Chrome 87.0.4280.66 (optional)
* Python

## Getting started

Install requirements with pip  
Run `main.py` with:

* `--uid user@gmail.com --pw password`
* `--utoken user_token`
* `--utoken_file path_to_file`

utoken can be saved to a file with `--save_utoken file_path`.

`--mobile 12345678 23456789` to query data for the listed mobile numbers.

### Login approach
If using the logging in approach, we will use chromedriver to login and get our required information. However, this method takes way longer to execute as the website loads slow.

### Result
```json
{'number': '12345678', 'data_usage': 9.426, 'data_left': 25.573, 'data_total': 35.0}
{'number': '23456789', 'data_usage': 9.426, 'data_left': 25.573, 'data_total': 35.0}
```


# Reverse engineering Starhub API

Record network in devtools, login to starhub.com. Go to https://secure.starhub.com/myaccountmgr/#/services/summary/. Start searching for values such as phone number in network tab. Afterwards, copy cURL to bash for import in Postman. If network has too much traffic, use HAR Analyzer tool.

## HAR Analyzer tool

* Record network and retrace all steps from logging in starhub to getting data usage of a phone
* Save all network as `.HAR` file, analyze file by accessing https://toolbox.googleapps.com/apps/har_analyzer/
* Search for values found
* Start reverse engineering

# Starhub codes

## Getting vctk3
```
GET /myaccountmgr/login?isExpired=false&acvctk=eHVUjq1l2d50aWqZq%2F%2BDWkzzIY0%3D HTTP/1.1
Host: secure.starhub.com
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-Dest: document
Referer: https://secure.starhub.com/myaccountmgr/login?isExpired=false
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Cookie: xxx
```

### Response Header contains vctk3 in cookie

```
HTTP/1.1 200 OK
Date: Thu, 19 Nov 2020 13:10:54 GMT
Server: Apache
Content-Length: 972
Set-Cookie: vctk3=y+SkQ5OunSJ06NtD3Jdo3VH2vUeDJzT4u2b4qL0OKnSFzoUMEL0XR76/dgLYLnWk7HKNLSHOR0WU46IbqbzHZymgbyu+DH/Zi+lnefSoB9AK9m3+uTG9I7ZQLSOhbU/RnTkYpNtijLoGtlwJjqLz+r8fI5bhHksptqDGPcn0NSUAM60BPDSzDGTTMILMjVa42evF0BSBYzsbIQn+5nL1HafgxETg7kCnGlz/54FdHtvbFqHrfMw/+SiujvIArbVDWZaaj0lSSYoh0htcAJBwmrbKRsgXmg74iIQfNyK+6BPhzfK2uIntPEbXVwyttP1Ygic6Dd69l6BD4YWDKGrrWoTCz6d7PueAOtE5N0L3APW+U4+sCAN3aC3k7J+7JM3B4hJKHSgRxuCfxNdbnEGHwMYa+5zuuVhbo0p8+73G5fy1DkzID6FGzl/xsMuKqfQo; Path=/; HttpOnly; Secure
Keep-Alive: timeout=15, max=83
Connection: Keep-Alive
Content-Type: text/html
X-DNS-Prefetch-Control: off
```

## Getting Authorization Request
```
POST /myaccountmgr/essoLogin?ts=1605731560564 HTTP/1.1
Host: secure.starhub.com
Connection: keep-alive
Content-Length: 0
Accept: application/json
X-User-Agent: 39955632c1b718a3c8082c9c58cb4771
x-forwarded-proto: https
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36
Origin: https://secure.starhub.com
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://secure.starhub.com/myaccountmgr/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Cookie: xxx
```

Important cookie values, the rest doesn't affect output

* uid
* vctk3

### Response contains utoken which is used for Authorization
```json
{
  "userDetails": {
    "uid": "redacted",
    "lastLogin": {
      redacted
    },
    "prepaid": false,
    "perxUToken": null,
    "permission": null,
    "currentLogin": null,
    "utype": "HUBID",
    "utoken": "xxx",
    "dno": null,
    "dtype": null
  },
  "mainContext": {
    "cid": "CTX000062",
    "banner": {
      "repName": "ESSO Web Login",
      "repURL": null
    },
    "present": {
      "any": [
        {
          redacted
        }
      ]
    },
    "collect": null,
    "script": null,
    "guidedFlows": {
      "gfcontext": []
    }
  },
  "subContext": [],
  "attachment": null,
  "irid": "redacted",
  "updatedOn": null
}
```

## Getting data usages of all devices
Use the utoken above as Authorization.

### Getting Data Usage Request
```
GET /myaccountmgr/fapi/usage/data?type=LOCAL&ts=1605731582281 HTTP/1.1
Host: secure.starhub.com
Connection: keep-alive
Accept: application/json
X-User-Agent: 39955632c1b718a3c8082c9c58cb4771
Authorization: UTOKEN
x-forwarded-proto: https
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://secure.starhub.com/myaccountmgr/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Cookie: xxx
```

**Note:** X-User-Agent is needed but it is set as a constant in our script.

### Response overview json
```json
{
  "userDetails": {
    "uid": "redacted",
    "lastLogin": null,
    "prepaid": false,
    "perxUToken": null,
    "permission": null,
    "currentLogin": null,
    "utoken": "xxx",
    "utype": "HUBID",
    "dno": null,
    "dtype": null
  },
  "mainContext": {
    "cid": "CTX000028",
    "banner": {
      "repName": "Data Usage",
      "repURL": null
    },
    "present": {
      "any": [
        {
          "dataUsages": {
            "usageDetail": [
              mobile_overview_json
            ],
            "cacheKey": null
          },
          "voiceUsages": null,
          "dataRoamingUsages": null,
          "iddusages": null,
          "smsusages": null
        }
      ]
    },
    "collect": null,
    "script": null,
    "guidedFlows": {
      "gfcontext": []
    }
  },
  "subContext": [],
  "attachment": null,
  "irid": "redacted",
  "updatedOn": null
}
```
