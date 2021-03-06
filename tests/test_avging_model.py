import unittest
from src.models.averaging_model import AvgModel
import pandas as pd


class TestAvgModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = AvgModel()
        cls.df = pd.DataFrame(
            [
                ["Annex", 1],
                ["Annex", 1],
                ["Annex", 1],
                ["Annex", 1],
                ["High Park", 2],
                ["High Park", 2],
                ["Bay St", 3],
            ], 
            columns=["neighbourhood", "nbhd_id"]
        )
    
    def test_preds(self):
        preds = self.model.predict(
            self.df, 365
        )
        pred_list = preds.expected_crimes_per_hour.round(3).tolist()
        assert [0.011, 0.005, 0.003] == pred_list


if __name__ == "__main__":
    unittest.main()