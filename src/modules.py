from typing import Callable

import pandas as pd
from bokeh import *
import pandas_bokeh

from src.read_files import load_data
from src.sidebar import *
from src.functions import *
from src.plots import plot_score_distribution

from shiny import Inputs, Outputs, Session, reactive, module, render, ui
from shinywidgets import render_bokeh

__all__ = ['dashboard_ui', 'training_server', 'tools_ui', 'data_view_server']

main_dataframe = load_data('test_files\AS.csv')
datapanel = {"AS":main_dataframe}
datapanelIndex = {"AS":"AS"}
datasetpanel = {}
datasetpanelIndex = {}

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
                    "loadData",
                    "Choose Data file",
                    accept=[".csv", ".xls", ".xlsx"],
                    multiple=False,
                    button_label="loadData"
                ),
                ui.input_file(
                    "loadDataset",
                    "Choose Dataset file",
                    accept=[".csv", ".xls", ".xlsx"],
                    multiple=False,
                    button_label="loadDataSet"
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
                    ui.output_plot("plot_fig"),
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
                    ui.input_select(
                        id = "datapanel",
                        multiple=True,
                        label="Data Panel",
                        choices=datapanelIndex,
                        selected="AS"
                    ),
                    max_height= "60vh",
                    class_="datapanel"
                ),
                # this card just displays a filler graph
                ui.card(
                    ui.card_header("Result"),
                    height="40vh",              
                ),
                ui.card(
                    ui.card_header("Dataset panel"),
                    ui.div({"id": "datasetpanel_entries"}),
                    ui.input_select(
                        id = "datasetpanel",
                        multiple=True,
                        label="Data set Panel",
                        choices=datasetpanelIndex
                    ), 
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
):
    df = reactive.Value(main_dataframe)

    # this is useless filler code, will be changed later
    @reactive.calc
    def parsed_file() -> pd.DataFrame:
        file: list[FileInfo] | None = input.loadData()
        if file is None:
            return df.get()
        read_data = load_data(file[0]["datapath"])
        datapanel.update({read_data[2]:read_data})
        datapanelIndex.update({read_data[2]:read_data[2]})
        df.set(read_data)
        ui.update_select("datapanel", choices=datapanelIndex)
        return df.get()

    @reactive.effect
    @reactive.event(input.datapanel)
    @reactive.event(input.loadData)
    def update_select_data():
        print("updating data select")
        global datapanel
        parsed_file()
        index = ''.join(input.datapanel()).replace(',', '')
        selected_data = datapanel[index]
        df.set(selected_data)
    
    @reactive.effect
    def clear_datapanel():
        # this function removes ui and resets the dataframe every time the clear data button is pressed.
        global main_dataframe
        global file_count
        if input.clear_data() > 0:
            ui.remove_ui(selector="div#datapanel_entries div", multiple=True)
            ui.remove_ui(selector="div#datasetpanel_entries div", multiple=True)
            df.set(main_dataframe)
            file_count = 0
            
    @render.plot
    def plot_fig():
        plot_data = df.get()
        print(plot_data)
        fig, ax = plt.subplots()
        ax.plot(plot_data[0], plot_data[1])
        ax.set_xlabel('Wavelength in micrometer')
        ax.set_ylabel('RAW ADC Spectra')
        return fig
        # plt.plot(plot_data[0], plot_data[1])
        # plt.legend()
        # plt.title('RAW ADC Spectra')
        # plt.xlabel('Wavelength in micrometer')
    

# This whole page is just boilerplate, nothing has been implemented yet here.
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

