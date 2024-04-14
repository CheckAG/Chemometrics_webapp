from typing import Callable

import pandas as pd
from plots import plot_auc_curve, plot_precision_recall_curve, plot_score_distribution

from shiny import Inputs, Outputs, Session, module, render, ui

__all__ = ['dashboard_ui', 'training_server', 'tools_ui', 'data_view_server',
           'transform_ui', 'transform_server', 'analysis_ui', 'analysis_server',
           'operations_ui', 'operations_server']

@module.ui
def dashboard_ui():
    return ui.nav_panel(
        "Dashboard",
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
            col_widths=(8,4),
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
        "Tools",
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


@module.ui
def transform_ui():
    return ui.nav_panel(
        "Transform",
        ui.layout_columns(
            ui.card(
                ui.card_header("placeholder 1"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 2"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 3"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 4"),
                height = "40vh"
            ),
            col_widths=(6,6)
        )
    )

@module.server
def transform_server(
    input: Inputs, 
    output: Outputs, 
    session: Session
):
    return


@module.ui
def analysis_ui():
    return ui.nav_panel(
        "Analysis",
        ui.layout_columns(
            ui.card(
                ui.card_header("placeholder 1"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 2"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 3"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 4"),
                height = "40vh"
            ),
            col_widths=(6,6)
        )
    )

@module.server
def analysis_server(
    input: Inputs, 
    output: Outputs, 
    session: Session
):
    return


@module.ui
def operations_ui():
    return ui.nav_panel(
        "Arithmetic",
        ui.layout_columns(
            ui.card(
                ui.card_header("placeholder 1"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 2"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 3"),
                height = "40vh"
            ),
            ui.card(
                ui.card_header("placeholder 4"),
                height = "40vh"
            ),
            col_widths=(6,6)
        )
    )

@module.server
def operations_server(
    input: Inputs, 
    output: Outputs, 
    session: Session
):
    return