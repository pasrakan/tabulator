import pandas as pd
from codebook import Codebook
from tabulator import Tabulator
from table_output import latex_output

df = pd.read_stata("analysis.dta")
data = [
    ["riagendr", "Gender", "male", "Male", "female", "Female"],
    ["ridageyr", "Age"],
    ["indfmpir", "Income ratio"],
    [
        "income",
        "Income level",
        "low_income",
        "Low income",
        "medium_income",
        "Medium income",
        "high_income",
        "High income",
    ],
    [
        "ridreth1",
        "Race",
        1,
        "Mexican American",
        2,
        "Other Hispanic",
        3,
        "Non-Hispanic White",
        4,
        "Non-Hispanic Black",
        5,
        "Other Race",
    ],
    [
        "dmdeduc2",
        "Education",
        1,
        "Less than 9th grade",
        2,
        "9-11th grade",
        3,
        "High School",
        4,
        "College",
        5,
        " Graduate or above",
    ],
    [
        "drinker_type",
        "Drinker type",
        "Non-drinker",
        "Non-drinker",
        "Moderate drinker",
        "Moderate drinker",
        "Heavy drinker",
        "Heavy drinker",
    ],
    ["total_score", "Depression score"],
    ["dpq", "Depression type", "No depression", "No", "Depression", "Yes"],
]
c = Codebook(data)

tab = Tabulator(df, c)
covariates = [
    "riagendr",
    "ridageyr",
    "income",
    "ridreth1",
    "dmdeduc2",
    "dmdmartz",
    "drinker_type",
    "total_score",
    "dpq",
]
covariate_type = ["C", "N", "C", "C", "C", "C", "C", "U", "C"]
variable_of_interest = ["income", "total_score", "dpq"]
variable_of_interest_type = ["C", "N", "C"]
res, midrule_modifier = tab.generate_bivariate_table(
    covariates,
    covariate_type,
    variable_of_interest,
    variable_of_interest_type,
    total_column=False,
    missing=False,
)

latex_table = latex_output(res, caption="epi demo", column_grouping=midrule_modifier)
# latex_table = latex_output(res)
print(latex_table)
