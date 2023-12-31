CONF_OPTS = -r required_fm_tags.yml -o other_fm_tags.yml
EP_DOCS = /home/jhk/projects/suse/epinio-docs/docs
EP_FMY = epinio-fm.yml
KW_FMY = kubewarden-fm.yml
EP_FM_OPTS = -f ${EP_FMY} -c config.yml
KW_FM_OPTS = -f ${KW_FMY} -c config.yml
KW_DOCS = /home/jhk/projects/suse/kubewarden-docs/docs

all: epinio kubewarden

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
	rm -f outputs/*
