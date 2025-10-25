#!/bin/bash

# OSInt-AI DigitalOcean Deployment Script
# This script automates the deployment of OSInt-AI to DigitalOcean

set -e  # Exit on error

echo "🚀 OSInt-AI DigitalOcean Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "ℹ $1"; }

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_error "doctl is not installed"
    echo "Install it with: brew install doctl (macOS) or snap install doctl (Linux)"
    exit 1
fi
print_success "doctl is installed"

# Check if user is authenticated
if ! doctl auth list &> /dev/null; then
    print_error "Not authenticated with DigitalOcean"
    echo "Run: doctl auth init"
    exit 1
fi
print_success "Authenticated with DigitalOcean"

# Get user inputs
echo ""
print_info "Please provide the following information:"

read -p "GitHub username: " GITHUB_USERNAME
read -p "GitHub repository name (default: osint-ai): " REPO_NAME
REPO_NAME=${REPO_NAME:-osint-ai}

read -p "DigitalOcean region (default: nyc3): " REGION
REGION=${REGION:-nyc3}

read -sp "Gradient AI API Key: " GRADIENT_API_KEY
echo ""

read -sp "GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

read -sp "Secret Key (press Enter to generate): " SECRET_KEY
echo ""
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -base64 32)
    print_info "Generated secret key"
fi

echo ""
print_info "Starting deployment..."

# Step 1: Create Container Registry
echo ""
print_info "Step 1: Creating Container Registry..."
if doctl registry get osint-ai &> /dev/null; then
    print_warning "Container registry 'osint-ai' already exists"
else
    doctl registry create osint-ai --region $REGION
    print_success "Container registry created"
fi

# Step 2: Create Managed Database
echo ""
print_info "Step 2: Creating PostgreSQL Database..."
if doctl databases list | grep -q "osint-ai-db"; then
    print_warning "Database 'osint-ai-db' already exists"
    DB_ID=$(doctl databases list --format ID,Name --no-header | grep "osint-ai-db" | awk '{print $1}')
else
    DB_ID=$(doctl databases create osint-ai-db \
        --engine pg \
        --region $REGION \
        --size db-s-1vcpu-1gb \
        --version 15 \
        --format ID --no-header)
    print_success "Database created with ID: $DB_ID"
    print_info "Waiting for database to be ready (this may take a few minutes)..."
    sleep 60
fi

# Get database connection details
DB_CONNECTION=$(doctl databases connection $DB_ID --format URI --no-header)
print_success "Database connection string retrieved"

# Step 3: Update App Spec
echo ""
print_info "Step 3: Updating app specification..."
sed -i.bak "s|YOUR_GITHUB_USERNAME|$GITHUB_USERNAME|g" .do/app.yaml
print_success "App spec updated"

# Step 4: Create App Platform App
echo ""
print_info "Step 4: Creating App Platform application..."

# Create a temporary spec with secrets
cat > /tmp/osint-ai-spec.yaml << EOF
name: osint-ai
region: $REGION

services:
  - name: backend
    dockerfile_path: Dockerfile.backend
    source_dir: /
    github:
      repo: $GITHUB_USERNAME/$REPO_NAME
      branch: main
      deploy_on_push: true
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xs
    
    routes:
      - path: /api
    
    health_check:
      http_path: /api/v1/health
      initial_delay_seconds: 30
      period_seconds: 10
      timeout_seconds: 5
    
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: "$DB_CONNECTION"
      
      - key: GRADIENT_AI_ENDPOINT
        scope: RUN_TIME
        value: "https://api.digitalocean.com/v2/ai"
      
      - key: GRADIENT_AI_API_KEY
        scope: RUN_TIME
        value: "$GRADIENT_API_KEY"
      
      - key: GITHUB_TOKEN
        scope: RUN_TIME
        value: "$GITHUB_TOKEN"
      
      - key: SECRET_KEY
        scope: RUN_TIME
        value: "$SECRET_KEY"
      
      - key: DEBUG
        scope: RUN_TIME
        value: "False"
      
      - key: LOG_LEVEL
        scope: RUN_TIME
        value: "INFO"

  - name: frontend
    dockerfile_path: Dockerfile.frontend
    source_dir: /
    github:
      repo: $GITHUB_USERNAME/$REPO_NAME
      branch: main
      deploy_on_push: true
    http_port: 3000
    instance_count: 1
    instance_size_slug: basic-xs
    
    routes:
      - path: /
    
    envs:
      - key: VITE_API_BASE_URL
        scope: BUILD_TIME
        value: "https://\${APP_URL}/api"
EOF

# Create the app
APP_ID=$(doctl apps create --spec /tmp/osint-ai-spec.yaml --format ID --no-header)
rm /tmp/osint-ai-spec.yaml
print_success "App created with ID: $APP_ID"

# Step 5: Wait for deployment
echo ""
print_info "Step 5: Waiting for initial deployment..."
print_info "This may take 5-10 minutes..."

while true; do
    STATUS=$(doctl apps get $APP_ID --format ActiveDeployment.Phase --no-header)
    if [ "$STATUS" == "ACTIVE" ]; then
        print_success "Deployment successful!"
        break
    elif [ "$STATUS" == "ERROR" ]; then
        print_error "Deployment failed"
        doctl apps get $APP_ID
        exit 1
    else
        echo -n "."
        sleep 10
    fi
done

# Step 6: Get app URL
echo ""
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)
print_success "Application deployed successfully!"

# Summary
echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "Application URL: https://$APP_URL"
echo "Backend API: https://$APP_URL/api"
echo "API Docs: https://$APP_URL/api/docs"
echo "Frontend Dashboard: https://$APP_URL/"
echo ""
echo "App ID: $APP_ID"
echo "Database ID: $DB_ID"
echo ""
echo "To view app details: doctl apps get $APP_ID"
echo "To view logs: doctl apps logs $APP_ID"
echo "To update the app: doctl apps update $APP_ID --spec .do/app.yaml"
echo ""
print_success "Save these IDs for future reference!"

# Create a .env.production file with the details
cat > .env.production << EOF
# DigitalOcean Deployment Details
APP_ID=$APP_ID
DATABASE_ID=$DB_ID
APP_URL=https://$APP_URL
REGION=$REGION

# API Keys (DO NOT COMMIT THIS FILE)
GRADIENT_AI_API_KEY=$GRADIENT_API_KEY
GITHUB_TOKEN=$GITHUB_TOKEN
SECRET_KEY=$SECRET_KEY

# Database
DATABASE_URL=$DB_CONNECTION
EOF

print_success ".env.production file created (DO NOT COMMIT THIS FILE)"

echo ""
print_warning "Next steps:"
echo "1. Add secrets to GitHub:"
echo "   - DIGITALOCEAN_ACCESS_TOKEN"
echo "   - APP_ID (value: $APP_ID)"
echo "   - GRADIENT_AI_ENDPOINT"
echo "   - GRADIENT_AI_API_KEY"
echo "   - GITHUB_TOKEN"
echo "   - SECRET_KEY"
echo ""
echo "2. Push your code to GitHub"
echo "3. GitHub Actions will automatically deploy on push to main"
echo ""
echo "4. Visit your application at: https://$APP_URL"
