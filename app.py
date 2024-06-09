from pathlib import Path

import pandas as pd
from src.modules import *
from src.sidebar import *

from shiny import App, Inputs, Outputs, Session, reactive, ui

df = pd.read_csv(Path(__file__).parent / "test_files/scores.csv")



app_ui = ui.page_navbar(
    dashboard_ui("tab1"),
    tools_ui("tab2"),
    header=ui.include_css(Path(__file__).parent / "css/styles.css"),
    id="tabs",
    title="Chemometrics Toolbox",
)


def server(input: Inputs, output: Outputs, session: Session):

    training_server(id="tab1")

    #These functions should bring up pop-ups
    @reactive.event(input.load_data)
    def load():
        return
    
    @reactive.event(input.load_dataset)
    def load():
        return
    
    @reactive.event(input.export_excel)
    def load():
        return
    
    @reactive.event(input.show_info)
    def load():
        return


app = App(app_ui, server)
