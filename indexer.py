import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
INDEX_DIR_PATH = CUR_PATH / "index"
INDEX_DIR_PATH.mkdir(parents=True, exist_ok=True)

HOME_LINK = "https://mauwi.wycokck.org/CitizenAccess/Cap/CapHome.aspx?module=Building&TabName=Building&TabList=Home%7C0%7CBuilding%7C1%7CEnforce%7C2%7CLicenses%7C3%7CPlanning%7C4%7CCurrentTabIndex%7C1"


def work(year: int):
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Start date
        start_date = datetime(year=year, month=1, day=1)

        # End date (current date)
        end_date = datetime.now()

        # Generate and print each date from start to end
        current_date = start_date
        while current_date <= end_date:
            try:
                if current_date.year > year:
                    break

                date_str = current_date.strftime("%m/%d/%Y")
                logger.info(f"date: {date_str}")

                output_fname = date_str.replace("/", "-") + ".jsonl"
                output_fpath = INDEX_DIR_PATH / output_fname

                already_done = False
                if output_fpath.is_file():
                    with output_fpath.open("r") as file:
                        try:
                            damaged = False
                            for line in file:
                                info = json.loads(line)
                                if "permit_number" not in info:
                                    damaged = True
                                    break
                                if "link" not in info:
                                    damaged = True
                                    break
                            if not damaged:
                                already_done = True
                                logger.info("already done")
                        except:  # noqa: E722
                            pass

                if not already_done:
                    page.goto(HOME_LINK, wait_until="networkidle")

                    # fill query field
                    page.eval_on_selector(
                        "input#ctl00_PlaceHolderMain_generalSearchForm_txtGSStartDate",
                        f'el => el.value = "{date_str}"',
                    )
                    page.eval_on_selector(
                        "input#ctl00_PlaceHolderMain_generalSearchForm_txtGSEndDate",
                        f'el => el.value = "{date_str}"',
                    )
                    # click search button
                    page.query_selector("a#ctl00_PlaceHolderMain_btnNewSearch").click()

                    index_list = []
                    page_number = 0
                    while True:
                        logger.info(f"{date_str}, page_number: {page_number}")

                        # wait for page loading
                        page.wait_for_load_state(state="networkidle")
                        display_style = ""
                        while display_style != "none":
                            display_style = page.evaluate("""() => {
                                const element = document.querySelector('#divGlobalLoading');
                                return window.getComputedStyle(element).display;
                            }""")
                            time.sleep(0.1)
                        time.sleep(0.5)

                        # fetch table rows
                        elems = page.query_selector_all('td[style="width:110px;"]')
                        if len(elems) == 0:
                            break

                        # iterate rows
                        for elem in elems:
                            permit_number = elem.inner_text().strip()
                            link = elem.query_selector("a").get_attribute("href")

                            index_list.append(
                                {
                                    "permit_number": permit_number,
                                    "link": link,
                                }
                            )

                        # click next button
                        page_btns = page.query_selector_all(
                            "a.aca_simple_text.font11px"
                        )
                        if len(page_btns) >= 1:
                            next_btn = page_btns[-1]
                            if "Next" in next_btn.inner_text():
                                next_btn.click()
                            else:
                                break
                        else:
                            break

                        page_number += 1

                    with output_fpath.open("w") as file:
                        for index in index_list:
                            file.write(json.dumps(index) + "\n")

            except Exception as ex:
                logger.exception(ex)

            current_date += timedelta(days=1)

        context.close()
        browser.close()


def main():
    try:
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                year = int(arg)
                work(year=year)
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
