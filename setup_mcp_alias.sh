#!/bin/bash

# Setup MCP Automation Alias
# This script sets up shell aliases for easy MCP automation access

echo "🔧 Setting up MCP Automation Aliases..."
echo "========================================"

# Determine shell configuration file
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
    echo "📝 Detected Zsh shell, using ~/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
    echo "📝 Detected Bash shell, using ~/.bashrc"
else
    echo "⚠️  Unknown shell: $SHELL"
    echo "📝 Using ~/.bashrc as default"
    SHELL_RC="$HOME/.bashrc"
fi

# MCP alias command
MCP_ALIAS="alias MCP='/Users/tradecomp/Desktop/VOPP/viper-/mcp'"
MCP_ALIAS_LOWER="alias mcp='/Users/tradecomp/Desktop/VOPP/viper-/mcp'"

# Check if aliases already exist
if grep -q "alias MCP=" "$SHELL_RC" 2>/dev/null; then
    echo "✅ MCP alias already exists in $SHELL_RC"
else
    echo "📝 Adding MCP alias to $SHELL_RC"

    # Add aliases to shell config
    echo "" >> "$SHELL_RC"
    echo "# MCP Automation Aliases" >> "$SHELL_RC"
    echo "$MCP_ALIAS" >> "$SHELL_RC"
    echo "$MCP_ALIAS_LOWER" >> "$SHELL_RC"

    echo "✅ MCP aliases added successfully!"
fi

# Add MCP function for more advanced usage
MCP_FUNCTION=$(cat << 'EOF'

# MCP Automation Function
mcp_analyze() {
    echo "🤖 MCP Trading Bot Analysis"
    echo "==========================="
    cd /Users/tradecomp/Desktop/VOPP/viper-
    python3 mcp_automation.py "$@"
}

# Quick MCP commands
mcp_logs() {
    echo "📋 Recent MCP Analysis Logs:"
    ls -la /Users/tradecomp/Desktop/VOPP/viper-/reports/mcp_analysis_*.json 2>/dev/null || echo "No MCP analysis reports found"
}

mcp_status() {
    echo "📊 System Status:"
    if pgrep -f "jordan_mainnet_trader.py" > /dev/null; then
        echo "✅ Trading bot is running"
    else
        echo "❌ Trading bot is not running"
    fi

    if [ -f "/Users/tradecomp/Desktop/VOPP/viper-/logs/jordan_mainnet_trader.log" ]; then
        echo "✅ Log file exists"
        echo "📅 Last log update: $(stat -f "%Sm" /Users/tradecomp/Desktop/VOPP/viper-/logs/jordan_mainnet_trader.log)"
    else
        echo "❌ Log file not found"
    fi
}

EOF
)

# Add function if it doesn't exist
if ! grep -q "mcp_analyze()" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "$MCP_FUNCTION" >> "$SHELL_RC"
    echo "✅ MCP functions added successfully!"
else
    echo "✅ MCP functions already exist"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo "You can now use the following commands:"
echo "• MCP          - Run full trading bot analysis"
echo "• mcp          - Same as MCP (lowercase)"
echo "• mcp_analyze  - Advanced analysis with options"
echo "• mcp_logs     - View recent analysis reports"
echo "• mcp_status   - Quick system status check"
echo ""
echo "Please restart your terminal or run: source $SHELL_RC"
echo "Then simply type 'MCP' to start the analysis!"
