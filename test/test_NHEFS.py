import pandas as pd
import re
from codebook import Codebook
from tabulator import Tabulator

NHEFS = pd.read_excel("NHEFS_Codebook.xlsx")
df = pd.read_csv("nhefs.csv")
restriction_cols = [
    "sex",
    "age",
    "race",
    "wt82",
    "ht",
    "school",
    "alcoholpy",
    "smokeintensity",
]
missing = df[restriction_cols].isnull().any(axis=1)
df = df.loc[~missing]

nested_list = []

for variable, label in NHEFS.iterrows():
    split_description = re.split("[,:]", label["Description"])
    row_list = [label["Variable name"]] + split_description
    for i in range(1, len(row_list)):
        if i % 2 == 0:
            try:
                row_list[i] = int(row_list[i])
            except ValueError:
                pass
    nested_list.append(row_list)

tab = Tabulator(df, Codebook(nested_list))

covariates = [
    "age",
    "sex",
    "race",
    "education",
    "wt71",
    "smokeintensity",
    "smokeyrs",
    "exercise",
    "active",
]
covariate_type = ["N", "C", "C", "C", "N", "N", "N", "C", "C"]

res, midrule_modifier = tab.generate_bivariate_table(
    covariates,
    covariate_type,
    ["qsmk"],
    ["C"],
    total_column=True,
    missing=False,
)
