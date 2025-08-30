#!/bin/bash

# Azure DevOps Impact Metrics Extension - Build Script

set -e

echo "🚀 Building Azure DevOps Impact Metrics Extension..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if tfx-cli is installed
if ! command -v tfx &> /dev/null; then
    echo -e "${RED}❌ tfx-cli is not installed${NC}"
    echo -e "${YELLOW}Installing tfx-cli globally...${NC}"
    npm install -g tfx-cli
fi

# Create dist directory
echo -e "${BLUE}📁 Creating dist directory...${NC}"
rm -rf dist
mkdir -p dist

# Copy static files
echo -e "${BLUE}📋 Copying static files...${NC}"
if [ ! -d "static" ]; then
    echo -e "${RED}❌ Static directory not found${NC}"
    exit 1
fi
cp -r static dist/
cp -r images dist/ 2>/dev/null || echo -e "${YELLOW}⚠️  No images directory found. Please add your icon and screenshots.${NC}"

# Bump patch version
echo -e "${BLUE}📈 Bumping patch version...${NC}"
if command -v jq &> /dev/null; then
    # Get current version from package.json
    CURRENT_VERSION=$(jq -r '.version' package.json)
    echo -e "${BLUE}Current version: $CURRENT_VERSION${NC}"
    
    # Bump patch version using npm
    npm version patch --no-git-tag-version
    
    # Get new version
    NEW_VERSION=$(jq -r '.version' package.json)
    echo -e "${GREEN}New version: $NEW_VERSION${NC}"
    
    # Update vss-extension.json version to match
    jq --arg version "$NEW_VERSION" '.version = $version' vss-extension.json > vss-extension.json.tmp && mv vss-extension.json.tmp vss-extension.json
else
    echo -e "${YELLOW}⚠️  jq not found. Install jq for automatic version bumping${NC}"
    echo -e "${YELLOW}   Run: brew install jq (macOS) or apt-get install jq (Ubuntu)${NC}"
fi

# Validate required files exist
echo -e "${BLUE}🔍 Validating required files...${NC}"
if [ ! -f "vss-extension.json" ]; then
    echo -e "${RED}❌ Extension manifest not found${NC}"
    exit 1
fi

# Validate extension and create package
echo -e "${BLUE}✅ Creating extension package...${NC}"
# Check if main.html exists as referenced in manifest
if [ ! -f "dist/static/main.html" ]; then
    echo -e "${RED}❌ main.html not found in static directory${NC}"
    exit 1
fi
tfx extension create --manifest-globs vss-extension.json --output-path dist/ --no-prompt

# Check if .vsix file was created
VSIX_FILE=$(ls dist/*.vsix 2>/dev/null | head -n 1)

if [ -f "$VSIX_FILE" ]; then
    VSIX_FILENAME=$(basename "$VSIX_FILE")
    echo -e "${GREEN}✅ Extension built successfully!${NC}"
    echo -e "${GREEN}📦 Generated: $VSIX_FILENAME${NC}"
    echo ""
    echo -e "${BLUE}🎯 Next Steps:${NC}"
    echo -e "  1. Upload $VSIX_FILENAME to Visual Studio Marketplace"
    echo -e "  2. Or run: ${YELLOW}tfx extension publish --manifest-globs vss-extension.json --token YOUR_PAT${NC}"
    echo ""
    echo -e "${BLUE}📋 Marketplace URL:${NC}"
    echo -e "  https://marketplace.visualstudio.com/manage"
    echo ""
else
    echo -e "${RED}❌ Extension build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Build completed successfully!${NC}"