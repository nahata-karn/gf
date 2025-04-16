#!/bin/bash
set -e

echo "Setting up static files..."

# Make sure static directories exist
mkdir -p /opt/render/project/src/goodfire_webapp/static/
mkdir -p /opt/render/project/src/goodfire_webapp/templates/

# Copy the static files to the correct location
cp -r goodfire_webapp/static/* /opt/render/project/src/goodfire_webapp/static/
cp -r goodfire_webapp/templates/* /opt/render/project/src/goodfire_webapp/templates/

echo "Static files setup complete!"

# Debug info
echo "Listing static files:"
ls -la /opt/render/project/src/goodfire_webapp/static/

echo "Current environment variables:"
env | grep -E 'API_KEY|GOODFIRE'

echo "Build script completed successfully." 