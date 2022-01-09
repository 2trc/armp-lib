from unittest import TestCase
from src.armp.tender_collector import build_url, build_output_filename, get_next_url
import os.path
from bs4 import BeautifulSoup


class Test(TestCase):

    def test_build_output_filename(self):
        url = "https://armp.cm/recherche_avancee?maitre_ouvrage=1761&region=0&departement=0&page=3"

        self.assertEqual(os.path.join(".",
                                      "https___armp_cm_recherche_avancee_maitre_ouvrage_1761_region_0_departement_0_page_3.html"),
                         build_output_filename(url, "."))

        self.assertEqual(os.path.join("out", "a___recolte_prime__.html"),
                         build_output_filename("a://recolte_prime?&", "out"))

    def test_build_url(self):
        url = "https://armp.cm/recherche_avancee?maitre_ouvrage=1761&region=0&departement=0"

        self.assertEqual(url, build_url(1761))

    def test_get_next_url(self):

        in_filename = "mo-1761-anafoot.html"
        expected_next = "https://armp.cm/recherche_avancee?maitre_ouvrage=1761&region=0&departement=0&page=2"

        with open(in_filename, "r", encoding="utf-8") as f:

            soup = BeautifulSoup(f.read(), 'html.parser')

            self.assertEqual(expected_next, get_next_url(soup))

        in_filename = "marches-with-TF.html"
        expected_next = "https://armp.cm?page=5"

        with open(in_filename, "r", encoding="utf-8") as f:

            soup = BeautifulSoup(f.read(), 'html.parser')

            self.assertEqual(expected_next, get_next_url(soup))

        in_filename = "one_page_2058.html"
        expected_next = ""

        with open(in_filename, "r", encoding="utf-8") as f:

            soup = BeautifulSoup(f.read(), 'html.parser')

            self.assertEqual(expected_next, get_next_url(soup))



