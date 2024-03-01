import pandas as pd
import logging
import os
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def preprocess_data(x_col, y_col, group_by=None, color_by=None, agg_rule=None, initial=False):
    """
    loads a CSV file named 'test_data.csv' and preprocesses it based on the specified parameters.

    Preprocessing Rules:
        1. data loading: load the CSV file named 'test_data.csv'.
        2. Filtering: Include the 'x_col' and 'y_col' columns in the DataFrame, and Include the 'group_by' and 'color_by' columns if they are specified and present in the DataFrame.
        3. Datetime Conversion: convert the 'date' column to datetime objects.
        4. sorting (optional): sort the DataFrame by the 'x_col' column if the aggregation rule ('agg_rule') is set to 'cumsum' and the 'x_col' column is not already monotonically increasing.
        5. categorical conversion: Convert the 'securityId' and 'industryId' columns to categorical data types.
    """
    try:
        # print( os.listdir(os.getcwd()))
        df = pd.read_csv('bigger_test_data.csv')
        print(len(df))
        # print("bigger")

        #filter the DataFrame Based on Selected Variables
        if not initial:
            required_columns = {x_col} | set(y_col)  # Start with x_col and y_col
            # Add group_by and color_by to required_columns if either is not 'y-variable'
            if group_by and group_by in df.columns:
                required_columns.add(group_by)
            if color_by and color_by in df.columns:
                required_columns.add(color_by)
            df = df[list(required_columns.intersection(df.columns))]

        #convert 'date' column to datetime object
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        #convert securityId and industryId to categorical columns
        if 'securityId' in df.columns:
            df['securityId'] = df['securityId'].astype('category')
        if 'industryId' in df.columns:
            df['industryId'] = df['industryId'].astype('category')
            
        #Sort the DataFrame if Necessary for Cumulative Sum
        if agg_rule == 'cumsum':
            if not df[x_col].is_monotonic_increasing:
                df.sort_values(by=x_col, inplace=True)

        return df
    
    except FileNotFoundError as e:
        logger.error(f"File 'test_data.csv' not found: {e}")
        raise 

    #Handle other exceptions 
    except Exception as e:
        logger.error(f"Error occurred during data preprocessing: {e}")

def group_data(df, group_by, color_by, x_col, y_col):
    """
    Groups the DataFrame based on the specified parameters.

    Parameters:
        df (DataFrame): The input DataFrame.
        group_by (str): Specifies how the data is grouped (either None, a column name, or 'y-variable').
        y_col (str or list): The column(s) representing the y-variable(s) for plotting.

    Returns:
        list of tuples or DataFrameGroupBy
    """
    if group_by == x_col or (group_by in y_col): 
        return [('', df)]
    try: 
        if group_by:
            if group_by == 'y-variable':
                return [(y_var, df) for y_var in y_col]
            return df.groupby(group_by, observed = False)
        else:
            return [('', df)]
    except Exception as e:
        print(e)
