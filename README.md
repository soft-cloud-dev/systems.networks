# Alpine Shell HTTP Executor

This container runs an Alpine Linux shell command execution server accessible via browser or HTTP requests on port `3000`.

## Features

- **Right Slide Panel PDF & Raw Text Viewer**: Typing `man {command}` in the web terminal or clicking manual entries slides open a sleek right panel featuring compiled **LaTeX PDF View** (with default OS PDF reader integration) and **Raw Text** view.
- **LaTeX Manual Generation & PDF Export**: Automatically converts any manual page into a publication-quality LaTeX document (`.tex`) and compiles it into a PDF file (`pdflatex`).
- **Interactive PDF Preview & Default PDF Reader**: Embedded PDF viewer in the slide panel (`📄 PDF View`), with direct one-click triggers to open compiled PDFs in your operating system's default PDF file reader (Preview / Acrobat / system default viewer) or download raw `.tex` source code.
- **Direct URL Command Execution**: Execute shell commands via HTTP GET requests at `http://localhost:3000/{shell-command}` (e.g. `http://localhost:3000/whoami` or `http://localhost:3000/ls%20-la`).
- **Interactive Web Interface**: Open `http://localhost:3000/` in your browser for a modern terminal interface with quick-action chips and formatted output.
- **POST API Support**: Execute complex commands by sending raw command string in a `POST` request body to `http://localhost:3000/`.

## Usage Examples

### Via `curl` (Command Line):

```sh
# Get current user inside container
curl http://localhost:3000/whoami

# Check Alpine OS release details
curl http://localhost:3000/cat%20/etc/os-release

# List files with arguments (URL-encoded space %20)
curl "http://localhost:3000/ls%20-la"

# Check disk space
curl http://localhost:3000/df%20-h

# Run echo command
curl "http://localhost:3000/echo%20Hello%20World"

# Execute multi-line command via POST
curl -X POST -d "whoami && uname -a" http://localhost:3000/
```

## Quick Start with Makefile

By default, the `Makefile` uses macOS native `container` CLI (`CONTAINER_ENGINE ?= container`). You can override it with `docker` or `podman`:

```sh
make build                 # Uses macOS container CLI by default
CONTAINER_ENGINE=docker make build   # Use Docker
CONTAINER_ENGINE=podman make build   # Use Podman

make run                   # Run container on port 3000
make stop                  # Stop container
make clean                 # Stop & remove container
make rebuild               # Rebuild and restart
make logs                  # View container logs
```

## Manual Commands

### Using macOS `container` CLI:
```sh
container build -t alpine-webshell -f Containerfile .
container run -d -p 3000:3000 --name web-shell alpine-webshell
```

### Using Docker:
```sh
docker build -t alpine-webshell -f Containerfile .
docker run -d -p 3000:3000 --name web-shell alpine-webshell
```

### Using Podman:
```sh
podman build -t alpine-webshell -f Containerfile .
podman run -d -p 3000:3000 --name web-shell alpine-webshell
```
