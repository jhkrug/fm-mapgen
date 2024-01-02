all: epinio kubewarden

epinio: clean
	python fm_mapgen.py -f epinio-fm.yml -n > outputs/epinio_nofm.txt
	python fm_mapgen.py -f epinio-fm.yml -t keywords > outputs/epinio_nokeywords.txt
	python fm_mapgen.py -f epinio-fm.yml -a > outputs/epinio_norequired.txt
	python fm_mapgen.py -f epinio-fm.yml -w > outputs/epinio_weird.txt
	python fm_mapgen.py -f epinio-fm.yml -d > outputs/epinio_dump.txt
	mv tree.txt outputs/epinio_tree.txt
	mv tree.dot outputs/epinio.dot
	dot outputs/epinio.dot -Tjpg > outputs/epinio.jpg

kubewarden: clean
	python fm_mapgen.py -f kubewarden-fm.yml -n > outputs/kubewarden_nofm.txt
	python fm_mapgen.py -f kubewarden-fm.yml -t keywords > outputs/kubewarden_nokeywords.txt
	python fm_mapgen.py -f kubewarden-fm.yml -a > outputs/kubewarden_norequired.txt
	python fm_mapgen.py -f kubewarden-fm.yml -w > outputs/kubewarden_weird.txt
	python fm_mapgen.py -f kubewarden-fm.yml -d > outputs/kubewarden_dump.txt
	mv tree.txt outputs/kubewarden_tree.txt
	mv tree.dot outputs/kubewarden.dot
	dot outputs/kubewarden.dot -Tjpg > outputs/kubewarden.jpg


clean:
	rm -f outputs/*
