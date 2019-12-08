import requests
import json


class ig_connect:
    def __init__(self, account_type, key, user_id, password):
        self.account_type = account_type
        self.key = key
        self.user_id = user_id
        self.password = password
        self.data = {"identifier": self.user_id, "password": self.password}
        self.headers_v2 = {'Content-Type': 'application/json; charset=utf-8',
           'Accept': 'application/json; charset=utf-8',
           'X-IG-API-KEY': self.key,
           'Version': '2'
           }
        if self.account_type == 'real':
            self.url = 'https://api.ig.com/gateway/deal/'
        elif self.account_type == 'demo':
            self.url = 'https://demo-api.ig.com/gateway/deal/'
        self.endpoint = self.url + 'session/'
        r = requests.post(self.endpoint, data=json.dumps(self.data), headers=self.headers_v2)
        headers_json = dict(r.headers)
        self.CST_token = headers_json["CST"]
        self.x_sec_token = headers_json["X-SECURITY-TOKEN"]

    def get_accounts(self):
        base_url = self.url + '/accounts'
        authenticated_headers = {'Content-Type': 'application/json; charset=utf-8',
                             'Accept': 'application/json; charset=utf-8',
                             'X-IG-API-KEY': self.key,
                             'CST': self.CST_token,
                             'X-SECURITY-TOKEN': self.x_sec_token}
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text) 
        return d