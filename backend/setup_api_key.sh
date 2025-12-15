#!/bin/bash
# Script to help set up BRIA API key

echo "🔑 BRIA API Key Setup"
echo "======================"
echo ""
echo "Please enter your BRIA API key:"
echo "(You can copy it from the BRIA dashboard)"
echo ""
read -s -p "API Key: " API_KEY
echo ""

if [ -z "$API_KEY" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Create or update .env file
if [ ! -f .env ]; then
    echo "Creating .env file from env.example..."
    cp env.example .env
fi

# Update BRIA_API_TOKEN in .env
if grep -q "BRIA_API_TOKEN" .env; then
    # Replace existing token
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|BRIA_API_TOKEN=.*|BRIA_API_TOKEN=$API_KEY|" .env
    else
        # Linux
        sed -i "s|BRIA_API_TOKEN=.*|BRIA_API_TOKEN=$API_KEY|" .env
    fi
    echo "✅ Updated BRIA_API_TOKEN in .env"
else
    # Add new token
    echo "BRIA_API_TOKEN=$API_KEY" >> .env
    echo "✅ Added BRIA_API_TOKEN to .env"
fi

echo ""
echo "✅ API key configured successfully!"
echo ""
echo "You can now start the backend server:"
echo "  python3 main.py"
echo ""




