"""Reads, parses, and interprets project front matter"""

import sys
import argparse
from ruamel.yaml import YAML
import treelib
import markdown
import re
import os
import jsonpickle
import json

# These are read from a YAML configuration file by read_config:
required_fm_tags = {}
other_fm_tags = {}
valid_fm_tags = {}
sort_fm_tag = None


class KmNodeData():
    """
    Knowledge Map Node is used to store data about a markdown file for those
    nodes at the leaves of the tree, i.e. the actual *.md files.

    Path and full_path are stored along with a dictionary for each of internal
    and external links.

    The main body of the data is defined by a couple of configuration YAML
    files. These config files are read by read_config and define the
    dictionaries required_fm_tags and other_fm_tags which when combined form
    valid_fm_tags. This valid_fm_tags defines the data items to be read from the
    document front matter to be processed.

    """

    def __init__(self, path, full_path, ndd: dict = {},
                 int_links=None, ext_links=None, can_link=None):
        self.path = path
        self.full_path = full_path

        try:
            for k in valid_fm_tags.keys():
                setattr(self, k, ndd[k])
        except:
            pass

        if int_links:
            self.int_links = int_links
        if ext_links:
            self.ext_links = ext_links
        if can_link:
            self.can_link = can_link

    def __repr__(self):
        return f"{self.path}, {self.full_path}"

    def __str__(self):
        return f"{self.path}"

    def print(self, node_is_leaf=False):
        print("=== Node data ===")
        print("path =", self.path)
        print("full_path =", self.full_path)
        if node_is_leaf:
            for k in valid_fm_tags.keys():
                try:
                    print(k, "=", getattr(self, k))
                except:
                    pass
            try:
                print("internal_links =", self.int_links)
            except:
                print("internal_links =", [])
            try:
                print("external_links =", self.ext_links)
            except:
                print("external_links =", [])
            try:
                print("canonical_link =", self.can_link)
            except:
                print("canonical_links =", [])
        print()

    def to_dict(self):
        return self.__dict__


def create_folder_structure_json(path, km, root_dir):
    # Initialize the result dictionary with folder
    # name, type, and an empty list for children
    name = os.path.basename(path)
    result = {"name": "/" + name,
              "type": "directory", "entries": []}

    # Check if the path is a directory
    if not os.path.isdir(path):
        return result

    # Iterate over the entries in the directory
    for entry in os.listdir(path):
       # Create the full path for the current entry
        entry_path = os.path.join(path, entry)

        # If the entry is a directory, recursively call the function
        if os.path.isdir(entry_path):
            result["entries"].append(
                create_folder_structure_json(entry_path, km, root_dir))
        # If the entry is a file, create a dictionary with name and type
        else:
            rel_path = entry_path.replace(root_dir, "")
            nd: treelib.Node = km.get_node(rel_path)
            try:
                ndc = nd.data.__dict__.copy()
                ndc.pop("path")
                ndc.pop("full_path")
                result["entries"].append(
                    {"name": rel_path, "type": "file", "data": ndc})
            except:
                result["entries"].append({"name": rel_path, "type": "file"})

    return result


def read_config(c):
    global required_fm_tags
    global other_fm_tags
    global valid_fm_tags
    global sort_fm_tag

    config_yaml = read_yaml(c)
    try:
        required_fm_tags = config_yaml['required_fm_tags']
    except:
        error_exit("Can't read required_fm_tags from config.")
    try:
        other_fm_tags = config_yaml['other_fm_tags']
    except:
        other_fm_tags = {}
    try:
        sort_fm_tag = config_yaml['sorting']['node_sort_key']
    except:
        sort_fm_tag = None
    valid_fm_tags = required_fm_tags | other_fm_tags


def main(argv):
    """Does the things"""
    args = process_args(argv)
    read_config(args.configuration)
    front_matter = read_yaml(args.yaml_filename)

    km = build_km(front_matter)
    try:
        os.remove("tree.txt")
    except:
        pass
    km.save2file(filename="tree.txt", key=get_sort_val)
    try:
        os.remove("tree.dot")
    except:
        pass
    km.to_graphviz(filename="tree.dot", key=get_sort_val)

    json_km = jsonpickle.encode(km, keys=True, indent=2)
    with open("tree.json", "w") as f:
        f.write(str(json_km))

    json_viz = km2json_for_viz(km, sorted=True)
    with open("tree-viz.json", "w") as f:
        f.write(json_viz)

    if args.dump:
        print_km(km, sorted=True)

    if args.no_frontmatter:
        report_files_without_fm(front_matter)
    if args.weird_tags:
        report_files_with_unrecognized_fm_tags(front_matter)
    if args.fm_tag:
        report_files_without_fm_tag(front_matter, args.fm_tag)
    if args.all_fm_tags:
        for fm_tag in required_fm_tags.values():
            report_files_without_fm_tag(front_matter, fm_tag)


def get_sort_val(node: treelib.Node):
    sv = 0
    try:
        sv = int(getattr(node.data, str(sort_fm_tag)))
        if sv == None:
            sv = 0
    except:
        sv = 0
    return sv


def print_km(km: treelib.Tree, sorted=False):
    print("knowledge_map, depth =", km.depth())
    # mode = 1, 2, 3 for DEPTH, WIDTH, ZIGZAG
    gen = km.expand_tree(mode=1, key=get_sort_val, sorting=sorted)
    for n in gen:
        print_node(km[n], km.depth(n))


def print_node(node, depth):
    print("=== Node ===")
    print("identifier =", node.identifier)
    print("Predecessor =", list(node._predecessor.values()))
    print("Successors =", list(node._successors.values())[0])
    print("Depth =", depth)
    node.data.print(node.is_leaf())


def km2json_for_viz(km: treelib.Tree, sorted=False) -> str:
    root_dir = km['root'].data.full_path
    km_json = create_folder_structure_json(root_dir, km, root_dir)
    return json.dumps(km_json, indent=2)


def build_node_data(id, fp, fm,
                    doc_int_links, doc_ext_links, doc_can_link) -> KmNodeData:
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
    try:
        can_link = doc_can_link
    except:
        can_link = None
    node_data = KmNodeData(id, fp, node_data_dict,
                           int_links, ext_links, can_link)
    return node_data


def build_km(front_matter) -> treelib.Tree:
    """Builds the knowledge map structure from front_matter"""
    root_dir = front_matter[0]['docstore-data']['root-dir']
    km = treelib.Tree()
    km.create_node("Frontmatter Map", identifier="root", parent=None,
                   data=KmNodeData(None, root_dir))
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
                    if not km.contains(pb):
                        node_data = KmNodeData(pb, root_dir + "/" + pb)
                        km.create_node(pb, identifier=pb,
                                       parent=parent, data=node_data)
                except:
                    pass
                parent = pb

            # Get the data to populate the leaf node.
            tag = branches[-1]
            ext_links, int_links, can_link = extract_links(
                full_path, root_dir)
            node_data = build_node_data(
                identifier, full_path, fm, int_links, ext_links, can_link)
            km.create_node(tag, identifier=identifier,
                           parent=parent, data=node_data)
    return km


def internal_link_resolve(l, f, r):
    """Given an internal link l and the file, f it's from return the
    full path, stripping the root_dir, r from the front."""
    # Do the python equivalents of dirname(f), tack on l, then readlink(f)
    # Seems to work fine with '#internal' anchors left in place.
    n = os.path.realpath(os.path.dirname(f) + "/" + l)
    n = n.replace(r, "")
    return n


def extract_links(filename, root_dir):
    """Reads markdown from filename and finds any links"""
    string = open(filename).read()
    html = markdown.markdown(string, output_format='html')
    links = list(set(re.findall(r'href=[\'"]?([^\'" >]+)', html)))
    links = list(filter(lambda l: l[0] != "{", links))
    internal_links, external_links = [], []
    for l in links:
        r = re.sub("^https?://", "", l)
        if r != l:
            external_links.append(l)
        else:
            internal_links.append(internal_link_resolve(l, filename, root_dir))
    canonical_link = list(
        set(re.findall(r'rel=[\'"]canonical[\'"] href=[\'"]?([^\'" >]+)', html)))
    canonical_link = list(filter(lambda l: l[0] != "{", canonical_link))
    try:
        canonical_link = canonical_link[0]
    except:
        canonical_link = None
    return external_links, internal_links, canonical_link


def process_args(a):
    arg_parser = argparse.ArgumentParser(a)
    arg_parser.add_argument(
        "-c", "--configuration",
        help="A YAML file with configuration, at minimum required_fm_tags",
        required=True)
    arg_parser.add_argument(
        "-f", "--yaml_filename",
        help="A YAML file containing frontmatter to read.",
        required=True)
    arg_parser.add_argument(
        "-n", "--no-frontmatter",
        help="Find files with no frontmatter defined.",
        required=False, action='store_true')
    arg_parser.add_argument(
        "-t", "--fm_tag",
        help="A YAML frontmatter tag to check files for the absence of.",
        required=False)
    arg_parser.add_argument(
        "-a", "--all_fm_tags",
        help="Check for absence of any required tags.",
        required=False, action='store_true')
    arg_parser.add_argument(
        "-w", "--weird_tags",
        help="Check for strange frontmatter tags not in the valid tags list.",
        required=False, action='store_true')
    arg_parser.add_argument(
        "-d", "--dump",
        help="Dump the map in a readable format.",
        required=False, action='store_true')
    args = arg_parser.parse_args()
    return args


def read_yaml(filename):
    with open(filename, 'r') as f:
        return YAML(typ='safe').load(f)


def report_files_without_fm(front_matter):
    """Report on any markdown files missing frontmatter"""
    print("=== No front matter files:")
    for f in front_matter:
        try:
            if f['docstore-data']:
                pass
        except:
            if f['frontmatter'] is None:
                print(f['path'])


def report_files_without_fm_tag(front_matter, fm_tag):
    """Report on any markdown files missing the fm_tag"""
    printf("=== Files with no, or empty frontmatter fm_tag: %s:\n", fm_tag)
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
    printf("=== Files with weird frontmatter tags:\n")
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
