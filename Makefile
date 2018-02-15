build:
	docker build -t mtg-docker.sb.upf.edu/dunya .

push:
	docker push mtg-docker.sb.upf.edu/dunya

all: build push

.PHONY: all build push
