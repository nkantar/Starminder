#!/bin/sh

set -e

echo "Applying database migrations..."
just migrate

echo "Starting server..."
exec just prodserve
