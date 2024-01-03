"""Reads, parses, and interprets project front matter"""

import sys
import argparse
import yaml
import treelib
import markdown
import re

required_tags = {
    "title": "title",
    "description": "description",
    "keywords": "keywords",
    "doc_persona": "doc-persona",
    "doc_type": "doc-type",
    "doc_topic": "doc-topic"
}

valid_tags = required_tags | {
    "slug": "slug",
    "sidebar_label": "sidebar_label",
    "sidebar_position": "sidebar_position"
}

valid_personas = ["developer", "manager", "operator"]


class KmNode(treelib.Node):
    def __init__(self, path, full_path, slug=None,
                 title=None, description=None, keywords=None,
                 sidebar_label=None, sidebar_position=None,
                 doc_persona=None, doc_type=None, doc_topic=None,
                 int_links=None, ext_links=None):
        self.path = path
        self.full_path = full_path
        self.slug = slug
        self.title = title
        self.description = description
        self.keywords = keywords
        self.sidebar_label = sidebar_label
        self.sidebar_position = sidebar_position
        self.doc_persona = doc_persona
        self.doc_type = doc_type
        self.doc_topic = doc_topic
        self.int_links = int_links
        self.ext_links = ext_links

    def __repr__(self):
        return f"{self.path}, {self.title}, {self.description}"

    def __str__(self):
        return f"{self.path}"


def main(argv):
    """Does all the things"""
    args = process_args(argv)
    front_matter = read_yaml_fm(args.yaml_filename)

    kt = build_kt(front_matter)
    kt.save2file(filename='tree.txt', key=False)
    kt.to_graphviz(filename='tree.dot')

    if args.dump:
        print_tree(kt)

    if args.no_frontmatter:
        report_files_without_fm(front_matter)
    if args.weird_tags:
        report_files_with_unrecognized_fm_tags(front_matter)
    if args.fm_tag:
        report_files_without_fm_tag(front_matter, args.fm_tag)
    if args.all_fm_tags:
        for fm_tag in required_tags:
            report_files_without_fm_tag(front_matter, fm_tag)


def print_tree(kt):
    print("tree_depth =", kt.depth())
    for node in kt.all_nodes_itr():
        print_node(node, kt.depth(node))


def print_node(node, depth):
    print("=== Node ===")
    print("Predecessor =", list(node._predecessor.values()))
    print("Successors =", list(node._successors.values())[0])
    print("Depth =", depth)
    print_node_data(node.data)


def print_node_data(node_data):
    print("=== Node data ===")
    print("path =", node_data.path)
    print("full_path =", node_data.full_path)
    for k in valid_tags.keys():
        print(k, "=", getattr(node_data, k))
    print("int_links =", node_data.int_links)
    print("ext_links =", node_data.ext_links)
    print()


def build_node_data(id, fp, fm, doc_int_links, doc_ext_links):
    try:
        slug = fm['frontmatter']['slug']
    except:
        slug = None
    try:
        title = fm['frontmatter']['title']
        if title == "":
            title = None
    except:
        title = None
    try:
        description = fm['frontmatter']['description']
    except:
        description = None
    try:
        keywords = fm['frontmatter']['keywords']
    except:
        keywords = None
    try:
        sidebar_label = fm['frontmatter']['sidebar_label']
    except:
        sidebar_label = None
    try:
        sidebar_position = int(fm['frontmatter']['sidebar_position'])
    except:
        sidebar_position = 0
    try:
        doc_persona = fm['frontmatter']['doc-persona']
    except:
        doc_persona = None
    try:
        doc_type = fm['frontmatter']['doc-type']
    except:
        doc_type = None
    try:
        doc_topic = fm['frontmatter']['doc-topic']
    except:
        doc_topic = None
    try:
        int_links = doc_int_links
    except:
        int_links = None
    try:
        ext_links = doc_ext_links
    except:
        ext_links = None
    node_data = KmNode(id, fp, slug, title, description, keywords,
                       sidebar_label, sidebar_position,
                       doc_persona, doc_type, doc_topic, int_links, ext_links)
    return node_data


def build_kt(front_matter):
    root_dir = front_matter[0]['docstore-data']['root-dir']
    kt = treelib.Tree()
    kt.create_node("Frontmatter Tree", identifier="root", parent=None,
                   data=KmNode(None, root_dir))
    for fm in front_matter:
        try:
            if fm['docstore-data']:
                print("Data generated:", fm['docstore-data']['gen-date'])
        except:
            full_path = fm['path']
            identifier = full_path.replace(root_dir, "")
            # Now create a node, if it does not already
            # exist for each path component, of identifier, separated by '/',
            # until the '*.md' file is reached.
            # This the final node in that tree branch and can be
            # filled with the frontmatter data.
            parent = 'root'
            pb = None
            branches = identifier.split("/")
            for branch in branches[:-1]:
                # Does parent.branch exist already?
                pb = branch + "/"
                try:
                    if not kt.contains(pb):
                        node_data = KmNode(pb, root_dir + pb)
                        kt.create_node(pb, identifier=pb,
                                       parent=parent, data=node_data)
                except:
                    pass
                parent = pb

            # Get the data to populate the leaf node.
            tag = branches[-1]
            ext_links, int_links = extract_links(full_path)
            node_data = build_node_data(
                identifier, full_path, fm, int_links, ext_links)
            kt.create_node(tag, identifier=identifier,
                           parent=parent, data=node_data)
    return kt


def extract_links(filename):
    string = open(filename).read()
    html = markdown.markdown(string, output_format='html')
    links = list(set(re.findall(r'href=[\'"]?([^\'" >]+)', html)))
    links = list(filter(lambda l: l[0] != "{", links))
    olinks, elinks = [], []
    for l in links:
        r = re.sub("^https?://", "", l)
        if r != l:
            elinks.append(l)
        else:
            olinks.append(l)
    return elinks, olinks


def process_args(a):
    """Command line argument processor"""
    arg_parser = argparse.ArgumentParser(a)
    arg_parser.add_argument("-f", "--yaml_filename",
                            help="A YAML file containing frontmatter to read.",
                            required=True)
    arg_parser.add_argument("-n", "--no-frontmatter",
                            help="Find files with no frontmatter defined.",
                            required=False, action='store_true')
    arg_parser.add_argument("-t", "--fm_tag",
                            help="A YAML frontmatter tag to check files for the absence of.",
                            required=False)
    arg_parser.add_argument("-a", "--all_fm_tags",
                            help="Check for absence of all required tags.",
                            required=False, action='store_true')
    arg_parser.add_argument("-w", "--weird_tags",
                            help="Check for any strange frontmatter tags not in the valid tags list.",
                            required=False, action='store_true')
    arg_parser.add_argument("-d", "--dump",
                            help="Dump the tree in a readable format.",
                            required=False, action='store_true')
    args = arg_parser.parse_args()
    return args


def read_yaml_fm(filename):
    with open(filename, 'r') as f:
        return yaml.safe_load(f)


def report_files_without_fm(front_matter):
    """Report on any markdown files missing frontmatter"""
    print("No front matter files ---")
    for f in front_matter:
        try:
            if f['docstore-data']:
                pass
        except:
            if f['frontmatter'] is None:
                print(f['path'])


def report_files_without_fm_tag(front_matter, fm_tag):
    """Report on any markdown files missing the fm_tag"""
    printf("Files with no, or empty frontmatter fm_tag: %s ---\n", fm_tag)
    for f in front_matter:
        try:
            if f['docstore-data']:
                pass
        except:
            try:
                tag_val = f['frontmatter'][fm_tag]
                if tag_val == "":
                    print(f['path'])
            except:
                print(f['path'])


def report_files_with_unrecognized_fm_tags(front_matter):
    """Any files with weird fm_tags"""
    printf("Files with weird frontmatter tags\n")
    for fm in front_matter:
        try:
            if fm['docstore-data']:
                pass
        except:
            try:
                f = fm['frontmatter']
                path = fm['path']
                for fm_tag in f:
                    if fm_tag not in valid_tags.values():
                        printf("Tag '%s' in file: %s\n", fm_tag, path)
            except:
                # no frontmatter here
                pass


def error_exit(err_string):
    """Prints an error string and exits

    Args:
        err_string (string): An error message
    """
    print(err_string)
    sys.exit(1)


def printf(format, *args):
    sys.stdout.write(format % args)


if __name__ == "__main__":
    main(sys.argv[1:])
