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

# Determine npm global bin directory
NPM_PREFIX=$(npm config get prefix 2>/dev/null || echo "/usr/local")
NPM_BIN="$NPM_PREFIX/bin"
echo "npm global bin directory: $NPM_BIN"

# Add npm bin to PATH for this script
export PATH="$NPM_BIN:$PATH"

# Install clawdbot globally using npm
echo "Installing clawdbot via npm..."
npm install -g clawdbot@latest || {
    echo "Global install failed, trying with --force..."
    npm install -g --force clawdbot@latest || {
        echo "Forced global install failed, trying local approach..."
        npm install clawdbot@latest
        
        # Create a wrapper if local install worked
        if [ -d "node_modules/.bin" ] && [ -f "node_modules/.bin/clawdbot" ]; then
            echo "Creating clawdbot wrapper..."
            cat > "$CLAWDBOT_DIR/clawdbot" << 'WRAPPER'
#!/bin/bash
exec node /app/backend/node_modules/clawdbot/bin/clawdbot.js "$@"
WRAPPER
            chmod +x "$CLAWDBOT_DIR/clawdbot"
            echo "✓ Local installation successful"
            exit 0
        fi
    }
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
fi

# If not in PATH, check common npm global locations
for BIN_DIR in "$NPM_BIN" "/root/.nix-profile/bin" "/nix/var/nix/profiles/default/bin" "/usr/local/bin"; do
    if [ -f "$BIN_DIR/clawdbot" ]; then
        echo "Found clawdbot at: $BIN_DIR/clawdbot"
        ln -sf "$BIN_DIR/clawdbot" "$CLAWDBOT_DIR/clawdbot"
        echo "✓ Installation successful (found in $BIN_DIR)"
        exit 0
    fi
done

# Check if it was installed but not in PATH
if [ -f "$NPM_PREFIX/lib/node_modules/clawdbot/bin/clawdbot.js" ]; then
    echo "Found clawdbot in node_modules, creating wrapper..."
    cat > "$CLAWDBOT_DIR/clawdbot" << WRAPPER
#!/bin/bash
exec node $NPM_PREFIX/lib/node_modules/clawdbot/bin/clawdbot.js "\$@"
WRAPPER
    chmod +x "$CLAWDBOT_DIR/clawdbot"
    echo "✓ Installation successful (created wrapper)"
    exit 0
fi

echo "WARNING: clawdbot command not found after installation"
echo "Trying official installer with non-interactive mode..."

# Try the official installer as fallback (non-interactive)
export OPENCLAW_SKIP_SETUP=1  # Skip interactive setup
curl -fsSL https://molt.bot/install.sh -o /tmp/install_moltbot.sh
chmod +x /tmp/install_moltbot.sh

# Run installer in non-interactive mode
bash /tmp/install_moltbot.sh </dev/null || true

# Check again after official installer
for BIN_DIR in "$NPM_BIN" "/root/.nix-profile/bin" "/nix/var/nix/profiles/default/bin" "/usr/local/bin" "$HOME/.local/bin"; do
    if [ -f "$BIN_DIR/clawdbot" ] || [ -f "$BIN_DIR/openclaw" ]; then
        FOUND_CMD="$BIN_DIR/clawdbot"
        [ ! -f "$FOUND_CMD" ] && FOUND_CMD="$BIN_DIR/openclaw"
        echo "Found OpenClaw at: $FOUND_CMD"
        ln -sf "$FOUND_CMD" "$CLAWDBOT_DIR/clawdbot"
        echo "✓ Alternative installation successful!"
        exit 0
    fi
done

# Last resort: check if npm package was installed and create direct node wrapper
if [ -d "$NPM_PREFIX/lib/node_modules/clawdbot" ]; then
    echo "Package installed but binary not accessible, creating direct wrapper..."
    cat > "$CLAWDBOT_DIR/clawdbot" << 'WRAPPER'
#!/bin/bash
# Find the clawdbot.js file
for DIR in /root/.nix-profile/lib/node_modules/clawdbot /usr/local/lib/node_modules/clawdbot /app/backend/node_modules/clawdbot; do
    if [ -f "$DIR/bin/clawdbot.js" ]; then
        exec node "$DIR/bin/clawdbot.js" "$@"
    fi
done
echo "ERROR: clawdbot.js not found" >&2
exit 1
WRAPPER
    chmod +x "$CLAWDBOT_DIR/clawdbot"
    echo "✓ Created direct wrapper"
    exit 0
fi

echo "ERROR: Unable to install or locate clawdbot"
echo "This is not fatal - installation will be retried at runtime if needed"
exit 0  # Don't fail the build, let runtime handle it
