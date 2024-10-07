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

    ret = "\n".join(regulated_lines)
    return ret.strip()


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
                "applicant_email": [],
                "applicant_home_phone": [],
                "applicant_mobile_phone": [],
                "applicant_fax": [],
                "applicant_others": [],
                "licensed_professional_email": [],
                "licensed_professional_home_phone": [],
                "licensed_professional_mobile_phone": [],
                "licensed_professional_fax": [],
                "licensed_professional_others": [],
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

                            # parse applicant information
                            applicant = regulate_str(info.get("applicant", ""))
                            if applicant != "":
                                lines = applicant.split("\n")
                                for i, line in enumerate(lines):
                                    if "@" in line.strip():
                                        store_info["applicant_email"] = (
                                            line.strip().strip(".")
                                        )
                                        applicant = applicant.replace(line, "")
                                    if line.strip() == "Home Phone:":
                                        if "@" not in lines[i + 1]:
                                            store_info["applicant_home_phone"] = lines[
                                                i + 1
                                            ].strip()
                                            applicant = applicant.replace(
                                                line, ""
                                            ).replace(lines[i + 1], "")
                                    if line.strip() == "Mobile Phone:":
                                        if "@" not in lines[i + 1]:
                                            store_info["applicant_mobile_phone"] = (
                                                lines[i + 1].strip()
                                            )
                                            applicant = applicant.replace(
                                                line, ""
                                            ).replace(lines[i + 1], "")
                                    if line.strip() == "Fax:":
                                        if "@" not in lines[i + 1]:
                                            store_info["applicant_fax"] = lines[
                                                i + 1
                                            ].strip()
                                            applicant = applicant.replace(
                                                line, ""
                                            ).replace(lines[i + 1], "")

                            store_info["applicant_others"] = regulate_str(applicant)

                            # parse licensed_professional information
                            licensed_professional = regulate_str(
                                info.get("licensed_professional", "")
                            )
                            if licensed_professional != "":
                                lines = licensed_professional.split("\n")
                                for i, line in enumerate(lines):
                                    if "@" in line.strip():
                                        store_info["licensed_professional_email"] = (
                                            line.strip().strip(".")
                                        )
                                        licensed_professional = (
                                            licensed_professional.replace(line, "")
                                        )
                                    if line.strip() == "Home Phone:":
                                        if "@" not in lines[i + 1]:
                                            store_info[
                                                "licensed_professional_home_phone"
                                            ] = lines[i + 1].strip()
                                            licensed_professional = (
                                                licensed_professional.replace(
                                                    line, ""
                                                ).replace(lines[i + 1], "")
                                            )
                                    if line.strip() == "Mobile Phone:":
                                        if "@" not in lines[i + 1]:
                                            store_info[
                                                "licensed_professional_mobile_phone"
                                            ] = lines[i + 1].strip()
                                            licensed_professional = (
                                                licensed_professional.replace(
                                                    line, ""
                                                ).replace(lines[i + 1], "")
                                            )
                                    if line.strip() == "Fax:":
                                        if "@" not in lines[i + 1]:
                                            store_info["licensed_professional_fax"] = (
                                                lines[i + 1].strip()
                                            )
                                            licensed_professional = (
                                                licensed_professional.replace(
                                                    line, ""
                                                ).replace(lines[i + 1], "")
                                            )

                            store_info["licensed_professional_others"] = regulate_str(
                                licensed_professional
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
