from typing import Callable

import pandas as pd
from sidebar import *
from plots import plot_auc_curve, plot_precision_recall_curve, plot_score_distribution

from shiny import Inputs, Outputs, Session, module, render, ui

__all__ = ['dashboard_ui', 'training_server', 'tools_ui', 'data_view_server']

@module.ui
def dashboard_ui():
    return ui.nav_panel(
        "Dashboard",
        ui.layout_columns(
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
            col_widths=(3,3,3,3)
        ),
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
                ui.card(
                    ui.card_header("Graph view"),
                    ui.output_plot("metric"),
                    ui.input_select(
                        "metric",
                        "Metric",
                        choices=["ROC Curve", "Precision-Recall"],
                    ),
                    height="40vh",
                ),
                ui.card(
                    ui.card_header("Data Panel"),
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

