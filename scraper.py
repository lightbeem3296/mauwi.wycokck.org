import argparse
import json
import os
from http import HTTPStatus
from pathlib import Path
from typing import Optional

import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger

urllib3.disable_warnings()

COOKIE = ""

CUR_DIR = Path(__file__).parent
INDEX_DIR = CUR_DIR / "index"
OUTPUT_DIR = CUR_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


BASE_URL = "https://mauwi.wycokck.org"


def fetch(permit_number: str, link: str) -> Optional[BeautifulSoup]:
    ret = None

    url = BASE_URL + link
    resp = requests.get(
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        },
    )
    if resp.status_code == HTTPStatus.OK:
        ret = BeautifulSoup(resp.text, "html.parser")
    else:
        logger.error(f"request error: {resp.status_code}")

    return ret


def parse(permit_number: str, soap: BeautifulSoup):
    store_info = {}
    store_info["permit_number"] = permit_number
    store_info["work_location"] = soap.select_one(
        "div#divWorkLocationInfo"
    ).text.strip()
    elems = soap.select("td.td_parent_left")
    for elem in elems:
        tag = elem.select_one("h1").text.strip().lower().replace(" ", "_")
        content = elem.select_one("span").text.strip()
        store_info[tag] = content
    output_file_path = OUTPUT_DIR / f"{permit_number}.json"
    with output_file_path.open("w") as file:
        json.dump(store_info, file, indent=2)


def work(start: int, count: int):
    try:
        fnames = os.listdir(INDEX_DIR)
        for i, fname in enumerate(fnames):
            if i < start:
                continue
            if i >= start + count:
                continue

            logger.info(f"{i}: {fname}")
            fpath = INDEX_DIR / fname
            with fpath.open("r") as file:
                info = json.load(file)
                permit_number = info["permit_number"]
                if fname.startswith(permit_number):
                    logger.info("already done")
                    continue

                soap = fetch(permit_number=info["permit_number"], link=info["link"])
                if soap is not None:
                    parse(permit_number=info["permit_number"], soap=soap)
                else:
                    logger.error("soap is None")

    except Exception as ex:
        logger.exception(ex)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start",
        dest="start",
        type=int,
        default=0,
        required=False,
        help="Start category index. Default is 0.",
    )
    parser.add_argument(
        "--count",
        dest="count",
        type=int,
        default=0,
        required=False,
        help="Category count. Default is 0 which means all the following categories.",
    )
    args = parser.parse_args()

    work(start=args.start, count=args.count)
    input("Press ENTER to exit.")


if __name__ == "__main__":
    main()
