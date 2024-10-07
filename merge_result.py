import json
import os
from pathlib import Path

import pandas as pd
from loguru import logger

CUR_DIR = Path(__file__).parent
OUTPUT_PATH = CUR_DIR / "output"
OUTPUT_SIMPLE_PATH = CUR_DIR / "output_simple"


def regulate_str(input_str: str) -> str:
    lines = input_str.splitlines()

    trimmed_lines = [line.strip() for line in lines]

    regulated_lines = []
    previous_line_empty = False

    for line in trimmed_lines:
        if line == "":
            if not previous_line_empty:
                regulated_lines.append(line)
            previous_line_empty = True
        else:
            regulated_lines.append(line)
            previous_line_empty = False

    return "\n".join(regulated_lines)


def merge():
    try:
        dst_fpath = CUR_DIR / "output.csv"

        res_df = pd.DataFrame(
            {
                "date": [],
                "permit_number": [],
                "permit_type": [],
                "status": [],
                "address": [],
                "short_notes": [],
                "link": [],
                "work_location": [],
                "applicant": [],
                "licensed_professional": [],
                "project_description": [],
            }
        )

        logger.info(f"[*] merge into > {dst_fpath}")
        file_number = 0
        for dpath, _, fnames in os.walk(OUTPUT_SIMPLE_PATH):
            for fname in fnames:
                if not fname.lower().endswith(".json"):
                    continue

                fpath = os.path.join(dpath, fname)
                logger.info(f"{file_number}: {fname}")
                with open(fpath, mode="r") as f:
                    simple_info: dict[str, str] = json.load(f)

                    permit_number = simple_info["permit_number"]

                    store_info = {}
                    store_info["date"] = simple_info["date"]
                    store_info["permit_number"] = permit_number
                    store_info["permit_type"] = simple_info["permit_type"]
                    store_info["status"] = simple_info["status"]
                    store_info["address"] = simple_info["address"]
                    store_info["short_notes"] = simple_info["short_notes"]

                    info_fpath = OUTPUT_PATH / f"{permit_number}.json"
                    if info_fpath.is_file():
                        with info_fpath.open("r") as info_file:
                            info: dict[str, str] = json.load(info_file)
                            store_info["link"] = "https://mauwi.wycokck.org" + info.get(
                                "link",
                                "",
                            )
                            store_info["work_location"] = regulate_str(
                                info.get(
                                    "work_location",
                                    "",
                                )
                            )
                            store_info["applicant"] = regulate_str(
                                info.get(
                                    "applicant",
                                    "",
                                )
                            )
                            store_info["licensed_professional"] = regulate_str(
                                info.get(
                                    "licensed_professional",
                                    "",
                                )
                            )
                            store_info["project_description"] = regulate_str(
                                info.get(
                                    "project_description",
                                    "",
                                )
                            )

                    res_df = pd.concat(
                        [res_df, pd.DataFrame([store_info])],
                        ignore_index=True,
                    )
                file_number += 1
        res_df.to_csv(dst_fpath, index=False)

    except Exception as ex:
        logger.exception(ex)


def main():
    try:
        merge()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
