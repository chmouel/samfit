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
import requests


# curl 'https://tpapi.trainingpeaks.com/exerciselibrary/v1/libraries'
# -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Accept-Language: en,en-US;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/json'


class TPSession(object):
    categories = []
    _obligatory_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:71.0) Gecko/20100101 Firefox/71.0",
        "Origin": "https://app.trainingpeaks.com",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://app.trainingpeaks.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }

    def __init__(self, token):
        self.token = token

    def __getattr__(self, name):
        def _(*args, **kwargs):
            return self.session(name, *args, **kwargs)

        return _

    def session(self, name, *args, **kwargs):
        path = args[0]
        print(path)
        headers = self._obligatory_headers
        headers.update({"Authorization": "Bearer " + self.token})
        s = requests.Request(
            name.upper(),
            f"https://app.trainingpeaks.com/{path}",
            headers=headers,
            *args[1:],
            **kwargs,
        )
        print(s)
        return s
