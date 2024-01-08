CONF_OPTS = -r required_fm_tags.yml -o other_fm_tags.yml
EP_FM = -f epinio-fm.yml
KW_FM = -f kubewarden-fm.yml

all: epinio kubewarden

epinio: clean
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM} -n > outputs/epinio_nofm.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM} -t keywords > outputs/epinio_nokeywords.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM} -a > outputs/epinio_norequired.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM} -w > outputs/epinio_weird.txt
	python fm_mapgen.py ${CONF_OPTS} ${EP_FM} -d > outputs/epinio_dump.txt
	mv tree.txt outputs/epinio_tree.txt
	mv tree.json outputs/epinio_tree.json
	mv tree.dot outputs/epinio.dot
	dot outputs/epinio.dot -Tjpg > outputs/epinio.jpg

kubewarden: clean
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM} -n > outputs/kubewarden_nofm.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM} -t keywords > outputs/kubewarden_nokeywords.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM} -a > outputs/kubewarden_norequired.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM} -w > outputs/kubewarden_weird.txt
	python fm_mapgen.py ${CONF_OPTS} ${KW_FM} -d > outputs/kubewarden_dump.txt
	mv tree.txt outputs/kubewarden_tree.txt
	mv tree.json outputs/kubewarden_tree.json
	mv tree.dot outputs/kubewarden.dot
	dot outputs/kubewarden.dot -Tjpg > outputs/kubewarden.jpg


clean:
	rm -f outputs/*
