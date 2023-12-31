# fm-mapgen

Messing around with doc stores, front matter data, graphs,
trying to discover/plan subject coverage.

I'm currently working with Docusarus repos, but should be applicable to others,
it's just querying a tree of docs.

For asciidoc you need to generate the YAML data files a bit differently I suppose.
For the future.

- `collect-fm` - collects the frontmatter/metadata
- `fm_mapgen.py` - processes it.

`fm_mapgen.py` creates a tree populating leaf nodes with data from the frontmatter YAML file.
Lots of work to do with this yet. Currently, it just outputs a tree in text format and dot format.
There are functions do do stuff like check absence of required tags, no frontmatter, etc.
To help with getting your frontmatter into a good state.

All very early days. And, I'm definitely not a real programmer.

Some command examples:

- `./collect-fm ~/projects/suse/kubewarden-docs/docs/ > kw-fm.yml`
Creates a file containing the collected frontmatter from a docs repo directory tree.
- `python fm_mapgen.py -f ./kw-fm.yml`
Process a file of collected frontmatter. Produces a `tree.out` text file and a `tree.dot` file.
- `dot -Tjpg tree.dot > tree.jpg` to create a JPEG graph.

The `python fm_mapgen.py` command:
```console
python fm_mapgen.py -h
usage: ['-h'] [-h] -f YAML_FILENAME [-n] [-t FM_TAG] [-a] [-w]

options:
  -h, --help            show this help message and exit
  -f YAML_FILENAME, --yaml_filename YAML_FILENAME
                        A YAML file containing frontmatter to read.
  -n, --no-frontmatter  Find files with no frontmatter defined.
  -t FM_TAG, --fm_tag FM_TAG
                      A YAML frontmatter tag to check files for the absence of.
  -a, --all_fm_tags     Check for absence of all required tags.
   -w, --weird_tags      Check for any strange frontmatter tags not in the valid tags list.
```

There are results included from example runs using Kubewarden and Epinio docs repos.
