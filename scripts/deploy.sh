#!/usr/bin/env bash

set -e

echo "Starting deployment..."

echo "Syncing production dependencies..."
just syncprod

echo "*NOT* running migrations..."
# NOTE migrations are run afterward, on a running container

echo "Collecting static files..."
just collectstatic

echo "Deployment complete!"
