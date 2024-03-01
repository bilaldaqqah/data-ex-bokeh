from bokeh.plotting import curdoc
from bokeh.layouts import column
from bokeh.themes import Theme
from ui_components import create_controls
from data_preprocessing import preprocess_data
from plot_creation import create_figure
from functools import lru_cache

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BokehApp:
    """
    A Bokeh application class that encapsulates the app's functionality, allowing for
    the creation, configuration, and updating of a Bokeh document.

    Attributes:
        df (DataFrame): The preprocessed data frame used for plotting.
        controls (WidgetBox): A collection of Bokeh widgets for user interaction.
        update_button (Button): A button widget for updating the plot based on user selections.
        plot_type_select (Select): A dropdown widget for selecting the plot type.
        x_col_select (Select): A dropdown widget for selecting the x-axis column.
        y_col_select (CheckboxGroup): A group of checkboxes for selecting one or more y-axis columns.
        agg_rule_select (Select): A dropdown for selecting the aggregation rule.
        group_by_select (Select): A dropdown for selecting the column to group data by.
        color_by_select (Select): A dropdown for selecting the column to color data by.
        layout (Column): The layout of the Bokeh application, including controls and the plot.
    """
    def __init__(self):
        """Initializes the BokehApp with default settings and configurations."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.logger.info("Initializing BokehApp...")
        self.df = preprocess_data("date", ["alphaT1"], initial=True)

        (
            self.controls, 
            self.update_button, 
            self.warning_div, 
            self.plot_type_select, 
            self.x_col_select, 
            self.y_col_select, 
            self.agg_rule_select, 
            self.group_by_select, 
            self.color_by_select
        ) = create_controls(self.df)
        
        self.layout = self.create_layout()

        # Wire up callbacks
        self.update_button.on_click(self.update)

    def get_layout(self):
        """Returns the layout of the Bokeh application."""
        return self.layout

    def create_layout(self):
        """Creates the initial layout for the Bokeh application."""
        self.logger.info("Creating initial layout...")

        initial_xcol = self.x_col_select.value
        initial_ycol = [self.y_col_select.labels[i] for i in self.y_col_select.active]
        initial_plots = create_figure(self.df, self.plot_type_select.value, self.x_col_select.value, initial_ycol)
        
        layout = column(self.controls, column(initial_plots))
        layout.margin = (0, 0, 0, 50)
        return layout

    @lru_cache(maxsize=32)
    def cached_create_figure(self, plot_type, x_col, y_col_str, agg_rule, group_by, color_by):
        """
        Creates a figure with caching to optimize performance for repeated calls with the same parameters.
        Caches the most recent 32 calls 
        """
        self.logger.info(f"Generating figure: plot_type={plot_type}, x_col={x_col}, agg_rule={agg_rule}, group_by={group_by}, color_by={color_by}")
        y_col = y_col_str.split(',')
        df = preprocess_data(x_col, y_col, group_by, color_by, agg_rule)
        return create_figure(df, plot_type, x_col, y_col, agg_rule, group_by, color_by)

    def update(self):
        """
        Updates the Bokeh plot based on user interactions. This method is triggered
        by the update button.
        """
        self.logger.info("Updating plot based on user interaction...")

        # check if group_by and color_by are distinct 
        if self.group_by_select.value == self.color_by_select.value and self.group_by_select.value and self.color_by_select:
            self.logger.warning("'group_by' and 'color_by' cannot be the same.")
            self.warning_div.text = "<p style='color: red; font-weight: bold; font-size: 20px;'>Warning: 'group_by' and 'color_by' cannot be the same. Please select different values.</p>"
            self.layout.children[1] = column() # Clear the existing plots as a precaution
        
        else:
            self.warning_div.text = ""
            new_plots = self.cached_create_figure(
                plot_type = self.plot_type_select.value, 
                x_col = self.x_col_select.value, 
                y_col_str = ','.join([self.y_col_select.labels[i] for i in self.y_col_select.active]),  
                agg_rule = self.agg_rule_select.value,  
                group_by = self.group_by_select.value,  
                color_by = self.color_by_select.value  
            )
            self.layout.children[1] = column(new_plots)

            # Log cache performance right after updating the plot
            cache_info = self.cached_create_figure.cache_info()
            self.logger.info(f"Cache hits: {cache_info.hits}, misses: {cache_info.misses}")


# create and add the app to the current document
app = BokehApp()
curdoc().add_root(app.get_layout())
