FROM alpine:latest

# Install python3, man, utilities, and documentation (-doc) packages
RUN apk add --no-cache \
    python3 \
    mandoc \
    man-pages \
    util-linux-misc \
    curl \
    ca-certificates \
    coreutils-doc \
    bash-doc \
    mandoc-doc \
    findutils-doc \
    grep-doc \
    tar-doc \
    curl-doc \
    sed-doc \
    gawk-doc \
    busybox-doc

# Set default working directory and terminal environment
WORKDIR /app
ENV TERM=xterm-256color
ENV MANPAGER="mandoc -c"

# Copy HTTP shell server script
COPY server.py /app/server.py

# Expose HTTP port 3000
EXPOSE 3000

# Run HTTP shell command execution server
CMD ["python3", "/app/server.py", "3000"]
