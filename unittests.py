import unittest
import config
from db import DatabaseController
from copernicus_api import CopernicusApi

class CopernicusExtractorTests(unittest.TestCase):
    # CopernicusApi Tests
    def test_copernicus_api_1(self):
        # tests if token is valid,
        # does the function return True as the first element in the returned tuple
        target = True
        copernicus_api = CopernicusApi(False)
        valid_token = "__5BxhCo_BB_gVwZJPH55UdnB-Zr_8eZIi9DOzS8Zrt6g__"
        url = f"https://download.regional.atmosphere.copernicus.eu/services/CAMS50?token={valid_token}&grid=0.1&model=ENSEMBLE&package=ANALYSIS_CO_SURFACE&time=-24H-1H&referencetime=2020-03-27T00:00:00Z&format=GRIB2"
        res = copernicus_api.execute_request(url)
        self.assertEqual(target, res[0])

    def test_copernicus_api_2(self):
        # tests if token is invalid,
        # does the function return False as the first element in the returned tuple
        target = False
        copernicus_api = CopernicusApi(False)
        valid_token = "TOKEN_INVALID"
        url = f"https://download.regional.atmosphere.copernicus.eu/services/CAMS50?token={valid_token}&grid=0.1&model=ENSEMBLE&package=ANALYSIS_CO_SURFACE&time=-24H-1H&referencetime=2020-03-27T00:00:00Z&format=GRIB2"
        res = copernicus_api.execute_request(url)
        self.assertEqual(target, res[0])

    def test_copernicus_api_3(self):
        # tests if token is invalid,
        # does the function return False as the second element in the returned Tuple is None
        target = False
        copernicus_api = CopernicusApi(False)
        valid_token = "TOKEN_INVALID"
        url = f"https://download.regional.atmosphere.copernicus.eu/services/CAMS50?token={valid_token}&grid=0.1&model=ENSEMBLE&package=ANALYSIS_CO_SURFACE&time=-24H-1H&referencetime=2020-03-27T00:00:00Z&format=GRIB2"
        res = copernicus_api.execute_request(url)
        self.assertEqual(None, res[1])


    def test_copernicus_api_4(self):
        target = True
        copernicus_api = CopernicusApi(False)
        files = copernicus_api.get_grib_data("PM10")
        self.assertEqual(target, len(files) >= 1)

    def test_db_controller_1(self):
        # tests successful connection to database with valid password
        db_controller = DatabaseController()
        target = 200
        res = db_controller.initialise_connection()
        self.assertEqual(target, res)

    def test_db_controller_2(self):
        #tests unsuccessful connection to database with 3 attempts
        db_controller = DatabaseController()
        target = -1
        res = db_controller.initialise_connection()
        self.assertEqual(target, res)

    def test_db_controller_3(self):
        # tests the path_leaf method to extract a file name from it's path
        db_controller = DatabaseController()
        path = "/home/evan/Downloads/pm10_test.grib2"
        target = "pm10_test.grib2"
        self.assertEqual(target, db_controller.path_leaf(path))


if __name__ == "__main__":
    unittest.main()
