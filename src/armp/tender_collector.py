import requests
import time
import csv
import logging
import re
import os.path
from bs4 import BeautifulSoup
import bs4

# logging.basicConfig(filename= os.path.join(os.getcwd(), "../logs", "tender_collector.log"),
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.DEBUG)
logging.basicConfig()

in_file = "../owner-list-test.txt"
# in_file = "owner-list-unique-alphabetical.txt"
delay = 5  # in-between fetches
out_folder = "raw"
skip_owner_count = 266
max_failure_count = 10


def build_url(owner_id: str) -> str:
    """
    https://armp.cm/recherche_avancee?maitre_ouvrage=1761&region=0&departement=0
    """

    return f"https://armp.cm/recherche_avancee?maitre_ouvrage={owner_id}&region=0&departement=0"


def build_output_filename(in_url, folder_name) -> str:

    escaped_url = re.sub("[\\W]", "_", in_url)
    return os.path.join(folder_name, escaped_url+".html")


def save_content(content, out_filename: str):

    with open(out_filename, "w", encoding="utf-8") as f_html:
        f_html.write(content)


def get_next_url(soup: bs4.element.Tag) -> str:
    """
    :param content:
    :return:
    """

    #<a class="page-link" href="https://armp.cm/recherche_avancee?maitre_ouvrage=1761&amp;region=0&amp;departement=0&amp;page=2" rel="next" aria-label="Next &raquo;">&rsaquo;</a>

    next_url_tag = soup.find(attrs={"rel": "next"})

    if next_url_tag:

        return next_url_tag.get("href")

    return ""


def main():

    with open(in_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        ii = 0
        failure_count = 0
        for row in reader:

            if skip_owner_count > 0 and ii < skip_owner_count:
                ii += 1
                continue

            if len(row) < 2:
                logging.warning("Empty row, %s", row)
                continue

            url = build_url(row[1])

            while url:

                logging.info("Fetching from %s", url)
                r = requests.get(url)

                if r.status_code != 200:
                    failure_count += 1
                    logging.warning("Response code %s unexpected for %s, current failure count %s",
                                  r.status_code, url, failure_count)
                    if failure_count < max_failure_count:
                        time.sleep(60)
                        continue
                    else:
                        logging.error("Max failure count reached, exiting")
                        return

                failure_count = 0

                html_content = r.text

                html_filename = build_output_filename(url, out_folder)
                logging.info(f"Saving content to {html_filename}")

                save_content(html_content, html_filename)
                soup = BeautifulSoup(html_content, "html.parser")
                url = get_next_url(soup)

                time.sleep(delay)


if __name__ == "__main__":
    main()
