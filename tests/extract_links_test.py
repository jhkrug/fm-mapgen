import fm_mapgen


def test_extract_links():
    tf = "tests/extract_links_test_data.md"
    rd = "/home/jhk/projects/fm-mapgen/tests"
    el, il, cl = fm_mapgen.extract_links(tf, rd)
    assert len(el) == 16
    assert il == ['/testing-policies/01-intro.md']
    assert cl == "https://docs.kubewarden.io/writing-policies/go/intro-go"
