from shiny import ui

tools_menu = [ui.input_action_button(
    "tools_resize",
    "Resize"
),
ui.input_action_button(
    "tools_duplicate",
    "Duplicate"
),
ui.input_action_button(
    "tools_transmittance_absorbance",
    "Transmittance to Absorbance"
),
ui.input_action_button(
    "tools_absorbance_transmittance",
    "Absorbance to Transmittance"
),
ui.input_action_button(
    "tools_transpose",
    "Transpose"
)]

transform_menu = [
ui.input_action_button(
    "transform_resolution_change",
    "Change Resolution"
),
ui.input_action_button(
    "transform_moving_average",
    "Moving Average Smoothing"
),
ui.input_action_button(
    "transform_median_filter",
    "Median Filter Smoothing"
),
ui.input_action_button(
    "transform_sg_filter",
    "SG Smoothing"
),
ui.input_action_button(
    "transform_gaussian_filter",
    "Gaussian Filter"
),
ui.input_action_button(
    "transform_snv",
    "SNV"
),
ui.input_action_button(
    "transform_msc",
    "MSC"
),
ui.input_action_button(
    "transform_normalise",
    "Normalise"
),
ui.input_action_button(
    "transform_sg_deriv",
    'SG Derivative'
),ui.input_action_button(
    "transform_interpolate",
    'Interpolate'
)]

analysis_menu = [
ui.input_checkbox("analysis_pca","PCA",False),
ui.input_checkbox("analysis_plsr","PLSR",False),
ui.input_checkbox("analysis_logistic_regression","Logistic Regression",False),
ui.input_checkbox("analysis_knn","KNN",False),
ui.input_checkbox("analysis_random_forest","Random Forest",False),
ui.input_action_button(
    "analysis_linear_discrim",
    "Linear Discriminative Analysis"
),
ui.input_action_button(
    "analysis_svm",
    "SVM Classification"
)
]