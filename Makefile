CONF_OPTS = -c config.yml
EP_DOCS = /home/jhk/projects/suse/epinio-docs/docs
EP_FMY = inputs/epinio-fm.yml
KW_FMY = inputs/kubewarden-fm.yml
EP_FM_OPTS = -f ${EP_FMY}
KW_FM_OPTS = -f ${KW_FMY}
KW_DOCS = /home/jhk/projects/suse/kubewarden-docs/docs

all: test epinio kubewarden

test:
	python -m pytest tests

update_examples:
	cp inputs/* example_inputs
	cp outputs/* example_outputs

epinio: clean
	./collect-fm ${EP_DOCS} > ${EP_FMY}
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -n > outputs/epinio_nofm.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -t keywords > outputs/epinio_nokeywords.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -a > outputs/epinio_norequired.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -w > outputs/epinio_weird.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM_OPTS} -d > outputs/epinio_dump.txt
	mv tree.txt outputs/epinio_tree.txt
	mv tree.json outputs/epinio_tree.json
	mv tree.dot outputs/epinio.dot
	dot outputs/epinio.dot -Tjpg > outputs/epinio.jpg

kubewarden: clean
	./collect-fm ${KW_DOCS} > ${KW_FMY}
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -n > outputs/kubewarden_nofm.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -t keywords > outputs/kubewarden_nokeywords.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -a > outputs/kubewarden_norequired.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -w > outputs/kubewarden_weird.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM_OPTS} -d > outputs/kubewarden_dump.txt
	mv tree.txt outputs/kubewarden_tree.txt
	mv tree.json outputs/kubewarden_tree.json
	mv tree.dot outputs/kubewarden.dot
	dot outputs/kubewarden.dot -Tjpg > outputs/kubewarden.jpg


clean:
	mkdir -p outputs
	mkdir -p inputs
	rm -f tree.txt tree.dot tree.json
	rm -f outputs/*
	rm -f inputs/*
