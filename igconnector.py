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
        if self.account_type == 'live':
            self.url = 'https://api.ig.com/gateway/deal/'
        elif self.account_type == 'demo':
            self.url = 'https://demo-api.ig.com/gateway/deal/'
        self.endpoint = self.url + 'session/'
        r = requests.post(self.endpoint, data=json.dumps(self.data), headers=self.headers_v2)
        headers_json = dict(r.headers)
        self.CST_token = headers_json["CST"]
        self.x_sec_token = headers_json["X-SECURITY-TOKEN"]
        self.authenticated_headers_v2 = {'Content-Type': 'application/json; charset=utf-8',
                             'Accept': 'application/json; charset=utf-8',
                             'X-IG-API-KEY': self.key,
                             'CST': self.CST_token,
                             'X-SECURITY-TOKEN': self.x_sec_token}

    def get_accounts(self):
        base_url = self.url + '/accounts'
        auth_r = requests.get(base_url, headers=self.authenticated_headers_v2)
        d = json.loads(auth_r.text) 
        return d

    def open_order(self, epic_id, direction, limit_distance, stop_distance, size, currency = 'GBP',
        order_type = 'MARKET', expiry = 'DFB', 
        guaranteed_stop = False, force_open = True):
        base_url = self.url + '/positions/otc'
        open_data = {
        "direction": direction,
        "epic": epic_id,
        "orderType": order_type,
        "size": str(size),
        "expiry": expiry,
        "guaranteedStop": str(guaranteed_stop).lower(),
        "currencyCode": currency,
        "forceOpen": str(force_open).lower(),
        "limitDistance": str(limit_distance),
        "stopDistance": str(stop_distance)
        }
        r = requests.post(
            base_url,
            data=json.dumps(open_data),
            headers=self.authenticated_headers_v2)

        print("#### RESPONSE ####")
        print("Status code: {}".format(r.status_code))
        print("Status reason: {}".format(r.reason))
        print("Status detail: {}".format(r.text))

    def get_orders(self):
        base_url = self.url + "/positions"
        position_auth_r = requests.get(base_url, headers=self.authenticated_headers_v2)
        position_json = json.loads(position_auth_r.text)
        
        print('Current position summary:')
        print(position_json)
        return position_json
    
    def close_order(self, deal_id):
        open_position = self.get_orders()
        for item in open_position['positions']:
            if item['position']['dealId'] == deal_id:
                dealSize = item['position']['dealSize']
                direction = item['position']['direction']

        authenticated_headers_delete = {'Content-Type': 'application/json; charset=utf-8',
                     'Accept': 'application/json; charset=utf-8',
                     'X-IG-API-KEY': self.key,
                     'CST': self.CST_token,
                     'Version': '1',
                     '_method': 'DELETE',
                     'X-SECURITY-TOKEN': self.x_sec_token}
        base_url = self.url + '/positions/otc'
        try: 
            if direction == 'BUY':
                closing_direction = 'SELL'
            elif direction == 'SELL':
                closing_direction = 'BUY'
        except:
            return print("Deal with id {} does not exist".format(deal_id))
        
        del_data = {
                "dealId": deal_id,
                "direction": closing_direction,
                "size": dealSize,
                "orderType": "MARKET",
            }
        r = requests.post(base_url, data=json.dumps(del_data), 
            headers=authenticated_headers_delete)
        if r.status_code == 200:
            print("Order closed with reference {}".format(r.text))
        else:
            print("Something went wrong. Please try again.")