# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
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
import json
import os
import requests
import subprocess
import tempfile
import time


class GarminConnect(object):
    _obligatory_headers = {"Referer": "https://connect.garmin.com/"}
    _reauthAttempts = 1
    _garmin_signin_headers = {"origin": "https://sso.garmin.com"}

    def __init__(self):
        rate_lock_path = tempfile.gettempdir() + "/gc_rate.localhost.lock"
        # Ensure the rate lock file exists (...the easy way)
        open(rate_lock_path, "a").close()
        self._rate_lock = open(rate_lock_path, "r+")

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

    def get_session(self, email=None, password=None):
        session = requests.Session()
        data = {
            "username": email,
            "password": password,
            "_eventId": "submit",
            "embed": "true",
            # "displayNameRequired": "false"
        }
        params = {
            "service": "https://connect.garmin.com/modern",
            # "redirectAfterAccountLoginUrl": "http://connect.garmin.com/modern",
            # "redirectAfterAccountCreationUrl": "http://connect.garmin.com/modern",
            # "webhost": "olaxpw-connect00.garmin.com",
            "clientId": "GarminConnect",
            "gauthHost": "https://sso.garmin.com/sso",
            # "rememberMeShown": "true",
            # "rememberMeChecked": "false",
            "consumeServiceTicket": "false",
            # "id": "gauth-widget",
            # "embedWidget": "false",
            # "cssUrl": "https://static.garmincdn.com/com.garmin.connect/ui/src-css/gauth-custom.css",
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
        preResp = session.get(
            "https://sso.garmin.com/sso/login", params=params)
        if preResp.status_code != 200:
            raise Exception("SSO prestart error %s %s" % (preResp.status_code,
                                                          preResp.text))

        ssoResp = session.post(
            "https://sso.garmin.com/sso/login",
            headers=self._garmin_signin_headers,
            params=params,
            data=data,
            allow_redirects=False)
        if ssoResp.status_code != 200 or "temporarily unavailable" \
           in ssoResp.text:
            raise Exception(
                "SSO error %s %s" % (ssoResp.status_code, ssoResp.text))

        if ">sendEvent('FAIL')" in ssoResp.text:
            raise Exception("Invalid login")
        if ">sendEvent('ACCOUNT_LOCKED')" in ssoResp.text:
            raise Exception("Account Locked")
        if "renewPassword" in ssoResp.text:
            raise Exception("Reset password")

        # ...AND WE'RE NOT DONE YET!

        self._rate_limit()
        gcRedeemResp = session.get(
            "https://connect.garmin.com/modern", allow_redirects=False)
        if gcRedeemResp.status_code != 302:
            raise Exception("GC redeem-start error %s %s" %
                            (gcRedeemResp.status_code, gcRedeemResp.text))
        url_prefix = "https://connect.garmin.com"
        # There are 6 redirects that need to be followed to get the correct cookie
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

            if current_redirect_count >= max_redirect_count and gcRedeemResp.status_code != 200:
                raise Exception("GC redeem %d/%d error %s %s" %
                                (current_redirect_count, max_redirect_count,
                                 gcRedeemResp.status_code, gcRedeemResp.text))
            if gcRedeemResp.status_code == 200 or gcRedeemResp.status_code == 404:
                break
            current_redirect_count += 1
            if current_redirect_count > max_redirect_count:
                break

        session.headers.update(self._obligatory_headers)

        return session


class GarminOPS(object):
    get_all_workouts_cache = {}

    def __init__(self, args):
        bg = GarminConnect()
        self.session = bg.get_session(args.garmin_user, args.garmin_password)

    def _build_curl(self, url, extra_headers={}):
        headers = {
            'origin':
            'https://connect.garmin.com',
            'accept-language':
            'en-GB,en-US;q=0.9,en;q=0.8,fr-FR;q=0.7,fr;q=0.6',
            'nk':
            'NT',
            'x-requested-with':
            'XMLHttpRequest',
            'x-lang':
            'en-US',
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'content-type':
            'application/json',
            'accept':
            'application/json, text/javascript, */*; q=0.01',
            'referer':
            'https://connect.garmin.com/modern/workout/create/running',
            'authority':
            'connect.garmin.com',
            'x-app-ver':
            '4.19.3.0',
            'dnt':
            '1',
        }
        headers.update(extra_headers)

        # request not working :\
        curl = f"curl -f --fail-early -s '{url}' "
        cookies = "-H 'Cookie: "
        for k, v in self.session.cookies.iteritems():
            cookies += f'{k}={v}; '
        curl += f"{cookies.strip()}' "
        for k, v in headers.items():
            curl += f"-H '{k.capitalize()}: {v}' "
        return curl

    def get_all_workouts(self):
        if self.get_all_workouts_cache:
            return self.get_all_workouts_cache
        resp = self.session.get(
            'https://connect.garmin.com/modern/proxy/workout-service/workouts?start=1&limit=999&myWorkoutsOnly=true&sharedWorkoutsOnly=false&orderBy=WORKOUT_NAME&orderSeq=ASC&includeAtp=false'
        )
        resp.raise_for_status()
        self.get_all_workouts_cache = resp.json()
        return self.get_all_workouts_cache

    def delete_workout(self, wid):

        curl = self._build_curl(
            f"https://connect.garmin.com/modern/proxy/workout-service/workout/{wid}",
            extra_headers={
                'x-http-method-override': 'DELETE',
            })
        curl += "-X POST"
        retcode, output = subprocess.getstatusoutput(f'{curl}')
        if retcode != 0:
            output = {
                'errorcode': retcode,
                'error': f"Error while adding garmin workout: {output}"
            }
        return

    def schedule_workout(self, wid, date):
        curl = self._build_curl(
            f"https://connect.garmin.com/modern/proxy/workout-service/schedule/{wid}"
        )
        jeez = json.dumps({"date": date.strftime("%Y-%m-%d")})
        curl += f"--data-binary '{jeez}'"
        retcode, output = subprocess.getstatusoutput(f'{curl}')
        if retcode != 0:
            output = {
                'errorcode': retcode,
                'error': f"Error while adding garmin workout: {output}"
            }
        return

    def create_workout(self, jeez):
        curl = self._build_curl(
            'https://connect.garmin.com/modern/proxy/workout-service/workout')

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
            fp.write(jeez)
            fp.close()

        curl += f"--data @{fp.name}"

        retcode, output = subprocess.getstatusoutput(f'{curl}')
        os.remove(fp.name)
        if retcode != 0:
            return {
                'errorcode': retcode,
                'error': f"Error while adding garmin workout: {output}"
            }
        try:
            return json.loads(output)
        except (json.decoder.JSONDecodeError):
            return output
