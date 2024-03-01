import unittest
from unittest.mock import patch
import pandas as pd
from data_preprocessing import preprocess_data, group_data

class TestDataPreprocessing(unittest.TestCase):

    def test_data_filtering(self):
        """
        tests if data pre-filtering is done correctly based on only selected values 
        """
        df = pd.read_csv('test_data.csv')
        x_col, y_col, group_by = 'date', ['alphaT1'], 'industryId'
        result = preprocess_data(x_col, y_col, group_by)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue('industryId' in result.columns)
        self.assertTrue('securityId' not in result.columns)
        self.assertTrue('date' in result.columns)

    def test_cumulative_sum_sorting(self): 
        """
        test if data is sorted by x_col when agg_rule == 'cumsum'
        """
        #mock dataframe
        df_unsorted = pd.DataFrame({
            'date': ['2024-03-05', '2024-03-03', '2024-03-01'],
            'value': [10, 20, 30]
        })
        x_col, y_col, agg_rule = 'date', ['value'], 'cumsum'
        result = preprocess_data(x_col, y_col, agg_rule=agg_rule, initial=True)
        sorted_dates = result['date'].tolist()
        self.assertEqual(sorted_dates, sorted(sorted_dates))

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_file_not_found_error(self, mock_read_csv):
        """
        Test FileNotFoundError when the file doesn't exist.
        mock_read_csv: Mock object for pd.read_csv.
        """
        x_col, y_col, group_by = 'date', ['alphaT1'], 'industryId'
        with self.assertRaises(FileNotFoundError):
            preprocess_data(x_col, y_col, group_by=group_by)

class TestGroupData(unittest.TestCase):
    """Test cases for the group_data function."""

    def setUp(self):
        """mock DataFrame for testing."""
        self.df = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=10),
            'industryId': ['A', 'A', 'B', 'B', 'C', 'C', 'A', 'A', 'B', 'B'],
            'securityId': ['X', 'Y', 'X', 'Y', 'X', 'Y', 'X', 'Y', 'X', 'Y'],
            'value': [10, 20, 15, 25, 30, 40, 35, 45, 50, 60]
        })

    def test_group_by_column(self):
        """Test grouping by a specified column."""
        group_by = 'industryId'
        color_by = 'securityId'
        y_col = 'value'

        result = group_data(self.df, group_by, color_by, y_col)

        self.assertIsInstance(result, pd.core.groupby.generic.DataFrameGroupBy)

    def test_group_by_y_variable(self):
        """Test grouping by 'y-variable'."""
        group_by = 'y-variable'
        color_by = 'securityId'
        y_col = ['value']
        result = group_data(self.df, group_by, color_by, y_col)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(y_col))

    def test_no_grouping(self):
        """Test no grouping (group_by=None)."""
        group_by = None
        color_by = 'securityId'
        y_col = 'value'
        result = group_data(self.df, group_by, color_by, y_col)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()
