from typing import Callable

import pandas as pd
from bokeh import *
import pandas_bokeh

from sidebar import *
from functions import *
from plots import plot_auc_curve, plot_precision_recall_curve, plot_score_distribution

from shiny import Inputs, Outputs, Session, reactive, module, render, ui
from shinywidgets import render_bokeh

__all__ = ['dashboard_ui', 'training_server', 'tools_ui', 'data_view_server']

main_dataframe = pd.read_csv('test_files/zDO_NOT_REMOVE.csv', skiprows=1)

# this variable increments every time a file is added. used to add labels to files.
file_count = 0

@module.ui
def dashboard_ui():
    return ui.nav_panel(
        "Dashboard",
        ui.layout_sidebar(
            ui.sidebar(
                ui.accordion(
                    ui.accordion_panel("Tools", tools_menu),  
                    ui.accordion_panel("Transform", transform_menu),  
                    ui.accordion_panel("Analysis", analysis_menu),  
                    ui.accordion_panel("Socket", "Section E content"),  
                    id="acc",  
                ),
                width="300px",
                open = "always"
            ),
            ui.layout_columns(
                ui.input_file(
                    "file1",
                    "Choose CSV File",
                    accept=[".csv"],
                    multiple=False,
                ),
                ui.input_action_button(
                    "load_dataset",
                    "Load Dataset"
                ),
                ui.input_action_button(
                    "export_excel",
                    "Export To Excel"
                ),
                ui.input_action_button(
                    "show_info",
                    "Information"
                ),
                col_widths=(3,3,3,3)
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Graph view"),
                    ui.output_plot("seaborn_plot"),
                    ui.card_footer(
                        ui.input_action_button(
                            "clear_data",
                            "Clear Data"
                        )
                    ),
                    height="60vh",
                ),
                ui.card(
                    ui.card_header("Data Panel"),
                    ui.div({"id": "datapanel_entries"}),
                    id = "datapanel",
                    max_height= "60vh",
                    class_="datapanel"
                ),
                ui.card(
                    ui.card_header("Result"),
                    ui.output_plot("score_dist"),  
                    height="40vh",              
                ),
                ui.card(
                    ui.card_header("Dataset panel"),
                    ui.div({"id": "datasetpanel_entries"})
                ),
                col_widths=(8,4)
            )
        )
    )


@module.server
def training_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: Callable[[], pd.DataFrame],
):
    @reactive.calc
    def parsed_file():
        # This function does two things: it reads the file input and converts it into a dataframe, 
        # and then also adds a data panel entry with the filename. moving the second function into 
        # a reactive.effect results in a program lockup.
        global main_dataframe
        global file_count
        file: list[FileInfo] | None = input.file1()
        if file is None:
            return main_dataframe
        tempfile = pd.read_csv(  # pyright: ignore[reportUnknownMemberType]
            file[0]["datapath"],
            skiprows=1,
        )
        tempfile['file'] = file[0]["name"]
        file_count += 1
        main_dataframe = pd.concat([main_dataframe, tempfile])

        filename = file[0]["name"]
        entry = ui.panel_well(
            f"{filename}"
        )
        ui.insert_ui(
            entry,
            selector= "#datapanel_entries",
            where="beforeEnd"
        )

        return main_dataframe
    
    @reactive.effect
    def clear_datapanel():
        global main_dataframe
        if input.clear_data() > 0:
            ui.remove_ui(selector="#datapanel_entries", multiple=True)
            ui.remove_ui(selector="#datasetpanel_entries", multiple=True)
            main_dataframe = pd.read_csv('test_files/zDO_NOT_REMOVE.csv', skiprows=1)

        

    @render.plot
    def seaborn_plot():
        return sns.relplot(
            data=parsed_file(),
            x="Wavelength [nm]",
            y="Intensity",
            hue="file",
            kind = "line",
            legend=False
        )
    
    # @render_bokeh
    # def interactive_plot():
    #     raise NotImplementedError("This is meant to plot a bokeh plot, but is incomplete. Use seaborn_plot() instead")
    
    @render.plot
    def score_dist():
        return plot_score_distribution(df())

    @render.plot
    def metric():
        if input.metric() == "ROC Curve":
            return plot_auc_curve(df(), "is_electronics", "training_score")
        else:
            return plot_precision_recall_curve(df(), "is_electronics", "training_score")


@module.ui
def tools_ui():
    return ui.nav_panel(
        "View Dataset",
        ui.layout_columns(
            ui.value_box(
                title="Row count",
                value=ui.output_text("row_count"),
                theme="primary",
            ),
            ui.value_box(
                title="Mean score",
                value=ui.output_text("mean_score"),
                theme="bg-green",
            ),
            gap="20px",
        ),
        ui.layout_columns(
            ui.card(ui.output_data_frame("data")),
            style="margin-top: 20px;",
        ),
    )


@module.server
def data_view_server(
    input: Inputs, 
    output: Outputs, 
    session: Session, 
    df: Callable[[], pd.DataFrame]
):
    @render.text
    def row_count():
        return df().shape[0]

    @render.text
    def mean_score():
        return round(df()["training_score"].mean(), 2)

    @render.data_frame
    def data():
        return df()

