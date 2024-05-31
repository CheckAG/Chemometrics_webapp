from typing import Callable

import pandas as pd
from bokeh import *
import pandas_bokeh

from sidebar import *
from functions import *
from plots import plot_score_distribution

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
                    "load_single_file",
                    "Choose Data",
                    accept=[".csv"],
                    multiple=False,
                ),
                ui.input_file(
                    "load_dataset_file",
                    "Choose Dataset",
                    accept=[".csv"],
                    multiple=False,
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
                # this card just displays a filler graph
                ui.card(
                    ui.card_header("Result"),
                    ui.output_plot("dataset_plot"),  
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
        # This function does two things: it reads the file input and adds it to the dataframe, 
        # and then also adds a datapanel ui element with the filename. moving the second function into 
        # a reactive.effect results in a program lockup because they both depend on the same reactive value.
        global main_dataframe
        global file_count
        file: list[FileInfo] | None = input.load_single_file()
        if file is None:
            return main_dataframe
        tempfile = pd.read_csv(  # pyright: ignore[reportUnknownMemberType]
            file[0]["datapath"],
            skiprows=1,
        )
        tempfile['file'] = file[0]["name"]
        file_count += 1
        new_dataframe = pd.concat([main_dataframe, tempfile])

        filename = file[0]["name"]
        entry = ui.panel_well(
            f"{filename}"
        )
        ui.insert_ui(
            entry,
            selector= "#datapanel_entries",
            where="beforeEnd"
        )

        return new_dataframe
    

    @reactive.calc
    def load_dataset():
        '''
        TODO:
        1) add a dataset panel ui that shows info about the dataset(size, shape, number of lines, etc.)
        2) Fix the code!!!! this doesn't work and needs to be fixed
        '''
        

        file2: list[FileInfo] | None = input.load_dataset_file()
        if file2 is None:
            df = pd.read_csv('test_files/another.csv', skiprows=1)
            filename = "lies"
        else:
            df = pd.read_csv(  # pyright: ignore[reportUnknownMemberType]
                file2[0]["datapath"],
                header=None,
                sep=',',
                skiprows=1
            )
            filename = file2[0]["name"]
            print("else block reached")


        dataset_csv = {}
        dataset_csv["wavelength"] = df.iloc[1:, 1].values.T.tolist()  # wavelength selecting all rows from 1 to end and all the columns till 0 to 1
        for i in range (1,len(df.axes[1]) - 1):
            data = df.iloc[1:, i].values.tolist()
            dataset_csv[f"sample{i}"] = data    
        # label = df.iloc[0:1, 1:].values.T  # label selecting first row and all the columns from 1 to end
        # dataset_csv = pd.DataFrame([Wavelength, data, label,filename], columns=["wavelength","data","label","filename"])
        df2 = pd.DataFrame(dataset_csv)
        df2_melted = df2.melt(id_vars = "wavelength",  var_name="sample", value_name = "absorbance")

        entry = ui.panel_well(
            f"{filename}"
        )
        ui.insert_ui(
            entry,
            selector= "#datasetpanel_entries",
            where="beforeEnd"
        )
        print("end of function")
        
        return df2_melted
    

    @reactive.effect
    def clear_datapanel():
        # this function removes ui and resets the dataframe every time the clear data button is pressed.
        global main_dataframe
        global file_count
        if input.clear_data() > 0:
            ui.remove_ui(selector="div#datapanel_entries div", multiple=True)
            ui.remove_ui(selector="div#datasetpanel_entries div", multiple=True)
            main_dataframe = pd.read_csv('test_files/zDO_NOT_REMOVE.csv', skiprows=1)
            file_count = 0
        

    # Seaborn plot. Works properly, no issues.
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
    
    @render.plot
    def dataset_plot():
        return sns.relplot(
            data = load_dataset(),
            x = "wavelength",
            y = "absorbance",
            hue = "sample",
            kind = "line",
            # legend = False
        )
    
    #Bokeh plot, does not display for some reason. show(p) returns a plot though so the code is correct.
    @render_bokeh
    def interactive_plot():
        from bokeh.plotting import figure,show, save
        data = parsed_file()
        p = figure(x_axis_label="Wavelength", y_axis_label="Intensity")
        p.line(x=[1,2,3,4,5,6], y= [2,4,6,8,10,12])  #change this to use dataframe after getting it working
        return p

    # placeholder
    @render.plot
    def score_dist():
        return plot_score_distribution(df())


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

