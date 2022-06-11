import requests
import tweepy
from bs4 import BeautifulSoup
import random
import json
import time

_url = ""
_url2 = ""
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
    _url2 = temp_dict['url2']
    
def random_text_ver3(api): # korea woeid = 23424868
    hot_topics = []
    for obj in api.available_trends():
        if obj['countryCode'] == "KR":
            if obj['name'] == "Korea":
                hot_topics = api.get_place_trends(obj['woeid'])
                break
    topic = hot_topics[0]['trends'][random.randint(0, len(hot_topics[0]['trends']))]
    # print(topic,topic['query'])
    for i in range(len(hot_topics[0]['trends'])):
        if hot_topics[0]['trends'][i]['tweet_volume'] == None:
            hot_topics[0]['trends'][i]['tweet_volume'] = 0

    hot_topics = sorted(hot_topics[0]['trends'], key=lambda x : x['tweet_volume'], reverse=True)
    topic = hot_topics[random.randint(0, len(hot_topics))]
    search_result = api.search_tweets(q=topic['query'], result_type="mixed", count=10)

    # no RT, no url
    text = ""
    for result in search_result:
        if "t" not in result.text and "T" not in result.text:
            text = result.text
            break
    api.update_status(text)

if __name__ == '__main__': 
    #authenticating to access the twitter API
    auth=tweepy.OAuthHandler(api_key,secret_key)
    auth.set_access_token(Access_token,Access_secret_token)
    api=tweepy.API(auth)

    # random_text_ver3(api)
    while True:
        try:
            random_text_ver3(api)
            time.sleep(random.randint(300,600))
        except:
            time.sleep(60)
            continue