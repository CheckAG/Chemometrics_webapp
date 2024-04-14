from pathlib import Path

import pandas as pd
from modules import *

from shiny import App, Inputs, Outputs, Session, reactive, ui

df = pd.read_csv(Path(__file__).parent / "scores.csv")


app_ui = ui.page_navbar(
    dashboard_ui("tab1"),
    tools_ui("tab2"),
    transform_ui("tab3"),
    analysis_ui("tab4"),
    operations_ui("tab5"),
    sidebar=ui.sidebar(
        ui.input_select(
            "account",
            "Account",
            choices=[
                "Berge & Berge",
                "Fritsch & Fritsch",
                "Hintz & Hintz",
                "Mosciski and Sons",
                "Wolff Ltd",
            ],
        ),
         ui.input_action_button(
            "load_data",
            "Load Data"
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
        width="300px",
    ),
    header=ui.include_css(Path(__file__).parent / "styles.css"),
    id="tabs",
    title="Monitoring",
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc()
    def filtered_data() -> pd.DataFrame:
        return df.loc[df["account"] == "Hintz & Hintz"]

    training_server(id="tab1", df=filtered_data)
    data_view_server(id="tab2", df=filtered_data)
    transform_server(id="tab3")
    analysis_server(id="tab4")
    operations_server(id="tab5")

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
