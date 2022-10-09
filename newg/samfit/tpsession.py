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
import glob
import gzip
import json
import pathlib
import subprocess

from .config import BASE_DIR


def get_cache(obj: str, verbose: bool = False) -> dict | list | None:
    if "/" in obj:
        key = obj
    else:
        key = f"cache/{obj}"
    globpath = pathlib.Path(BASE_DIR) / f"{key}-*"
    tryglobs = glob.glob(globpath.as_posix())
    if not tryglobs:
        globpath = pathlib.Path(BASE_DIR) / f"{key}.*"
        tryglobs = glob.glob(globpath.as_posix())
    fpath = pathlib.Path(BASE_DIR) / "cache" / f"{obj}.json"
    if len(tryglobs) == 1:
        fpath = pathlib.Path(tryglobs[0])
    elif not obj:
        return None
    elif "/" in obj:
        fpath = pathlib.Path(BASE_DIR) / f"{obj}.json"

    if fpath.exists() and fpath.is_file():
        if verbose:
            print(f"Using cache {fpath}")
        if fpath.as_posix().endswith(".gz"):
            with gzip.open(fpath) as f:
                return json.load(f)
        else:
            return json.load(fpath.open(encoding="utf-8"))

    return None


def store_cache(cache_id: str, content: str, verbose: bool = False) -> None:
    fpath = pathlib.Path(BASE_DIR) / "cache" / f"{cache_id}.json.gz"
    if verbose:
        print(f"Storing cache: {fpath}")
    with gzip.open(fpath, "wb") as f:
        f.write(content)


def do_curl(
    token: str,
    url: str,
    method: str = "GET",
    as_json=False,
    return_retcode=False,
    cache_id: str = None,
    data: dict | list = None,
    test: bool = False,
    verbose: bool = False,
) -> str | dict | int:
    if cache_id and method == "GET":
        cached = get_cache(cache_id, verbose=verbose)
        if cached:
            return cached
    data_str = ""
    if data:
        data_str = json.dumps(data).replace("'", "")
        data_str = f"-d '{data_str}'"
        method = "POST"
    test_str = test and "echo " or ""
    method_str = f"-X {method.upper()}" if method.upper() != "GET" else ""
    command = f"""{test_str} curl -f 'https://tpapi.trainingpeaks.com/{url.lstrip("/")}' \
    {method_str} \
    {data_str} \
    -H 'Accept-Encoding: gzip, deflate, br' \
    -H 'Accept-Language: en,en-US;q=0.5' \
    -H 'Accept: application/json, text/javascript, */*; q=0.01' \
    -H 'Authorization: Bearer {token}' \
    -H 'Cache-Control: no-cache' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: application/json' \
    -H 'DNT: 1' \
    -H 'Origin: https://app.trainingpeaks.com' \
    -H 'Pragma: no-cache' \
    -H 'Referer: https://app.trainingpeaks.com/' \
    -H 'Sec-Fetch-Dest: empty' \
    -H 'Sec-Fetch-Mode: cors' \
    -H 'Sec-Fetch-Site: same-site' \
    -H 'TE: trailers' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0' """
    try:
        run = subprocess.run(command, check=True, shell=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if return_retcode:
            return e.returncode
        print(f"Error: {command}")
        raise e
    if return_retcode:
        return run.returncode
    if run.returncode != 0:
        raise Exception(f"Failed to run curl: {run.stdout}")
    if as_json and run.stdout == "":
        return {}
    elif as_json:
        if cache_id:
            store_cache(cache_id, run.stdout, verbose=verbose)
        return json.loads(run.stdout)
    else:
        return run.stdout
