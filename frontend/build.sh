#!/bin/bash
set -e

# Enable corepack for yarn
corepack enable

# Install dependencies
yarn install --frozen-lockfile

# Build the app
yarn build

echo "Build completed successfully!"
