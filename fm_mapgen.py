"""Reads, parses, and interprets project front matter"""

import sys
import argparse
import yaml
import treelib
import markdown
import re

# These 3 are read from config files by read_config:
required_fm_tags = {}
other_fm_tags = {}
valid_fm_tags = {}


class KmNode(treelib.Node):
    def __init__(self, path, full_path, ndd: dict = {},
                 int_links=None, ext_links=None):
        self.path = path
        self.full_path = full_path
        try:
            for k in valid_fm_tags.keys():
                setattr(self, k, ndd[k])
        except:
            pass
        self.int_links = int_links
        self.ext_links = ext_links

    def __repr__(self):
        return f"{self.path}, {self.full_path}"

    def __str__(self):
        return f"{self.path}"


def read_config(r, o):
    global required_fm_tags
    global other_fm_tags
    global valid_fm_tags
    required_fm_tags = read_yaml(r)
    other_fm_tags = read_yaml(o)
    valid_fm_tags = required_fm_tags | other_fm_tags


def main(argv):
    """Does the things"""
    args = process_args(argv)
    read_config(args.required_fm_tags, args.other_fm_tags)
    front_matter = read_yaml(args.yaml_filename)

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
        for fm_tag in required_fm_tags:
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
    print_node_data(node.data, node.is_leaf())


def print_node_data(node_data, node_is_leaf):
    print("=== Node data ===")
    print("path =", node_data.path)
    print("full_path =", node_data.full_path)
    for k in valid_fm_tags.keys():
        try:
            print(k, "=", getattr(node_data, k))
        except:
            pass
    if node_is_leaf:
        print("int_links =", node_data.int_links)
        print("ext_links =", node_data.ext_links)
    print()


def build_node_data(id, fp, fm, doc_int_links, doc_ext_links):
    """Puts any frontmatter data for into node_data for the tree"""
    node_data_dict = {}
    for k, v in valid_fm_tags.items():
        try:
            node_data_dict[k] = fm['frontmatter'][v]
        except:
            node_data_dict[k] = None
    try:
        int_links = doc_int_links
    except:
        int_links = None
    try:
        ext_links = doc_ext_links
    except:
        ext_links = None
    node_data = KmNode(id, fp, node_data_dict, int_links, ext_links)
    return node_data


def build_kt(front_matter):
    """Builds the knowledge tree structure from front_matter"""
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
    """Reads markdown from filename and finds any links"""
    string = open(filename).read()
    html = markdown.markdown(string, output_format='html')
    links = list(set(re.findall(r'href=[\'"]?([^\'" >]+)', html)))
    links = list(filter(lambda l: l[0] != "{", links))
    o_links, e_links = [], []
    for l in links:
        r = re.sub("^https?://", "", l)
        if r != l:
            e_links.append(l)
        else:
            o_links.append(l)
    return e_links, o_links


def process_args(a):
    arg_parser = argparse.ArgumentParser(a)
    arg_parser.add_argument("-f", "--yaml_filename",
                            help="A YAML file containing frontmatter to read.",
                            required=True)
    arg_parser.add_argument("-r", "--required_fm_tags",
                            help="A YAML file containing the required front matter tags.",
                            required=True)
    arg_parser.add_argument("-o", "--other_fm_tags",
                            help="A YAML file containing the other front matter tags.",
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


def read_yaml(filename):
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
                    if fm_tag not in valid_fm_tags.values():
                        printf("Tag '%s' in file: %s\n", fm_tag, path)
            except:
                # no frontmatter here
                pass


def error_exit(err_string):
    print(err_string)
    sys.exit(1)


def printf(format, *args):
    sys.stdout.write(format % args)


if __name__ == "__main__":
    main(sys.argv[1:])
