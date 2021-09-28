# -*- coding: utf-8 -*-
# Snippetized from tapirik (https://github.com/cpfair/tapiriik) source code by
# Chmouel Boudjnah <chmouel@chmouel.com>
#
# Get/Update weight on Garmin via its API
# Set the weight to strava
# You need to register your strava app and get a token, see :
#    https://strava.github.io/api/v3/oauth/
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import fcntl
import requests
import tempfile
import time

from stravalib.client import Client


def strava_update_weight(client_id, client_secret, code, weight):
    client = Client()

    access_token = client.exchange_code_for_token(
        client_id=client_id,
        client_secret=client_secret,
        code=code)

    client.access_token = access_token
    client.update_athlete(weight=weight)
    return(client.get_athlete())


class Gconnect(object):
    _obligatory_headers = {
        "Referer": "https://connect.garmin.com/"
    }
    _reauthAttempts = 1

    def __init__(self):
        rate_lock_path = tempfile.gettempdir() + "/gc_rate.localhost.lock"
        # Ensure the rate lock file exists (...the easy way)
        open(rate_lock_path, "a").close()
        self._rate_lock = open(rate_lock_path, "r+")

    def _request_with_reauth(self, req_lambda, email=None, password=None):
        for i in range(self._reauthAttempts + 1):
            session = self._get_session(email=email, password=password)
            self._rate_limit()
            result = req_lambda(session)
            if result.status_code not in (403, 500):
                return result
        return result

    def _rate_limit(self):
        min_period = 1
        fcntl.flock(self._rate_lock, fcntl.LOCK_EX)
        try:
            self._rate_lock.seek(0)
            last_req_start = self._rate_lock.read()
            if not last_req_start:
                last_req_start = 0
            else:
                last_req_start = float(last_req_start)

            wait_time = max(0, min_period - (time.time() - last_req_start))
            time.sleep(wait_time)

            self._rate_lock.seek(0)
            self._rate_lock.write(str(time.time()))
            self._rate_lock.flush()
        finally:
            fcntl.flock(self._rate_lock, fcntl.LOCK_UN)

    def _get_session(self, email=None, password=None):
        session = requests.Session()
        data = {
            "username": email,
            "password": password,
            "_eventId": "submit",
            "embed": "true",
            # "displayNameRequired": "false"
        }
        params = {
            "service": "https://connect.garmin.com/post-auth/login",
            # "webhost": "olaxpw-connect00.garmin.com",
            "clientId": "GarminConnect",
            "gauthHost": "https://sso.garmin.com/sso",
            # "rememberMeShown": "true",
            # "rememberMeChecked": "false",
            "consumeServiceTicket": "false",
            # "id": "gauth-widget",
            # "embedWidget": "false",
            # "source": "http://connect.garmin.com/en-US/signin",
            # "createAccountShown": "true",
            # "openCreateAccount": "false",
            # "usernameShown": "true",
            # "displayNameShown": "false",
            # "initialFocus": "true",
            # "locale": "en"
        }
        # I may never understand what motivates people to mangle a perfectly
        # good protocol like HTTP in the ways they do...
        preResp = session.get("https://sso.garmin.com/sso/login",
                              params=params)
        if preResp.status_code != 200:
            raise Exception("SSO prestart error %s %s" %
                            (preResp.status_code, preResp.text))

        ssoResp = session.post("https://sso.garmin.com/sso/login",
                               params=params,
                               data=data, allow_redirects=False)
        if ssoResp.status_code != 200 or "temporarily unavailable" \
           in ssoResp.text:
            raise Exception("SSO error %s %s" % (ssoResp.status_code,
                                                 ssoResp.text))

        if ">sendEvent('FAIL')" in ssoResp.text:
            raise Exception("Invalid login")
        if ">sendEvent('ACCOUNT_LOCKED')" in ssoResp.text:
            raise Exception("Account Locked")
        if "renewPassword" in ssoResp.text:
            raise Exception("Reset password")

        # ...AND WE'RE NOT DONE YET!

        self._rate_limit()
        gcRedeemResp = session.get(
            "https://connect.garmin.com/post-auth/login",
            allow_redirects=False)
        if gcRedeemResp.status_code != 302:
            raise Exception("GC redeem-start error %s %s" % (
                gcRedeemResp.status_code, gcRedeemResp.text))
        url_prefix = "https://connect.garmin.com"
        # There are 6 redirects that need to be followed to get the correct
        # cookie
        # ... :(
        max_redirect_count = 7
        current_redirect_count = 1
        while True:
            self._rate_limit()
            url = gcRedeemResp.headers["location"]
            # Fix up relative redirects.
            if url.startswith("/"):
                url = url_prefix + url
            url_prefix = "/".join(url.split("/")[:3])
            gcRedeemResp = session.get(url, allow_redirects=False)

            if current_redirect_count >= max_redirect_count and \
               gcRedeemResp.status_code != 200:
                raise Exception("GC redeem %d/%d error %s %s" % (
                    current_redirect_count, max_redirect_count,
                    gcRedeemResp.status_code, gcRedeemResp.text))
            if gcRedeemResp.status_code == 200 \
               or gcRedeemResp.status_code == 404:
                break
            current_redirect_count += 1
            if current_redirect_count > max_redirect_count:
                break

        session.headers.update(self._obligatory_headers)

        return session


def updateweight(username, password, kg):
    data = '{"userData":{"weight":%d}}' % (int(kg * 1000))
    bg = Gconnect()
    sess = bg._get_session(username, password)
    h = {
        'nk': 'NT',
        'x-requested-with': 'XMLHttpRequest',
        'x-http-method-override': 'PUT',
        'content-type': 'application/json',
    }
    sess.headers = h
    resp = sess.post("https://connect.garmin.com/modern/proxy" +
                     "/userprofile-service/userprofile/user-settings/",
                     data, headers=h)
    return resp


def getweight(username, password):
    bg = Gconnect()
    sess = bg._get_session(username, password)

    resp = sess.get("https://connect.garmin.com/modern/proxy" +
                    "/userprofile-service/userprofile/user-settings/")
    ret = resp.json()

    if ret and 'userData' in ret and 'weight' in ret['userData']:
        return ret['userData']['weight'] / 1000


if __name__ == '__main__':
    # Garmin username password
    username = ''
    password = ''
    gweight = getweight(username, password)

    client_id = ""
    code = ''
    client_secret = ''
    # To get the values, you should be able to do this :
    # Run a simple webserver with python -m SimpleHTTPServer 8080 first, click
    #  on the URL from authorize_url and grab the 'code' keyword from the URL
    #  from the 404 message)
    #
    # The client_id and client_secret should be grabbed from your app setting
    # here: https://www.strava.com/settings/api
    #
    # client = Client()
    # authorize_url = client.authorization_url(
    #     client_id=client_id,
    #     scope='write',
    #     redirect_uri='http://localhost:8080/')
    # print(authorize_url)
    # sys.exit(0)

    strava_update_weight(client_id, client_secret, code, gweight)
