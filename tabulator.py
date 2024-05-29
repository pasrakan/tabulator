import pandas as pd
from codebook import Codebook
from typing import List, Tuple
from scipy import stats


# Ensure all missing and invalid/non-meaningful values are properly handled (e.g., defined as NA or pd.NaN) prior to the analysis.
class Tabulator:
    """
    A class that generates a bivariate analysis table from a dataset and a codebook.
    """

    def __init__(self, data: pd.DataFrame, codebook: Codebook, decimal_places: int = 2):
        self.data = data
        self.codebook = codebook
        self.sample_size, _ = self.data.shape
        self.decimal_places = decimal_places

    def split_codes_labels(self, variable: str) -> Tuple[List[str], List[str]]:
        """
        Split a variable into a list of codes and a list of labels.

        Args:
            variable (str): The name of the variable.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing the list of codes and the list of labels.
        """
        if variable in self.codebook:
            codes = [code for code, _ in self.codebook[variable].items()]
            codes.pop(0)
            labels = [label for _, label in self.codebook[variable].items()]
        else:
            codes = self.data[variable].dropna().unique()
            codes = codes[0:20]
            labels = [variable] + [str(code) for code in codes]
        return codes, labels

    def calculate_covariate_name_column(
        self,
        covariates: List[str],
        variable_type: List[str],
        total_row: bool,
        category_variable_suffix: str,
    ) -> pd.DataFrame:
        """
        Generate the characteristic rows for the bivariate analysis table.

        Args:
            covariates (List[str]): A list of covariate variable names.
            variable_type (List[str]): A list of covariate variable types, either 'N' (normally distributed),
                'U' (not normally distributed), or 'C' (categorical variables).
            total_row (bool): Whether to include a row for all participants.
            category_variable_suffix (str): The suffix for the categorical variables (e.g., "n(%)")

        Returns:
            pd.DataFrame: A DataFrame containing the characteristic rows.
        """
        result = ["Characteristics"]
        if total_row:
            result.append("All participants")
        for variable, var_type in zip(covariates, variable_type):
            _, labels = self.split_codes_labels(variable)
            if var_type == "N":
                result.append(labels[0])
                result.append("mean (sd)")
            elif var_type == "U":
                result.append(labels[0])
                result.append("median (IQR)")
            elif var_type == "C":
                result.append(f"{labels[0]} {category_variable_suffix}")
                result.extend(labels[1:])

        return pd.DataFrame(result, columns=[""])

    def calculate_total_column(
        self,
        covariates: List[str],
        variable_type: List[str],
        missing: bool,
        total_row: bool,
    ) -> pd.DataFrame:
        """
        Generate the total row for the bivariate analysis table, including missing value counts and summary statistics.

        Args:
            covariates (List[str]): A list of covariate variable names.
            variable_type (List[str]): A list of covariate variable types, either 'N', 'U', or 'C'.
            total_row (bool): Whether to include a row for all participants.

        Returns:
            pd.DataFrame: A DataFrame containing the total row.
        """
        result = ["Total"]
        if total_row:
            result.append(f"{self.sample_size} (100%)")
        for variable, var_type in zip(covariates, variable_type):
            if missing:
                missing_count = self.data[variable].isnull().sum()
                result.append(
                    f"{missing_count} missing ({missing_count / self.sample_size:.{self.decimal_places}%})"
                )
            else:
                result.append("")
            if var_type == "N":
                mean_value = self.data[variable].mean()
                sd_value = self.data[variable].std()
                result.append(
                    f"{mean_value:.{self.decimal_places}f} ({sd_value:.{self.decimal_places}f})"
                )
            elif var_type == "U":
                median_value = self.data[variable].median()
                q1 = self.data[variable].quantile(0.25)
                q3 = self.data[variable].quantile(0.75)
                iqr = q3 - q1
                result.append(
                    f"{median_value:.{self.decimal_places}f} ({iqr:.{self.decimal_places}f})"
                )
            elif var_type == "C":
                codes, _ = self.split_codes_labels(variable)
                for code in codes:
                    count = self.data[variable].eq(code).sum()
                    result.append(
                        f"{count} ({count / self.sample_size:.{self.decimal_places}%})"
                    )
        return pd.DataFrame(result, columns=[""])

    def calculate_variable_of_interest_columns(
        self,
        covariates,
        covariable_type,
        variable_of_interest: str,
        variable_type: str,
        table_length: int,
        total_row: bool,
    ) -> pd.DataFrame:
        """
        Generate the variable of interest rows for the bivariate analysis table.

        Args:
            covariates (List[str]): A list of covariate variable names.
            covariable_type (List[str]): A list of covariate variable types, either 'N', 'U', or 'C'.
            variable_of_interest (str): The name of the variable of interest.
            variable_type (str): The type of the variable of interest, either 'N', 'U', or 'C'.
            table_length (int): The total number of rows in the table.
            total_row (bool): Whether to include a row for all participants.

        Returns:
            pd.DataFrame: A DataFrame containing the variable of interest rows.
        """
        codes, labels = self.split_codes_labels(variable_of_interest)
        result = pd.DataFrame()
        if variable_type == "N":
            result[labels[0]] = None
        elif variable_type == "U":
            result[labels[0]] = None
        elif variable_type == "C":
            for label in labels[1:]:
                result[label] = None
        # result['p_value'] = None
        new_index = pd.RangeIndex(stop=table_length)
        result = result.reindex(index=new_index, fill_value="")

        row_index = 1
        col_index = 0
        if total_row:
            if variable_type == "N":
                mean_value = self.data[variable_of_interest].mean()
                sd_value = self.data[variable_of_interest].std()
                result.iloc[row_index, col_index] = (
                    f"{mean_value:.{self.decimal_places}f} ({sd_value:.{self.decimal_places}f})"
                )
            elif variable_type == "U":
                median_value = self.data[variable_of_interest].median()
                q1 = self.data[variable_of_interest].quantile(0.25)
                q3 = self.data[variable_of_interest].quantile(0.75)
                iqr = q3 - q1
                result.iloc[row_index, col_index] = (
                    f"{median_value:.{self.decimal_places}f} ({iqr:.{self.decimal_places}f})"
                )
            elif variable_type == "C":
                for code in codes:
                    count = self.data[variable_of_interest].eq(code).sum()
                    result.iloc[row_index, col_index] = (
                        f"{count} ({count / self.sample_size:.{self.decimal_places}%})"
                    )
                    col_index += 1
            row_index += 1

        # Process each covariate based on its type
        for covariate, covariate_type in zip(covariates, covariable_type):
            covariate_codes, _ = self.split_codes_labels(covariate)
            col_index = 0
            # Leave empty for the first block of each covariate
            row_index += 1

            if covariate_type == "N":
                if variable_type == "N":
                    r, p = stats.pearsonr(
                        self.data[variable_of_interest], self.data[covariate]
                    )
                    result.iloc[row_index, col_index] = (
                        f"Pearson r: {r:.{self.decimal_places}f}"
                    )
                    # result.iloc[row_index-1, col_index+1] = self.format_p(p)
                    row_index += 1
                elif variable_type == "U":
                    r, p = stats.spearmanr(
                        self.data[variable_of_interest],
                        self.data[covariate],
                        nan_policy="omit",
                    )
                    result.iloc[row_index, col_index] = (
                        f"Spearman r: {r:.{self.decimal_places}f}"
                    )
                    # result.iloc[row_index-1, col_index+1] = self.format_p(p)
                    row_index += 1
                elif variable_type == "C":
                    for code in codes:
                        mean_value = self.data.loc[
                            self.data[variable_of_interest] == code, covariate
                        ].mean(skipna=True)
                        sd_value = self.data.loc[
                            self.data[variable_of_interest] == code, covariate
                        ].std(skipna=True)
                        result.iloc[row_index, col_index] = (
                            f"{mean_value:.{self.decimal_places}f} ({sd_value:.{self.decimal_places}f})"
                        )
                        col_index += 1
                    # result.iloc[row_index-1, col_index] = "p"
                    row_index += 1

            elif covariate_type == "U":
                if variable_type == "N" or variable_type == "U":
                    r, p = stats.spearmanr(
                        self.data[variable_of_interest],
                        self.data[covariate],
                        nan_policy="omit",
                    )
                    result.iloc[row_index, col_index] = (
                        f"spearman r: {r:.{self.decimal_places}f}"
                    )
                    # result.iloc[row_index-1, col_index+1] = self.format_p(p)
                    row_index += 1
                elif variable_type == "C":
                    for code in codes:
                        median_value = self.data.loc[
                            self.data[variable_of_interest] == code, covariate
                        ].median()
                        q1 = self.data.loc[
                            self.data[variable_of_interest] == code, covariate
                        ].quantile(0.25)
                        q3 = self.data.loc[
                            self.data[variable_of_interest] == code, covariate
                        ].quantile(0.75)
                        iqr = q3 - q1
                        result.iloc[row_index, col_index] = (
                            f"{median_value:.{self.decimal_places}f} ({iqr:.{self.decimal_places}f})"
                        )
                        col_index += 1
                    # result.iloc[row_index-1, col_index] = "p"
                    row_index += 1

            elif covariate_type == "C":
                p_value_row = row_index - 1
                if variable_type == "N":
                    for code in covariate_codes:
                        mean_value = self.data.loc[
                            self.data[covariate] == code, variable_of_interest
                        ].mean(skipna=True)
                        sd_value = self.data.loc[
                            self.data[covariate] == code, variable_of_interest
                        ].std(skipna=True)
                        result.iloc[row_index, col_index] = (
                            f"{mean_value:.{self.decimal_places}f} ({sd_value:.{self.decimal_places}f})"
                        )
                        row_index += 1
                    # Anova or t-test
                    # p = basic_analysis.anova_or_t_from_variables(self.data, variable_of_interest, covariate)
                    # result.iloc[p_value_row, col_index+1] = self.format_p(p)
                elif variable_type == "U":
                    for code in covariate_codes:
                        median_value = self.data.loc[
                            self.data[covariate] == code, variable_of_interest
                        ].median()
                        q1 = self.data.loc[
                            self.data[covariate] == code, variable_of_interest
                        ].quantile(0.25)
                        q3 = self.data.loc[
                            self.data[covariate] == code, variable_of_interest
                        ].quantile(0.75)
                        iqr = q3 - q1
                        result.iloc[row_index, col_index] = (
                            f"{median_value:.{self.decimal_places}f} ({iqr:.{self.decimal_places}f})"
                        )
                        row_index += 1
                    # Non-parametric test
                    # result.iloc[p_value_row, col_index+1] = "p"
                elif variable_type == "C":
                    for covariate_code in covariate_codes:
                        col_index = 0
                        total = self.data.loc[
                            self.data[covariate] == covariate_code
                        ].shape[0]
                        for code in codes:
                            count = self.data.loc[
                                (self.data[covariate] == covariate_code)
                                & (self.data[variable_of_interest] == code)
                            ].shape[0]
                            result.iloc[row_index, col_index] = (
                                f"{count} ({count / total:.{self.decimal_places}%})"
                            )
                            col_index += 1
                        row_index += 1
                    # Chi square test
                    # rslt = ctab.Table.from_data(self.data[[variable_of_interest, covariate]])
                    # p = rslt.test_nominal_association().pvalue
                    # result.iloc[p_value_row, col_index] = self.format_p(p)

        result.loc[0] = result.columns
        if variable_type == "N" or variable_type == "U":
            result.columns = [""]
        elif variable_type == "C":
            result.columns = [labels[0]] + [""] * (len(labels) - 2)
        return result

    def generate_bivariate_table(
        self,
        covariates: list,
        covariable_type: list = None,
        variables_of_interest=None,
        variable_of_interest_data_type=None,
        missing=True,
        total_row=False,
        total_column=True,
        category_variable_suffix="",
    ):
        """
        Generate a bivariate analysis table.

        Parameters:
        covariates (list): A list of covariate variable names.
        covariate_types (list): A list of covariate variable types, either 'N', 'U', or 'C'.
        variables_of_interest (list, optional): A list of variable names to be analyzed.
        variable_of_interest_data_types (list, optional): A list of data types for the variables of interest, either 'N', 'U', or 'C'.
        total_row (bool, default=False): Whether to include a row for all participants.
        total_column (bool, default=True): Whether to include a column for all participants.
        category_variable_suffix (str, optional): The suffix for the categorical variables (e.g., "n(%)")

        Returns:
        pd.DataFrame: The generated bivariate analysis table.
        """
        row_grouping = []
        column_grouping = []
        result = self.calculate_covariate_name_column(
            covariates, covariable_type, total_row, category_variable_suffix
        )
        column_grouping.append(1)
        if total_column:
            result = pd.concat(
                [
                    result,
                    self.calculate_total_column(
                        covariates, covariable_type, missing, total_row
                    ),
                ],
                axis=1,
            )
            column_grouping.append(1)

        for variable, variable_type in zip(
            variables_of_interest, variable_of_interest_data_type
        ):
            report = self.calculate_variable_of_interest_columns(
                covariates,
                covariable_type,
                variable,
                variable_type,
                len(result),
                total_row,
            )
            result = pd.concat([result, report], axis=1)
            column_grouping.append(report.shape[1])
        return result, column_grouping
