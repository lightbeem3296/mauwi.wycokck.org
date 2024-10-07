import time
import json
from pathlib import Path

from loguru import logger
from playwright.sync_api import sync_playwright

CUR_PATH = Path(__file__).parent
OUTPUT_PATH = CUR_PATH / "index"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

HOME_LINK = "https://mauwi.wycokck.org/CitizenAccess/Cap/CapHome.aspx?module=Building&TabName=Building&TabList=Home%7C0%7CBuilding%7C1%7CEnforce%7C2%7CLicenses%7C3%7CPlanning%7C4%7CCurrentTabIndex%7C1"


def work():
    with sync_playwright() as pw_ctx_man:
        browser = pw_ctx_man.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(HOME_LINK, wait_until="networkidle")

        # fill query field
        page.eval_on_selector(
            "input#ctl00_PlaceHolderMain_generalSearchForm_txtGSStartDate",
            'el => el.value = "01/01/2020"',
        )
        # click search button
        page.query_selector("a#ctl00_PlaceHolderMain_btnNewSearch").click()

        page_number = 0
        while True:
            try:
                logger.info(f"page_number: {page_number}")

                # fetch table rows
                page.wait_for_selector('td[style="width:110px;"]')
                time.sleep(0.5)
                elems = page.query_selector_all('td[style="width:110px;"]')
                if len(elems) == 0:
                    break

                # iterate rows
                for elem in elems:
                    permit_number = elem.inner_text().strip()
                    elem.wait_for_selector("a", state="attached")
                    link = elem.query_selector("a").get_attribute("href")

                    # save `permit_number` and `link``
                    output_file_path = OUTPUT_PATH / f"{permit_number}.json"
                    with output_file_path.open("w") as file:
                        json.dump(
                            {
                                "permit_number": permit_number,
                                "link": link,
                            },
                            file,
                        )

            except Exception as ex:
                logger.exception(ex)

            # click next button
            page.wait_for_selector("a.aca_simple_text.font11px", state="attached")
            page_btns = page.query_selector_all("a.aca_simple_text.font11px")
            next_btn = page_btns[-1]
            next_btn.click()

            # wait for page loading
            page.wait_for_load_state(state="networkidle")
            display_style = ""
            while display_style != "none":
                display_style = page.evaluate("""() => {
                    const element = document.querySelector('#divGlobalLoading');
                    return window.getComputedStyle(element).display;
                }""")
                time.sleep(0.1)

            page_number += 1

        context.close()
        browser.close()


def main():
    try:
        work()
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    main()
