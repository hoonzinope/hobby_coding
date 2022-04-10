import requests
import tweepy
from bs4 import BeautifulSoup
import random
import json
import time

_url = ""
api_key = ""
secret_key = ""
Bearer_token = ""
Access_token = ""
Access_secret_token = ""

with open("tweet_api.json", "r") as temp_json:
    temp_dict = json.load(temp_json)

    api_key = temp_dict['api_key']
    secret_key = temp_dict['secret_key']
    Bearer_token = temp_dict['Bearer_token']
    Access_token = temp_dict['Access_token']
    Access_secret_token = temp_dict['Access_secret_token']
    _url = temp_dict['url']

def random_text():
    url = _url
    headers = {
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    text_list = []
    for td in soup.select('.listsubject.sbj'):
        text = td.text.strip()
        if len(text) < 3:
            continue
        text_list.append(text)
        
    if len(text_list) == 0:
        return None
    else:
        rand_index = random.randint(1,len(text_list))
        return text_list[rand_index]

if __name__ == '__main__': 
    #authenticating to access the twitter API
    auth=tweepy.OAuthHandler(api_key,secret_key)
    auth.set_access_token(Access_token,Access_secret_token)
    api=tweepy.API(auth)

    while True:
        try:
            tweet=random_text()
            api.update_status(tweet)
            time.sleep(600)
        except:
            time.sleep(60)
            continue