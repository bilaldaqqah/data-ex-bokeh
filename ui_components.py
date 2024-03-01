import pandas as pd
from bokeh.models import CheckboxGroup, HoverTool, Select, Button, Div, Column, Row
from bokeh.layouts import column, row
from bokeh.palettes import Category10_10
from plot_creation import create_figure
from data_preprocessing import preprocess_data

def create_controls(df):
    plot_type_select = Select(title="Plot Type", value="Line", options=["Line", "Scatter"])
    x_col_select = Select(title="X Column", value="date", options=["date", "alphaT1", "returnT1"])
    y_col_select = CheckboxGroup(labels=["alphaT1", "returnT1"], active=[0])
    agg_rule_select = Select(title="Aggregation Rule", value=None, options=[None, "cumsum"])
    cols_without_date = [col for col in df.columns if col!= 'date']
    group_by_select = Select(title="Group By", value=None, options=[None, 'y-variable'] + cols_without_date)
    color_by_select = Select(title="Color By", value=None, options=[None, 'y-variable'] + cols_without_date)
    update_button = Button(label="Update", button_type="success")
    warning_div = Div(text="")
    controls = column(
        Div(text="<h1 style='text-align:center;'>Data Visualization Exercise</h1>"),
        Div(text="<b>Instructions:</b> Select options and click Update to visualize data."),
        plot_type_select,
        row(x_col_select, Column(Div(text="Y Column"), y_col_select)),
        row(agg_rule_select, group_by_select, color_by_select),
        update_button, 
        warning_div
    )
    return controls, update_button, warning_div, plot_type_select, x_col_select, y_col_select, agg_rule_select, group_by_select, color_by_select
