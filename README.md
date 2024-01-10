# fm-mapgen

Messing around with doc stores, front matter data, graphs,
trying to discover/plan subject coverage.

I'm currently working with Docusaurus repositories,
but should be applicable to others.
The data collection is just querying a tree of documents to produce a YAML file.

For asciidoc you need to generate the YAML data files a bit differently.
For the future.

This has arisen from questions I was asking myself about the project docs repositories I'm working on.
So, front matter already has stuff, title, description, keywords.
For SEO, I think.
Add in more tags for things of interest.
Then, doc-persona to say who the doc is for,
doc-type for something from [Diátaxis](https://diataxis.fr) types (we're trying to use that),
doc-topic to try say something about the content.
Also, the actual directory structure storage has something to say about the knowledge organization.

Given this front matter, what can we say about the document repository? Firstly, you can tidy things up by checking for things like missing front matter or front matter tags.

The front matter data is parsed into a `treelib` structure and from there can be graphed, visualized, or printed, or something.
The `treelib` library can export the tree in `dot` format so, the generated JPEGs are there to look at, as glimpse of what might be possible.

## Commands

- `collect-fm`: collects the frontmatter/metadata
- `fm_mapgen.py`: processes it.

`fm_mapgen.py` creates a tree populating leaf nodes with data from the front matter YAML file.
Lots of work to do with this yet.
Currently, it outputs a tree in text format and dot format.
So, it's really just the same as directory structure tree.
The nodes are populated with all the data from the front matter, for
further development and processing.
There are also functions to do stuff like check absence of required tags,
files with no front matter, etc.
To help with getting your front matter into a good state.

All early days.
I'm wondering how valid an approach this in the technical writing community I have so recently joined.

An underlying assumption is that a directory structure is a reasonable
top-level organizing mechanism for a knowledge tree/map.
I think that's probably ok, I'm raised on an '[everything is a file](https://en.wikipedia.org/wiki/Everything_is_a_file)' philosophy.
And directories organize files.

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
usage: ['-h'] [-h] -f YAML_FILENAME -r REQUIRED_FM_TAGS -o OTHER_FM_TAGS [-n] [-t FM_TAG] [-a] [-w] [-d]

options:
  -h, --help            show this help message and exit
  -f YAML_FILENAME, --yaml_filename YAML_FILENAME
                        A YAML file containing frontmatter to read.
  -r REQUIRED_FM_TAGS, --required_fm_tags REQUIRED_FM_TAGS
                        A YAML file containing the required front matter tags.
  -o OTHER_FM_TAGS, --other_fm_tags OTHER_FM_TAGS
                        A YAML file containing the other front matter tags.
  -n, --no-frontmatter  Find files with no frontmatter defined.
  -t FM_TAG, --fm_tag FM_TAG
                        A YAML frontmatter tag to check files for the absence of.
  -a, --all_fm_tags     Check for absence of all required tags.
  -w, --weird_tags      Check for any strange frontmatter tags not in the valid tags list.
  -d, --dump            Dump the tree in a readable format.
```

There are results included from example runs using
[Kubewarden](https://github.com/kubewarden/docs) and
[Epinio](https://github.com/epinio/docs) docs repositories.

Check the inputs/outputs in the `example_inputs` and `example_outputs` directories.
