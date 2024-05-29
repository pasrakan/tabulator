import pandas as pd
import re


# For LaTeX output, refer to:
# https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_latex.html
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_latex.html

# For Excel output, ‘openpyxl’ or ‘xlsxwriter’ is required.


def latex_output(
    result: pd.DataFrame,
    caption="Example Table",
    label="tab:example",
    column_grouping=None,
):
    """
    Generates a LaTeX representation of a DataFrame with optional column grouping.

    Args:
        result (pd.DataFrame): The DataFrame to be converted to LaTeX.
        caption (str): The caption for the LaTeX table.
        label (str): The label for the LaTeX table.
        column_grouping (list of int, optional): A list specifying the grouping of columns.

    Returns:
        str: The LaTeX table as a string.
    """
    latex_table = result.to_latex(
        index=False,
        na_rep="-",
        column_format="l" + "c" * (len(result.columns) - 1),
        longtable=False,
        escape=True,
        multicolumn=False,
        caption=caption,
        label=label,
        position=None,
    )
    # Todo: This also works for regression table, where 'model 1' 'model 2' are the columns and 'beta' 'CI' are the first row.
    lines = latex_table.split("\n")
    midrule_index = None
    for i, line in enumerate(lines):
        if "\midrule" in line:
            midrule_index = i
            break
    lines[midrule_index], lines[midrule_index + 1] = (
        lines[midrule_index + 1],
        lines[midrule_index],
    )

    # line midrule_index-1: column name in result
    # line midrule_index: result[0]
    if column_grouping is not None and len(set(column_grouping)) > 1:
        # Use regex to split by '&' not preceded by a backslash
        columns = re.split(r"(?<!\\)&", lines[midrule_index - 1][:-2])
        suffix = ""
        count = 0
        suffix_index = 0
        for i in column_grouping:
            if not isinstance(i, int) or i < 1:
                raise ValueError(
                    "All elements in midrule_modifier must be integers greater than or equal to 1."
                )
            if i == 1:
                count += 1
                suffix_index += 1
            elif i > 1:
                columns[count] = f"\multicolumn{{{i}}}{{c}}{{{columns[count].strip()}}}"
                del columns[count + 1 : count + i]
                suffix += (
                    f"\cmidrule(lr{{0.5em}}){{{suffix_index+1}-{suffix_index+i}}} "
                )
                count += 1
                suffix_index += i
        lines[midrule_index - 1] = "&".join(columns) + " \\\\ \n" + suffix

    if set(lines[midrule_index - 1].strip()).issubset({"&", " ", "\\"}):
        del lines[midrule_index - 1]
    return "\n".join(lines)


def excel_output(result: pd.DataFrame, file_name="output.xlsx"):
    """
    Generates an Excel file from a DataFrame.

    Args:
        result (pd.DataFrame): The DataFrame to be saved as an Excel file.
        file_name (str): The name of the Excel file to be created.

    Returns:
        None
    """
    result.to_excel(excel_writer=file_name, index=False, na_rep="-", merge_cells=False)
    return 0
