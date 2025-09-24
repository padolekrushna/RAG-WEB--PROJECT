#!/bin/bash
# azure/scripts/deploy.sh
set -e

# Configuration
RESOURCE_GROUP="rag-document-qa-rg"
LOCATION="eastus"
APP_NAME="rag-document-qa"
SUBSCRIPTION_ID=""  # Set your subscription ID

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    echo_info "Checking prerequisites..."
    
    if ! command -v az &> /dev/null; then
        echo_error "Azure CLI not found. Please install Azure CLI."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check if logged in to Azure
    if ! az account show &> /dev/null; then
        echo_error "Not logged in to Azure. Run 'az login' first."
        exit 1
    fi
    
    echo_info "Prerequisites check passed!"
}

# Create resource group
create_resource_group() {
    echo_info "Creating resource group: $RESOURCE_GROUP"
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
}

# Deploy infrastructure
deploy_infrastructure() {
    echo_info "Deploying Azure infrastructure..."
    
    DEPLOYMENT_NAME="rag-deployment-$(date +%Y%m%d-%H%M%S)"
    
    az deployment group create \
        --resource-group $RESOURCE_GROUP \
        --template-file ../arm-templates/main.json \
        --parameters appName=$APP_NAME \
        --parameters location=$LOCATION \
        --name $DEPLOYMENT_NAME \
        --output table
    
    # Get outputs
    CONTAINER_REGISTRY=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query 'properties.outputs.containerRegistryName.value' \
        --output tsv)
    
    STORAGE_ACCOUNT=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query 'properties.outputs.storageAccountName.value' \
        --output tsv)
    
    echo_info "Container Registry: $CONTAINER_REGISTRY"
    echo_info "Storage Account: $STORAGE_ACCOUNT"
    
    # Store in variables file for later use
    cat > ../deployment-vars.env << EOF
CONTAINER_REGISTRY=$CONTAINER_REGISTRY
STORAGE_ACCOUNT=$STORAGE_ACCOUNT
RESOURCE_GROUP=$RESOURCE_GROUP
EOF
}

# Build and push Docker images
build_and_push_images() {
    echo_info "Building and pushing Docker images..."
    
    # Source deployment variables
    source ../deployment-vars.env
    
    # Login to ACR
    az acr login --name $CONTAINER_REGISTRY
    
    # Build and push backend
    echo_info "Building backend image..."
    docker build -t $CONTAINER_REGISTRY.azurecr.io/rag-backend:latest ../../backend/
    docker push $CONTAINER_REGISTRY.azurecr.io/rag-backend:latest
    
    # Build and push frontend
    echo_info "Building frontend image..."
    docker build -t $CONTAINER_REGISTRY.azurecr.io/rag-frontend:latest ../../frontend/
    docker push $CONTAINER_REGISTRY.azurecr.io/rag-frontend:latest
}

# Update container apps with new images
update_container_apps() {
    echo_info "Updating Container Apps..."
    
    # Source deployment variables
    source ../deployment-vars.env
    
    # Update backend
    az containerapp update \
        --name "${APP_NAME}-backend" \
        --resource-group $RESOURCE_GROUP \
        --image $CONTAINER_REGISTRY.azurecr.io/rag-backend:latest
    
    # Update frontend
    az containerapp update \
        --name "${APP_NAME}-frontend" \
        --resource-group $RESOURCE_GROUP \
        --image $CONTAINER_REGISTRY.azurecr.io/rag-frontend:latest
}

# Get deployment URLs
get_deployment_urls() {
    echo_info "Getting deployment URLs..."
    
    FRONTEND_URL=$(az containerapp show \
        --name "${APP_NAME}-frontend" \
        --resource-group $RESOURCE_GROUP \
        --query 'properties.configuration.ingress.fqdn' \
        --output tsv)
    
    BACKEND_URL=$(az containerapp show \
        --name "${APP_NAME}-backend" \
        --resource-group $RESOURCE_GROUP \
        --query 'properties.configuration.ingress.fqdn' \
        --output tsv)
    
    echo_info "Deployment completed successfully!"
    echo_info "Frontend URL: https://$FRONTEND_URL"
    echo_info "Backend URL: https://$BACKEND_URL"
    echo_info "Backend API: https://$BACKEND_URL/api/v1"
    
    # Save URLs to file
    cat > ../deployment-urls.txt << EOF
Frontend: https://$FRONTEND_URL
Backend: https://$BACKEND_URL
API: https://$BACKEND_URL/api/v1
EOF
}

# Main execution
main() {
    echo_info "Starting RAG Document Q&A deployment to Azure..."
    
    check_prerequisites
    create_resource_group
    deploy_infrastructure
    build_and_push_images
    update_container_apps
    get_deployment_urls
    
    echo_info "Deployment script completed!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

#!/bin/bash
# azure/scripts/setup-storage.sh
set -e

# Configuration
source ../deployment-vars.env

echo "Setting up Azure Storage for RAG system..."

# Create containers in storage account
az storage container create \
    --name "rag-documents" \
    --account-name $STORAGE_ACCOUNT \
    --public-access off

az storage container create \
    --name "rag-indexes" \
    --account-name $STORAGE_ACCOUNT \
    --public-access off

az storage container create \
    --name "rag-logs" \
    --account-name $STORAGE_ACCOUNT \
    --public-access off

# Set CORS rules for web access
az storage cors add \
    --services b \
    --methods GET POST PUT DELETE OPTIONS \
    --origins "*" \
    --allowed-headers "*" \
    --exposed-headers "*" \
    --max-age 3600 \
    --account-name $STORAGE_ACCOUNT

echo "Azure Storage setup completed!"

# backend/app/__init__.py
"""
RAG Document Q&A Backend Application
"""

__version__ = "1.0.0"
__author__ = "RAG Team"
__description__ = "Backend API for RAG Document Q&A System"

# backend/app/utils/helpers.py
import os
import hashlib
import mimetypes
from typing import Optional

def get_file_hash(file_path: str) -> str:
    """Generate SHA-256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def get_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def ensure_directory(directory: str) -> None:
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

# frontend/src/utils/helpers.js
/**
 * Format file size to human readable format
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Get file icon based on file type
 */
export const getFileIcon = (contentType) => {
  if (contentType === 'application/pdf') return '📄';
  if (contentType === 'text/plain') return '📝';
  if (contentType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') return '📘';
  return '📋';
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text, maxLength = 100) => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Format timestamp
 */
export const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString();
};

/**
 * Validate file type
 */
export const isValidFileType = (file) => {
  const validTypes = [
    'application/pdf',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];
  
  return validTypes.includes(file.type);
};

# .env.example (root level)
# Backend Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
AZURE_CONTAINER_NAME=rag-documents

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_APP_NAME=RAG Document Q&A System

# Development
NODE_ENV=development
DEBUG=true

# Production
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-backend-domain.com

# .gitignore
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
/frontend/build
/backend/dist
*.log

# Storage
/storage/uploads/*
/storage/indexes/*
/storage/logs/*
!/storage/.gitkeep

# Azure
/azure/deployment-vars.env
/azure/deployment-urls.txt

# Docker
.dockerignore

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
