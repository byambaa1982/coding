#!/bin/sh
# Entrypoint script for Python sandbox

# Set resource limits
ulimit -t 30     # CPU time limit: 30 seconds
ulimit -v 134217728  # Virtual memory limit: 128MB
ulimit -f 1024   # File size limit: 1MB

# Execute Python code
exec python3 "$@"
