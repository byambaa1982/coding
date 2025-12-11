#!/bin/bash
set -e

echo "Starting SQL Sandbox initialization..."

# Execute default MySQL entrypoint
exec docker-entrypoint.sh "$@"
