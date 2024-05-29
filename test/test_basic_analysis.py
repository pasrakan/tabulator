import pandas as pd
from codebook import Codebook
from basic_analysis import raw_table_report

test_data = {
    "regender": [1, 2, 1, 1, 1, 2],
    "riageyr": [18, 25, 18, 25, 18, 18],
    "education": [1, 2, 3, 1, 4, 5],
    "married": [True, False, False, False, False, 3],
}
test_df = pd.DataFrame(test_data)

c = Codebook()
c.append("regender", "Gender", 1, "Male", 2, "Female")
c.append("riageyr", "Age")
c.append("education", "Education Level", 1, "High School", 2, "College", 3, "Graduate")

report_df = raw_table_report(test_df, c)

result = {
    "Gender": ["Male", "Female", "Male", "Male", "Male", "Female"],
    "Age": ["18", "25", "18", "25", "18", "18"],
    "Education Level": ["High School", "College", "Graduate", "High School", "4", "5"],
    "married": [True, False, False, False, False, 3],
}

pd.testing.assert_frame_equal(report_df, pd.DataFrame(result), check_dtype=False)
