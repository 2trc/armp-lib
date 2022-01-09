import re
import bs4
from bs4 import BeautifulSoup
import os.path
import logging
import os
import csv
from urllib.parse import parse_qs, urlparse
from typing import Optional

# logging.basicConfig(filename= os.path.join(os.getcwd(), "../logs", "tender_parser.log"),
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.DEBUG)
logging.basicConfig()

def get_tous_les_avis(soup_in: bs4.element.Tag):
    tous_les_avis = soup_in.find(id="tout_les_avis")

    return tous_les_avis.find_all("li")


def map_key(key_in: str) -> str:

    key_in = key_in.lower().replace(":", "").strip()

    if "mo/ac" in key_in or "po/ca" in key_in:
        return "owner_short"
    elif "région" in key_in:
        return "region"
    elif "montant" in key_in or "amount" in key_in:
        return "cost"
    elif "publié" in key_in or 'published' in key_in:
        return "publish_date_time"
    elif "date de clôture" in key_in or "closing date" in key_in:
        return "end_date"
    elif "heure de clôture" in key_in or "closing time" in key_in:
        return "end_time"
    elif "détails" in key_in:
        return "details"
    elif 'tf' in key_in:
        return 'dao'
    elif key_in not in ["type", "dao", 'region', 'details']:
        # TODO
        logging.warning(f"Warning, unknown key: {key_in}")

    return key_in


def clean_title(in_title):
    return re.sub("[\\s*]", " ", in_title)


def clean_cost(in_cost):
    return re.sub("[a-zA-Z ]", "", in_cost)


def rel_to_full_link(in_link):

    if in_link.startswith("/"):
        return f"https://armp.cm{in_link}"
    return in_link


def get_publication_type(in_url: str) -> Optional[str]:

    query = urlparse(in_url).query

    query_dict = parse_qs(query)

    type_list = query_dict.get('type_publication')

    if len(type_list) > 0:
        return type_list[0]
    else:
        return None


def parse_one_avis(soup_in: bs4.element.Tag) -> dict:
    avis = dict()

    avis["title"] = clean_title(soup_in.strong.text.strip())

    rows = soup_in.find_all(class_="d-table-row")

    for row in rows[:-1]:
        divs = row.find_all("div")
        key = map_key(divs[0].text.strip())
        avis[key] = divs[1].text.strip()

    avis["cost"] = clean_cost(avis["cost"])

    links = soup_in.find_all(attrs={"role": "button"})

    # Détails, DAO, TF...
    for link in links:
        key = map_key(link.text.strip())
        avis[key] = link.get('href')

    avis["details"] = rel_to_full_link(avis.get("details"))
    avis["publication_type"] = get_publication_type(avis["details"])

    return avis


def extract_owner_id(one_file: str) -> str:
    a = re.match("[a-zA-Z_]*(\\d*).*", one_file)
    return a.group(1)


def filter_html_and_sort(in_list):
    return sorted(list(filter(lambda x: x.endswith(".html"), in_list)))


def save_avis(parsed_avis_list: list, folder_name: str, rel_file_name:str):

    joined_file_name = os.path.join(folder_name, rel_file_name)

    fieldnames = ["owner_id", "owner_short", "region", "type", "publication_type", "cost", "publish_date_time",
                  "end_date", "end_time", "title", "details", "tf", "dao"]

    with open(joined_file_name, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(parsed_avis_list)


#in_folder = "raw_local"
in_folder = "raw"
#out_folder = "parsed_data"
out_folder = "parsed"
skip_file_count = 0


def main():
    # loop through in_folder for each html
    logging.info("".ljust(80, "-"))
    logging.info("Starting the parsing process")
    logging.info("input dir: %s\noutput dir: %s", in_folder, out_folder)
    logging.info("".ljust(80, "-"))

    file_list = filter_html_and_sort(os.listdir(in_folder))

    f_count = len(file_list)

    logging.info("%d files to parse", f_count)

    ii = 0

    for one_file in file_list:
        # parse content to a list of dict
        logging.info("parsing %s", one_file)

        with open(os.path.join(in_folder,one_file), encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            les_avis = get_tous_les_avis(soup)

            parsed_avis_list = []

            owner_id = extract_owner_id(one_file)

            for avis in les_avis:
                parsed_avis = parse_one_avis(avis)
                parsed_avis["owner_id"] = owner_id
                parsed_avis_list.append(parsed_avis)

            # save list of dict to csv, figure out filename and add out_folder
            save_avis(parsed_avis_list, out_folder, one_file.replace(".html", ".csv"))

        ii += 1
        logging.info("%.1f%% done\n", 100.0*ii/f_count)


if __name__ == "__main__":
    main()
