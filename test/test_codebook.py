from codebook import Codebook


def test_append():
    c = Codebook()
    c.append("regender", "gender", 1, "Male", 2, "Female")
    c.append("riageyr", "Age")
    assert c["regender"] == {"_label": "gender", 1: "Male", 2: "Female"}
    assert c["riageyr"] == {"_label": "Age"}
    print(c)


test_append()
