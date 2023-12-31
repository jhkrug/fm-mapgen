# Ideas

## Pre-processing

Given a hierarchical directory structure of markdown files:

- Traverse the directory tree to find markdown files
- for each markdown file
  - record the directory name
  - file name
  - the front-matter as a text blob
  - parsed, configurable, front-matter elements
    - slug
    - title
    - sidebar_label
    - etc.
- Produce an output data structure for further processing.

## Configuration

- Front-matter elements
- Hierarchy definition, what describes the hierarchy and how?
File system structure? Contents of front-matter tag `doc-topic`?

## Outputs

Given the output data structure:

- Generate a graphical representation of the knowledge tree for coverage and documentation of coverage.
- Generate a documentation tree with markdown file placeholders, containing front-matter ready for further work.

## How to represent knowledge graph data structure

YAML, JSON?

## Controlled vocabulary

The tags and some of the tag contents, for example,
`doc-topic` and `doc-persona` need a controlled vocabulary to check data with.
