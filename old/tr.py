# -*- coding: utf-8 -*-
# Chmouel Boudjnah <chmouel@chmouel.com>
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


class TRconnect(object):
    _obligatory_headers = {
        "Referer": "https://www.trainerroad.com/login"
    }
    _reauthAttempts = 1

    def __init__(self, username, password):
        self.username = username
        self.password = password
        rate_lock_path = tempfile.gettempdir() + "/tr_rate.localhost.lock"
        # Ensure the rate lock file exists (...the easy way)
        open(rate_lock_path, "a").close()
        self._rate_lock = open(rate_lock_path, "r+")

        self.session = None
        self.athlete_id = None

    def init(self):
        if self.session is None:
            self._get_session()

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

    def _get_session(self):
        session = requests.Session()
        data = {
            "Username": self.username,
            "Password": self.password,
        }
        params = {}
        preResp = session.get("https://www.trainerroad.com/login",
                              params=params)
        if preResp.status_code != 200:
            raise Exception("SSO prestart error %s %s" %
                            (preResp.status_code, preResp.text))

        ssoResp = session.post("https://www.trainerroad.com/login",
                               params=params,
                               data=data, allow_redirects=False)
        if ssoResp.status_code != 302 or "temporarily unavailable" \
           in ssoResp.text:
            raise Exception("TRLogin error %s %s" % (
                ssoResp.status_code, ssoResp.text))
        session.headers.update(self._obligatory_headers)

        self.session = session
