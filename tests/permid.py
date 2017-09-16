import sys
import requests
import os
import json
import re
calais_url = 'https://api.thomsonreuters.com/permid/calais'

token = 'pMrokjCJfmv15ZVDcfJ1dqeadtcAqONR'

class PermidSender(object):
    def __init__(self,token):
        self.token = token
        self.headers = {'X-AG-Access-Token' : token, 'Content-Type' : 'text/html', 'outputformat' : 'application/json'}

    def get_topics(self, sentence):
        content = self._sendFile(sentence, self.headers)
        keys = content.keys()
        relevant_keys = [key for key in keys if '/cat' in key]
        topics = []
        for key in relevant_keys:
            topics.append(content[key]['name'])

        return topics

    def _sendFile(self, sentence, headers):
        response = requests.post(calais_url, data=sentence, headers=headers, timeout=80)
        content = response.text
        json_c = json.loads(content)
        return json_c

if __name__ == "__main__":
   sender = PermidSender(token)
   topics = sender.get_topics('Obama Care was repealled.')
   print(topics)
