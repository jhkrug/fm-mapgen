# fm-mapgen

Messing around with doc stores, front matter data, graphs,
trying to discover/plan subject coverage.

I'm currently working with Docusaurus repositories,
but should be applicable to others.
The data collection is just querying a tree of documents to produce a YAML file.

For asciidoc you need to generate the YAML data files a bit differently.
For the future.

## Commands

- `collect-fm`: collects the frontmatter/metadata
- `fm_mapgen.py`: processes it.

`fm_mapgen.py` creates a tree populating leaf nodes with data from the front matter YAML file.
Lots of work to do with this yet.
Currently, it just outputs a tree in text format and dot format.
So, it's really just the directory structure.
The nodes are populated with all the data from the front matter though,
for further development and processing.
There are also functions to do stuff like check absence of required tags,
no front matter, etc.
To help with getting your front matter into a good state.

All early days. And, I'm definitely not a real programmer.

An underlying assumption is that a directory structure is a reasonable
top-level organizing mechanism for a knowledge tree/map.
I think it's probably ok, I've been raised on an '[everything is a file](https://en.wikipedia.org/wiki/Everything_is_a_file)' philosophy. And directories organize files.

Command examples:

- `./collect-fm ~/projects/suse/kubewarden-docs/docs/ > kw-fm.yml`
Creates a file containing the collected front matter,
from a documentation repository directory tree.
- `python fm_mapgen.py -f ./kw-fm.yml`:
Process a file of collected front matter.
Produces a `tree.out` text file and a `tree.dot` file.
- `dot -Tjpg tree.dot > tree.jpg`:
To create a JPEG graph.

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

There are results included from example runs using
[Kubewarden](https://github.com/kubewarden/docs) and
[Epinio](https://github.com/epinio/docs) docs repositories.
Check out `kw.txt`, `ep.txt`, `kw.jpg`, `ep.jpg`.
