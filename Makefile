CONF_OPTS = -c config.yml

EP_DOCS = /home/jhk/projects/suse/epinio-docs/docs
EP_FMY = inputs/epinio-fm.yml
EP_FM_OPTS = -f ${EP_FMY}

KW_DOCS = /home/jhk/projects/suse/kubewarden-docs/docs
KW_FMY = inputs/kubewarden-fm.yml
KW_FM_OPTS = -f ${KW_FMY}

all: epinio kubewarden

ep-inputs:
	./collect-fm ${EP_DOCS} > ${EP_FMY}

kw-inputs:
	./collect-fm ${KW_DOCS} > ${KW_FMY}

inputs: ep-inputs kw-inputs

test:
	python -m pytest tests

update_examples:
	cp inputs/* example_inputs
	cp outputs/* example_outputs

epinio: clean ep-inputs
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -n > outputs/epinio_nofm.txt
	for t in sidebar_label title description keywords doc-persona doc-type doc-topic; do \
		python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -t $$t > outputs/epinio_no_$$t.txt; \
	done
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -a > outputs/epinio_norequired.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -w > outputs/epinio_weird.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -d > outputs/epinio_dump.txt
	mv tree.txt outputs/epinio_tree.txt
	mv tree.json outputs/epinio_tree.json
	mv tree.dot outputs/epinio.dot
	mv tree-viz.json outputs/epinio-viz.json
	dot outputs/epinio.dot -Tjpg > outputs/epinio.jpg

kubewarden: clean kw-inputs
	./collect-fm ${KW_DOCS} > ${KW_FMY}
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -n > outputs/kubewarden_nofm.txt
	for t in sidebar_label title description keywords doc-persona doc-type doc-topic; do \
		python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -t $$t > outputs/kubewarden_no_$$t.txt; \
	done
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -a > outputs/kubewarden_norequired.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -w > outputs/kubewarden_weird.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -d > outputs/kubewarden_dump.txt
	mv tree.txt outputs/kubewarden_tree.txt
	mv tree.json outputs/kubewarden_tree.json
	mv tree.dot outputs/kubewarden.dot
	mv tree-viz.json outputs/kubewarden-viz.json
	dot outputs/kubewarden.dot -Tjpg > outputs/kubewarden.jpg


clean:
	mkdir -p outputs
	mkdir -p inputs
	rm -f tree.txt tree.dot tree.json
	rm -f outputs/*
	rm -f inputs/*
