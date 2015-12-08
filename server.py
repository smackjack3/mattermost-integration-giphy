import os
import sys
import requests
import json
from flask import Flask
from flask import request
from flask import Response

app = Flask(__name__)

USERNAME = 'giphy' # username the bot posts as
ICON_URL = 'http://api.giphy.com/img/api_giphy_logo.png' # display picture the bot posts with
RATING = 'pg-13' # the maximum parental rating of gifs posted (y, pg, pg-13, r)

GIPHY_API_KEY = 'dc6zaTOxFJmzC' # this is a public beta key, for production use you must go to http://api.giphy.com/submit and request a production key
MATTERMOST_TOKEN = '' # the Mattermost token generated when you created your outgoing webhook

@app.route('/')
def root():
    """
    Home handler
    """

    return "OK"

@app.route('/new_post', methods=['POST'])
def new_post():
    """
    Mattermost new post event handler
    """

    data = request.form

    if data['token'] != MATTERMOST_TOKEN:
        print 'Tokens did not match, it is possible that this request came from somewhere other than Mattermost'
        return 'OK'

    translate_text = data['text'][len(data['trigger_word']):]

    if len(translate_text) == 0:
        print "No translate text provided, not hitting Giphy"
        return 'OK'

    gif_url = giphy_translate(translate_text)

    if len(gif_url) == 0:
        print 'No gif url found, not returning a post to Mattermost'
        return 'OK'

    resp_data = {}
    resp_data['text'] = gif_url
    resp_data['username'] = USERNAME
    resp_data['icon_url'] = ICON_URL

    resp = Response(content_type='application/json')
    resp.set_data(json.dumps(resp_data))

    return resp

def giphy_translate(text):
    """
    Giphy translate method, uses the Giphy API to find an appropriate gif url
    """

    params = {}
    params['s'] = text
    params['rating'] = RATING
    params['api_key'] = GIPHY_API_KEY

    resp = requests.get('http://api.giphy.com/v1/gifs/translate', params=params)

    if resp.status_code is not requests.codes.ok:
        print 'Encountered error using Giphy API, text=%s, status=%d, response_body=%s' % (text, resp.status_code, resp.json())
        return ''

    resp_data = resp.json()

    return resp_data['data']['images']['original']['url']


if __name__ == "__main__":
    USERNAME = os.environ.get('USERNAME', USERNAME)
    ICON_URL = os.environ.get('ICON_URL', ICON_URL)
    RATING = os.environ.get('RATING', RATING)
    GIPHY_API_KEY = os.environ.get('GIPHY_API_KEY', GIPHY_API_KEY)
    MATTERMOST_TOKEN = os.environ.get('MATTERMOST_TOKEN', MATTERMOST_TOKEN)

    if len(GIPHY_API_KEY) == 0:
        print "GIPHY_API_KEY must be configured. Please see README.md for instructions"
        sys.exit()

    if len(MATTERMOST_TOKEN) == 0:
        print "MATTERMOST_TOKEN must be configured. Please see README.md for instructions"
        sys.exit()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
