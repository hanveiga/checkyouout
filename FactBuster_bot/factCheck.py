## telegram bot: @factbuster_bot Name: WhatTheFAct
# adapted code from echobot.py example
# Query to telegram returns the statement/sentence/content's reliability of information through checking various articles published
# on reuters. 

import json
import requests
import time
import urllib
import os


TOKEN = '417979782:AAFv5IMcPNYhKjQWX8ZoN6LO__P1nByauoQ'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        query={"text": text}
        print(query)
        try:
            factUrl="http://localhost:8877/textcheck"
            response = requests.post(factUrl, data=json.dumps(query))
            data=json.loads(response.text)
            label=data[0]["label"]
            results=data[0]["results"]
            for b in results:
                try:
                    video_link=b["video_url"]
                    send_message("You might want to watch this from SRF on this topic: " + video_link, chat)
                except:
                    print("none")#empty
            

            if label == "discuss":
                factcheck = "This statement/topic is debatable"
            elif label == "agree":
                factcheck = "This topic agrees with reliable sourcess" 
            elif label == "disagree":
                factcheck = "Hmmm... Seems like this phrase disagrees with content from reliable sources"        
            else: 
                factcheck = "You might want to look into that topic against other sources"
           
            send_message(factcheck, chat)

        except:
            factcheck='no result'
            #send_message(factcheck, chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()