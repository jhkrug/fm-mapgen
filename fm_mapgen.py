"""Reads, parses, and interprets project front matter"""

import sys
import argparse
import yaml
import treelib

required_tags = {"title", "description", "keywords",
                 "doc-persona", "doc-type", "doc-topic"}
valid_tags = required_tags | {"slug", "sidebar_label", "sidebar_position"}

valid_personas = {"developer", "manager", "operator"}


class KmNode(treelib.Node):
    def __init__(self, path, full_path, slug=None,
                 title=None, description=None, keywords=None,
                 sidebar_label=None, sidebar_position=None,
                 doc_persona=None, doc_type=None, doc_topic=None):
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

    def __repr__(self):
        return f"{self.path}, {self.title}, {self.description}"

    def __str__(self):
        return f"{self.path}"

    def get_path(self):
        return f"{self.path}"

    def get_full_path(self):
        return f"{self.full_path}"

    def get_slug(self):
        return f"{self.slug}"

    def get_title(self):
        return f"{self.title}"

    def get_description(self):
        return f"{self.description}"

    def get_keywords(self):
        return f"{self.keywords}"

    def get_sidebar_label(self):
        return f"{self.sidebar_label}"

    def get_sidebar_position(self):
        return f"{self.sidebar_position}"

    def get_doc_persona(self):
        return f"{self.doc_persona}"

    def get_doc_type(self):
        return f"{self.doc_type}"

    def get_doc_topic(self):
        return f"{self.doc_topic}"


def get_node_data_field(node_data, df):
    try:
        match df:
            case "path":
                return node_data.get_path()
            case "full_path":
                return node_data.get_full_path()
            case "slug":
                return node_data.get_slug()
            case "title":
                return node_data.get_title()
            case "description":
                return node_data.get_description()
            case "keywords":
                return node_data.get_keywords()
            case "sidebar_label":
                return node_data.sidebar_label()
            case "sidebar_position":
                return node_data.get_sidebar_position()
            case "doc-persona":
                return node_data.get_doc_persona()
            case "doc-type":
                return node_data.get_doc_type()
            case "doc-topic":
                return node_data.get_doc_topic()
            case _:
                return None
    except:
        return None


def main(argv):
    """Does all the things"""
    args = process_args(argv)
    front_matter = read_yaml_fm(args.yaml_filename)

    kt = build_kt(front_matter)
    kt.save2file(filename='tree.txt', key=False)
    kt.to_graphviz(filename='tree.dot')

    if args.dump:
        for node in kt.all_nodes_itr():
            print_node(node)

    if args.no_frontmatter:
        report_files_without_fm(front_matter)
    if args.weird_tags:
        report_files_with_unrecognized_fm_tags(front_matter)
    if args.fm_tag:
        report_files_without_fm_tag(front_matter, args.fm_tag)
    if args.all_fm_tags:
        for fm_tag in required_tags:
            report_files_without_fm_tag(front_matter, fm_tag)


def print_node(node):
    print("=== Node ===")
    print("Predecessor =", list(node._predecessor.values()))
    print("Successors =", list(node._successors.values())[0])
    print_node_data(node.data)


def print_node_data(node_data):
    print("=== Node data ===")
    print("path =", get_node_data_field(node_data, "path"))
    print("full_path =", get_node_data_field(node_data, "full_path"))
    print("slug =", get_node_data_field(node_data, "slug"))
    print("title =", get_node_data_field(node_data, "title"))
    print("description =", get_node_data_field(node_data, "description"))
    print("keywords =", get_node_data_field(node_data, "keywords"))
    print("sidebar_label =", get_node_data_field(node_data, "sidebar_label"))
    print("sidebar_position =",
          get_node_data_field(node_data, "sidebar_position"))
    print("doc-persona =", get_node_data_field(node_data, "doc-persona"))
    print("doc-type =", get_node_data_field(node_data, "doc-type"))
    print("doc-topic =", get_node_data_field(node_data, "doc-topic"))
    print()


def build_node_data(id, fp, fm):
    try:
        slug = fm['frontmatter']['slug']
    except:
        slug = None
    try:
        title = fm['frontmatter']['title']
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
    node_data = KmNode(id, fp, slug, title, description, keywords,
                       sidebar_label, sidebar_position,
                       doc_persona, doc_type, doc_topic)
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
            node_data = build_node_data(identifier, full_path, fm)
            kt.create_node(tag, identifier=identifier,
                           parent=parent, data=node_data)
    return kt


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
                for tag in f:
                    if tag not in valid_tags:
                        printf("Tag '%s' in file: %s\n", tag, path)
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
