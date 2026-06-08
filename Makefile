build:
	docker build --platform linux/amd64 -t registry.sb.upf.edu/mtg/dunya:latest .

push:
	docker push registry.sb.upf.edu/mtg/dunya:latest

all: build push

.PHONY: all build push
