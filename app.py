import requests
import json
import time
from datetime import datetime
import pandas as pd
import os
import random
from flask import Flask, jsonify

app = Flask(__name__)

def getSnapp(snapp_auth, origin, destinations):
    print('getting Snapp price...')

    cookies = {
        '_ym_uid': '1720127313783530019',
        '_ym_isad': '2',
        '_ym_d': '1720127313',
        '_ga_Y4QV007ERR': 'GS1.1.1721666421.7.1.1721667520.21.0.0',
        '_ga': 'GA1.1.896494269.1720127312',
        '_clck': '1hg0vw8%7C2%7Cfno%7C0%7C1646',
        'X-Contour-Session-Affinity': '"cc59efd4730d8935"'
    }

    json_data = {
        'points': [
            {
                'lat': str(origin[0]),
                'lng': str(origin[1]),
            },
            {
                'lat': str(destinations[0]),
                'lng': str(destinations[1]),
            },
            None,
        ],
        'waiting': None,
        'round_trip': False,
        'voucher_code': None,
        'service_types': [
            1,
            5,
        ],
        'hurry_price': None,
        'hurry_flag': None,
        'priceidercomm': False,
    }

    headers = {
        'authority': 'app.snapp.taxi',
        'accept': '*/*',
        'accept-language': 'fa,en-US;q=0.9,en;q=0.8,ar;q=0.7',
        'app-version': 'pwa',
        'authorization': snapp_auth,
        'content-type': 'application/json',
        'cookie': '_ga=GA1.1.896494269.1720127312; _ym_uid=1720127313783530019; _ym_d=1720127313; X-Contour-Session-Affinity="cc59efd4730d8935"; _clck=1hg0vw8%7C2%7Cfno%7C0%7C1646; _ym_isad=2; _ga_Y4QV007ERR=GS1.1.1721666421.7.1.1721667520.21.0.0',
        'locale': 'fa-IR',
        'origin': 'https://app.snapp.taxi',
        'referer': 'https://app.snapp.taxi/pre-ride?utm_source=website&utm_medium=webapp-button',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-app-name': 'passenger-pwa',
        'x-app-version': '18.1.0',
    }

    response = requests.post(
        'https://app.snapp.taxi/api/api-base/v2/passenger/newprice/s/6/0',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    newdata = response.json()
    print(newdata)

    snapp_price = {'normal': ['', ''], 'bike': ['', ''], 'timestamp': int(time.time()),'active':False,'surge':False, 'distance':0, 'duration':0}
    if newdata['data'].get('prices'):
        snapp_price['active']=True
        snapp_price['normal'][0] = newdata['data'].get('prices')[0].get('final')
        snapp_price['normal'][1] = newdata['data'].get('prices')[0].get('raw_fare')
        snapp_price['surge'] = newdata['data'].get('prices')[0].get('is_surged')
        
        response_des = requests.get(
            f'https://direction.raah.ir/navigation-v7/directions/v5/mapbox/driving-traffic/{origin[1]},{origin[0]};{destinations[1]},{destinations[0]}'
        )
        
        newdata_des = response_des.json()
        print(newdata_des)
        if 'routes' in newdata_des:
            snapp_price['distance']=newdata_des['routes'][0].get('distance')
            snapp_price['duration']=newdata_des['routes'][0].get('duration')
        else:
            snapp_price['distance']=None
            snapp_price['duration']=None
            
        if len(newdata['data'].get('prices', [])) > 1 and newdata['data']['prices'][1].get('final'):
            snapp_price['bike'][0] = newdata['data'].get('prices')[1].get('final')
            snapp_price['bike'][1] = newdata['data'].get('prices')[1].get('raw_fare')
        else:
            snapp_price['bike'][0] = None
            snapp_price['bike'][1] = None
        if snapp_price['normal'][1] is None:
            snapp_price['normal'][1] = snapp_price['normal'][0]
        if snapp_price['bike'][1] is None:
            snapp_price['bike'][1] = snapp_price['bike'][0]

    return snapp_price

def generate_random_coordinates():
    min_lat = 35.5
    max_lat = 36.1
    min_lng = 51.0
    max_lng = 51.7
    lat = round(random.uniform(min_lat, max_lat), 6)
    lng = round(random.uniform(min_lng, max_lng), 6)
    return [lat, lng]

@app.route('/')
def fetch_snapp_price():
    while True:
        
        
        origin = generate_random_coordinates()
        destinations = generate_random_coordinates()
        snapp_auth = 'Bearer eyJhbGciOiJFN6NDlrdzJaT05JQk5vVURYUGYyQlVWWGt4SzZlUHlnakUiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOlsicGFzc2VuZ2VyIl0sImV4cCI6MTcyNDA5MTQ3NCwiaWF0IjoxNzIyODgxODc0LCJpc3MiOjEsImp0aSI6IkNNZXJiRk5YRWUrWVJob0wwdURPV2JaaVdPMU1GRXQ1b2JVZnlWZ0dTMVEiLCJxYSI6ZmFsc2UsInNpZCI6IjJJTlhaUE5EQTFKMERQUkozT05YMExSMDRRUSIsInN1YiI6ImJ5djg1UjdrTEFlMDdvNCJ9.6zxf_W4fNOgmj1W2KusMa6JgH9CZrONB-emoS0CY88rmTNTfwOZNSkVHPveE4gMVZjo8XERtkFaSu8NJrS7d6A'

        snapp_price = getSnapp(snapp_auth, origin, destinations)
    
        new_data = pd.DataFrame({
            'origin_lat': [origin[0]],
            'origin_lng': [origin[1]],
            'destination_lat': [destinations[0]],
            'destination_lng': [destinations[1]],
            'price_normal_final': [snapp_price['normal'][0]],
            'price_normal_raw': [snapp_price['normal'][1]],
            'price_bike_final': [snapp_price['bike'][0]],
            'price_bike_raw': [snapp_price['bike'][1]],
            'timestamp': [snapp_price['timestamp']],
            'surge':[snapp_price['surge']],
            'distance':[snapp_price['distance']],
            'duration':[snapp_price['duration']]
        })

        if snapp_price['active']:
        
            csv_file = 'snapp_data_test.csv'

            if os.path.exists(csv_file):
                existing_data = pd.read_csv(csv_file)
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            else:
                updated_data = new_data
    
            updated_data.to_csv(csv_file, index=False)
        time.sleep(30)
    
    return jsonify(snapp_price)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
