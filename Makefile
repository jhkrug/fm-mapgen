all: epinio kubewarden

epinio:
	> epinio.txt

kubewarden:
	> kubewarden.txt

clean:
	rm -f epinio.txt kubewarden.txt \
		epinio.dot kubewarden.dot \
		epinio.jpg kubewarden.jpg
