from typing import Callable

import pandas as pd
from bokeh import *
import pandas_bokeh

from src.read_files import load_data, load_dataset
from src.sidebar import *
from src.functions import *
from src.plots import plot_score_distribution

from shiny import Inputs, Outputs, Session, reactive, module, render, ui
from shinywidgets import render_bokeh

__all__ = ['dashboard_ui', 'training_server', 'tools_ui', 'data_view_server']

default_data = load_data(r'test_files/AS.csv', "AS.csv")
default_dataset = load_data(r'test_files/Book1.csv', "Book1.csv")
datapanel = {"AS":default_data}
datapanelIndex = {"AS":"AS"}
datasetpanel = {"Book1": default_dataset}
datasetpanelIndex = {"Book1":"Book1"}

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
                        choices=datasetpanelIndex,
                        selected="Book1"
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
    df = reactive.Value(default_data)

    @reactive.calc()
    def parsed_file() -> pd.DataFrame:
        file: list[FileInfo] | None = input.loadData()
        if file is None:
            return df.get()
        read_data = load_data(file[0]["datapath"], file[0]['name'])
        print(read_data)
        datapanel.update({read_data[2]:read_data})
        datapanelIndex.update({read_data[2]:read_data[2]})
        return read_data
    
    # same thing just for datasets.
    @reactive.calc()
    def parsed_dataset() -> pd.DataFrame:
        file: list[FileInfo] | None = input.loadDataset()
        if file is None:
            return df.get()
        read_data = load_dataset(file[0]["datapath"], file[0]["name"])
        print(read_data)
        datasetpanel.update({read_data[3]:read_data})
        datasetpanelIndex.update({read_data[3]:read_data[3]})
        return read_data
    
    @reactive.effect
    @reactive.event(input.loadData)
    def update_load_data():
        print("updating data select")
        global datapanel
        read_data = parsed_file()
        ui.update_select("datapanel", choices=datapanelIndex, selected=read_data[2])
        index = ''.join(input.datapanel()).replace(',', '')
        selected_data = datapanel[index]
        df.set(selected_data)

    @reactive.effect
    @reactive.event(input.loadDataset)
    def update_load_data():
        print("updating dataset select")
        global datasetpanel
        read_data = parsed_dataset()
        ui.update_select("datasetpanel", choices=datapanelIndex, selected=read_data[3])
        index = ''.join(input.datasetpanel()).replace(',', '')
        selected_data = datasetpanel[index]
        df.set(selected_data)
    
    @reactive.effect
    @reactive.event(input.datapanel)
    def update_select_data():
        index = ''.join(input.datapanel()).replace(',', '')
        selected_data = datapanel[index]
        df.set(selected_data)

    @reactive.effect
    @reactive.event(input.datasetpanel)
    def update_select_data():
        index = ''.join(input.datasetpanel()).replace(',', '')
        selected_data = datasetpanel[index]
        df.set(selected_data)
    
    @reactive.effect
    def clear_datapanel():
        # this function removes ui and resets the dataframe every time the clear data button is pressed.
        global default_data
        global file_count
        if input.clear_data() > 0:
            ui.remove_ui(selector="div#datapanel_entries div", multiple=True)
            ui.remove_ui(selector="div#datasetpanel_entries div", multiple=True)
            df.set(default_data)
            file_count = 0
            
    @render.plot
    def plot_fig():
        plot_data = df.get()
        fig, ax = plt.subplots()
        ax.plot(plot_data[0], plot_data[1])
        ax.set_xlabel('Wavelength in micrometer')
        ax.set_ylabel('RAW ADC Spectra')
        return fig
        # plt.plot(plot_data[0], plot_data[1])
        # plt.legend()
        # plt.title('RAW ADC Spectra')
        # plt.xlabel('Wavelength in micrometer')
    

# Boilerplate
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