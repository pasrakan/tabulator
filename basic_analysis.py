import pandas as pd
import scipy.stats as stats
from codebook import Codebook


def raw_table_report(dataset, codebook: Codebook):
    """
    Generate a report table based on the dataset and the codebook.

    Parameters:
    dataset (pandas.DataFrame): The dataset to generate the report from.
    codebook (Codebook): The codebook object containing the code-label mappings.

    Returns:
    pandas.DataFrame: The report table.
    """
    report = pd.DataFrame()
    for column in dataset.columns:
        if column in codebook:
            report[codebook.get_variable_label(column)] = dataset[column].map(
                lambda x: codebook.get_code_label(column, x)
            )
        else:
            report[column] = dataset[column]
    return report


def anova_or_t_from_variables(dataset, continuous_variable, categorical_variable):
    """
    Perform a statistical test (t-test or ANOVA) between a continuous variable and a categorical variable.

    Parameters:
    dataset (pandas.DataFrame): The input dataset.
    continuous_variable (str): The name of the continuous variable.
    categorical_variable (str): The name of the categorical variable.

    Returns:
    float: The p-value of the statistical test.
    """
    possible_values = dataset[categorical_variable].dropna().unique()
    if len(possible_values) < 2:
        raise ValueError(
            f"The categorical variable '{categorical_variable}' must have at least two categories."
        )

    if len(possible_values) == 2:
        # Perform t-test for each group of the binary variable
        x1 = dataset.loc[
            dataset[categorical_variable] == possible_values[0], continuous_variable
        ]
        x2 = dataset.loc[
            dataset[categorical_variable] == possible_values[1], continuous_variable
        ]
        _, levene = stats.levene(x1, x2, nan_policy="omit")
        if levene < 0.05:
            return stats.ttest_ind(x1, x2, equal_var=False, nan_policy="omit").pvalue
        else:
            return stats.ttest_ind(x1, x2, equal_var=True, nan_policy="omit").pvalue
    else:
        # Perform anova
        groups = [
            dataset.loc[dataset[categorical_variable] == value, continuous_variable]
            for value in possible_values
        ]
        _, p_value = stats.f_oneway(*groups)
        return p_value
