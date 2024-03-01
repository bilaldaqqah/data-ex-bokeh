from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Div
from bokeh.palettes import Category10_10
from data_preprocessing import group_data
from bokeh.layouts import gridplot, column
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def add_hover(plot, x_col, y_col): 
    """
    Adds a hover tool to the Bokeh plot with appropriate formatting for tooltips when x_col is 'date'

    Parameters:
        plot (Bokeh Plot Object): The plot to which the hover tool will be added.
        x_col (str): The name of the column representing the x-variable.
        y_col (str): The name of the column representing the y-variable.

    Returns:
        None
    """
    try:
        if x_col == "date":
            tooltips = [(f'{x_col}', '@' + x_col + '{%Y-%m-%d}'), (f'{y_col}', f'@{y_col}')]
            hover = HoverTool(tooltips=tooltips, formatters={'@' + x_col: 'datetime'})
        else:
            tooltips = [(f'{x_col}', f'@{x_col}'), (f'{y_col}', f'@{y_col}')]
            hover = HoverTool(tooltips=tooltips)
        plot.add_tools(hover)
    except Exception as e:
        logger.error(f"Error occurred while adding hover tool: {e}")

def create_subplot(p, group_name, group_df, plot_type, x_col, y_col, agg_rule, group_by, color_by):
    """
    Creates a subplot based on the provided parameters.

    Parameters:
        p (Bokeh Plot Object): The subplot.
        group_name, group_df, plot_type, x_col, y_col, agg_rule, group_by, color_by:
            create_figure() parameters

    Returns:
        None
    """
    try:
        group_label = f"{group_by if group_by else ''} {group_name}"

        for i, y_var in enumerate(y_col):
            # print(i)
            if group_by == "y-variable" and y_var != group_name:
                continue
            colors = group_df.groupby(color_by, observed=False) if color_by else [(y_var, group_df)]
            for j, (color_name, color_group) in enumerate(colors):
                color_label = f"{color_by if color_by else ''} {color_name}"
                if agg_rule == 'cumsum':
                    color_group[y_var] = color_group[y_var].transform('cumsum')

                # convert color_group to ColumnDataSource
                source = ColumnDataSource(color_group)

                if plot_type == 'Line':
                    color = Category10_10[i] if not color_by else Category10_10[j]
                    line = p.line(x=x_col, y=y_var, source=source, legend_label=color_label, line_width=2, color=color)

                elif plot_type == 'Scatter':
                    p.scatter(x=x_col, y=y_var, source=source, legend_label=color_label, size=8, alpha=0.7, color=Category10_10[j])

                add_hover(p, x_col, y_var)

        p.xaxis.axis_label = x_col
        p.yaxis.axis_label = y_var
        p.title.text = group_label
    except Exception as e:
        logger.error(f"Error occurred while creating subplot: {e}")



def create_figure(df, plot_type, x_col, y_col, agg_rule=None, group_by=None, color_by=None):
    """
    Creates a Bokeh figure with subplots based on the provided parameters.

    Parameters:
        df (DataFrame): The input DataFrame.
        plot_type (str): The type of plot to create (either 'Line' or 'Scatter').
        x_col (str): The column representing the x-variable.
        y_col (str or list of str): The column(s) representing the y-variable(s) for plotting.
        agg_rule (str): The aggregation rule to apply (either None or 'cumsum', defaults to None).
        group_by (str): Specifies how the data is grouped (either None, a column name, or 'y-variable').
        color_by (str): The column used for coloring the plot (either None, a column name, or 'y-variable').

    Returns:
        layout (Column): The layout containing the Bokeh figure with subplots.
    """
    try:
        #if y_col is passed in as a string, convert it to a list for consistency
        if not isinstance(y_col, list):
            y_col = [y_col]

        color_by = None if color_by == 'y-variable' else color_by

        groups = group_data(df, group_by, color_by, x_col, y_col)        

        plots = []
        for group_name, group_df in groups:
            x_axis_type = 'datetime' if x_col == 'date' else 'linear'
            p = figure(width=600, height=400, title="", x_axis_type=x_axis_type)
            create_subplot(p, group_name, group_df, plot_type, x_col, y_col, agg_rule, group_by, color_by)
            plots.append(p)

        #  plot title
        title = f"{y_col[0] if len(y_col) == 1 else ', '.join(y_col[:-1]) + ' & ' + y_col[-1]} vs. {x_col}"
        page_title = Div(text=f"<h3>{title}</h3>", width=800, height=50)

        # arrange plot with title in grid 
        grid = gridplot(plots, ncols=2)
        layout = column(page_title, grid)

        return layout
    except Exception as e: 
        logger.error(f"Error occurred while creating figure: {e}")
