import fm_mapgen


def test_printf():
    assert fm_mapgen.printf("Hello %s!\n", "World") == None


def test_internal_link_resolve():
    link = "../../howtos/raw-policies.md"
    file = "/home/jhk/projects/suse/kubewarden-docs/docs/writing-policies/go/raw-policies.md"
    root_dir = "/home/jhk/projects/suse/kubewarden-docs/docs"
    result = "/howtos/raw-policies.md"
    assert fm_mapgen.internal_link_resolve(
        link, file, root_dir) == result
