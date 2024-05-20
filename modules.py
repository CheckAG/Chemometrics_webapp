from typing import Callable

import pandas as pd
from bokeh import *
import pandas_bokeh

from sidebar import *
from functions import *
from plots import plot_auc_curve, plot_precision_recall_curve, plot_score_distribution

from shiny import Inputs, Outputs, Session, reactive, module, render, ui

__all__ = ['dashboard_ui', 'training_server', 'tools_ui', 'data_view_server']

main_dataframe = pd.read_csv('zDO_NOT_REMOVE.csv', skiprows=1)

# this variable increments every time a file is added. used to add labels to files.
file_count = 1

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
                    ui.output_plot("theplot"),
                    height="40vh",
                ),
                ui.card(
                    ui.card_header("Data Panel"),
                    id = "datapanel",
                    max_height= "40vh"
                ),
                ui.card(
                    ui.card_header("Result"),
                    ui.output_plot("score_dist"),  
                    height="40vh",              
                ),
                ui.card(
                    ui.card_header("Dataset panel")
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
            f"{filename}",
            ui.input_checkbox(
                f"datapanel_{file_count}",
                "remove",
                False
            )
        )
        ui.insert_ui(
            entry,
            selector= "#datapanel",
            where="beforeEnd"
        )

        return main_dataframe
    
    @reactive.effect
    def removeDatapanelEntry():
        return


    @render.plot
    def theplot():
        return sns.relplot(
            data=parsed_file(),
            x="Wavelength [nm]",
            y="Intensity",
            hue="file",
            kind = "line",
            legend=False
        )
    
    # @render_bokeh
    # def mainplot():
    #     from bokeh.plotting import figure

    #     fig = figure(x_axis_label = "wavelength", y_axis_label = "Intensity")
    #     fig.line(
            
    #     )

    # @reactive.effect
    # def add_data_panel():
    #     global file_count
    #     file: list[FileInfo] | None = input.file1()
    #     if file is None:
    #         return
    #     filename = file[0]["name"]
    #     entry = ui.panel_well(
    #         f"{filename}",
    #         ui.input_checkbox(
    #             f"datapanel_{file_count}",
    #             "remove",
    #             False
    #         )
    #     )
    #     ui.insert_ui(
    #         entry,
    #         #datapanel,
    #         where="beforeEnd"
    #     )
    #     return

    
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

