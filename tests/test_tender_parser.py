from unittest import TestCase
from src.armp.tender_parser import map_key, extract_owner_id, filter_html_and_sort, get_publication_type, \
    get_tous_les_avis, parse_one_avis
from bs4 import BeautifulSoup


class Test(TestCase):
    def test_map_key(self):
        self.assertEqual("owner_short", map_key("mo/ac"))
        self.assertEqual("owner_short", map_key("po/ca"))
        self.assertEqual("type", map_key("Type :"))
        self.assertEqual("end_time", map_key("heure de clôture : "))
        self.assertEqual("publish_date_time", map_key("Published on the : "))
        self.assertEqual("details", map_key("Details : "))
        self.assertEqual("details", map_key("Détails : "))

        sth_weird = "pure random key"

        self.assertEqual(sth_weird, map_key(sth_weird))

    def test_extract_owner_id(self):
        self.assertEqual("3", extract_owner_id(
            "https___armp_cm_recherche_avancee_maitre_ouvrage_3_region_0_departement_0_page_10.html"
        ))

        self.assertEqual("1761", extract_owner_id(
            "https___armp_cm_recherche_avancee_maitre_ouvrage_1761_region_0_departement_0.html"
        ))

    def test_filter_html_and_sort(self):
        unordered = ["x.html", "skip1.txt", "c.html", "skip2", "d.html"]

        self.assertListEqual(["c.html", "d.html", "x.html"], filter_html_and_sort(unordered))

    def test_clean_title(self):
        a = """PUBLIC                                             
IMPUTATION : 94 709 05 110000 2279
MONTANT : SOIXANTE-DIX-NEUF MILLIONS (79 
        """

    def test_get_publication_type(self):
        in_url = "https://armp.cm/details?type_publication=ADDITIF&id_publication=1335"
        self.assertEqual("ADDITIF", get_publication_type(in_url))

        in_url = "https://armp.cm/details?type_publication=DEC-ATTR&id_publication=3607"
        self.assertEqual("DEC-ATTR", get_publication_type(in_url))

        in_url = "https://armp.cm/details?type_publication=DEC-INF&id_publication=363"
        self.assertEqual("DEC-INF", get_publication_type(in_url))

    def test_tous_les_avis(self):

        in_filename = "marches-with-TF.html"

        with open(in_filename, "r", encoding="utf-8") as f:

            soup = BeautifulSoup(f.read(), 'html.parser')

            avis_list = get_tous_les_avis(soup)

            self.assertEqual(10, len(avis_list))

        in_filename = "zina-page-2-less-than-10.html"

        with open(in_filename, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

            avis_list = get_tous_les_avis(soup)

            self.assertEqual(4, len(avis_list))

    def test_avis_parser(self):

        in_filename = "tender-en-p2-2021-11-11.html"

        with open(in_filename, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

            avis_list = get_tous_les_avis(soup)

            self.assertEqual(10, len(avis_list))

            avis_2 = parse_one_avis(avis_list[2])

            self.assertEqual('111072000', avis_2['cost'])

            self.assertEqual(
                'http://pridesoft.armp.cm//0903_dao_dl?type_publication=AO&id_publication=31018',
                avis_2['dao']
            )

            self.assertEqual(
                'https://armp.cm/details?type_publication=AO&id_publication=31018',
                avis_2['details']
            )
            self.assertEqual('RGAE & BUCREP', avis_2['owner_short'])

            avis_6 = parse_one_avis(avis_list[6])

            self.assertEqual('', avis_6['cost'])
            self.assertEqual('CENTER', avis_6['region'])
            self.assertEqual('MAIRE D\'OKOLA', avis_6['owner_short'])
