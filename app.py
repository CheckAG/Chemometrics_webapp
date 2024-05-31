from pathlib import Path

import pandas as pd
from modules import *
from sidebar import *

from shiny import App, Inputs, Outputs, Session, reactive, ui



df = pd.read_csv(Path(__file__).parent / "scores.csv")
    


app_ui = ui.page_navbar(
    dashboard_ui("tab1"),
    tools_ui("tab2"),
    header=ui.include_css(Path(__file__).parent / "styles.css"),
    id="tabs",
    title="Chemometrics Toolbox",
)


def server(input: Inputs, output: Outputs, session: Session):
    # this is useless filler code, will be changed later
    @reactive.calc()
    def filtered_data() -> pd.DataFrame:
        return df.loc[df["account"] == input.account()]

    training_server(id="tab1", df=filtered_data)
    data_view_server(id="tab2", df=filtered_data)

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
