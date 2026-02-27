#!/bin/bash
# Railway-optimized Moltbot Installation Script
# Installs clawdbot using the available Node.js from Nixpacks

set -e

echo "=== Railway Moltbot Installation ==="
echo "Current PATH: $PATH"
echo "Node version: $(node -v 2>/dev/null || echo 'not found')"
echo "npm version: $(npm -v 2>/dev/null || echo 'not found')"

# Create directories for clawdbot
CLAWDBOT_DIR="/app/.clawdbot-bin"
mkdir -p "$CLAWDBOT_DIR"

# Install clawdbot globally using npm
echo "Installing clawdbot via npm..."
npm install -g clawdbot@latest || {
    echo "Global install failed, trying local approach..."
    npm install clawdbot@latest
    
    # Create a wrapper if local install worked
    if [ -d "node_modules/.bin" ] && [ -f "node_modules/.bin/clawdbot" ]; then
        echo "Creating clawdbot wrapper..."
        cat > "$CLAWDBOT_DIR/clawdbot" << 'WRAPPER'
#!/bin/bash
exec node /app/backend/node_modules/clawdbot/bin/clawdbot.js "$@"
WRAPPER
        chmod +x "$CLAWDBOT_DIR/clawdbot"
        echo "Local installation successful"
        exit 0
    fi
}

# Check if global install worked
if command -v clawdbot &> /dev/null; then
    CLAWDBOT_PATH=$(which clawdbot)
    echo "Clawdbot installed at: $CLAWDBOT_PATH"
    
    # Create symlink in our custom directory
    ln -sf "$CLAWDBOT_PATH" "$CLAWDBOT_DIR/clawdbot"
    
    # Verify installation
    VERSION=$(clawdbot --version 2>/dev/null || echo 'installed')
    echo "Clawdbot version: $VERSION"
    echo "✓ Installation successful!"
    exit 0
else
    echo "WARNING: clawdbot command not found after installation"
    echo "Trying alternative installation method..."
    
    # Try the official installer as fallback
    curl -fsSL https://molt.bot/install.sh -o /tmp/install_moltbot.sh
    chmod +x /tmp/install_moltbot.sh
    bash /tmp/install_moltbot.sh || true
    
    # Check if it installed to /usr/local/bin or similar
    if command -v clawdbot &> /dev/null; then
        CLAWDBOT_PATH=$(which clawdbot)
        ln -sf "$CLAWDBOT_PATH" "$CLAWDBOT_DIR/clawdbot"
        echo "✓ Alternative installation successful!"
        exit 0
    fi
    
    echo "ERROR: Unable to install clawdbot"
    exit 1
fi
