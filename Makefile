CONTAINER_ENGINE ?= container
IMAGE_NAME ?= alpine-webshell
CONTAINER_NAME ?= web-shell
PORT ?= 3000

.PHONY: all build run stop clean rebuild logs help

all: build

help:
	@echo "Available targets (using $(CONTAINER_ENGINE)):"
	@echo "  make build    - Build the container image"
	@echo "  make run      - Run the container on port $(PORT)"
	@echo "  make stop     - Stop the running container"
	@echo "  make clean    - Remove the container"
	@echo "  make rebuild  - Rebuild image and restart container"
	@echo "  make logs     - View container logs"

build:
	$(CONTAINER_ENGINE) build -t $(IMAGE_NAME) -f Containerfile .

run:
	$(CONTAINER_ENGINE) run -d --name $(CONTAINER_NAME) -p $(PORT):3000 $(IMAGE_NAME)
	@echo "HTTP Shell Executor listening at http://localhost:$(PORT)"

stop:
	-$(CONTAINER_ENGINE) stop $(CONTAINER_NAME)

clean: stop
	-$(CONTAINER_ENGINE) rm $(CONTAINER_NAME)

rebuild: clean build run

logs:
	$(CONTAINER_ENGINE) logs -f $(CONTAINER_NAME)
