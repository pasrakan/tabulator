class Codebook(dict):
    """
    A dictionary-based class that represents a code-label mapping.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def append(self, variable, variable_label, *code_label_pairs):
        """
        Add one or more variables and their corresponding codes and labels to the codebook.

        Parameters:
        variable (str): The name of the variable.
        variable_label (str): The label for the variable.
        *code_label_pairs (tuple): Pairs of code and label for the variable, provided as positional arguments.

        """
        if len(code_label_pairs) % 2 != 0:
            raise ValueError(
                "Arguments should be provided in the format: variable, variable_label, code1, label1, code2, label2, ..."
            )

        self[variable] = {"_label": variable_label}
        for i in range(0, len(code_label_pairs), 2):
            code, label = code_label_pairs[i], code_label_pairs[i + 1]
            self[variable][code] = label

    def get_code_label(self, variable, code):
        """
        Get the label for a given variable and code.

        Parameters:
        variable (str): The name of the variable.
        code: The code value.

        Returns:
        str: The label for the given variable and code.
        If the variable is not found in the codebook or the code is not found for the variable, the original code value is returned.
        """
        if variable in self and code in self[variable]:
            return self[variable][code]
        else:
            return str(code)

    def get_variable_label(self, variable):
        """
        Get the label for a given variable.

        Parameters:
        variable (str): The name of the variable.

        Returns:
        str: The label for the given variable.
        If the variable is not found in the codebook, the original variable name is returned.
        """
        if variable in self and "_label" in self[variable]:
            return self[variable]["_label"]
        else:
            return variable
