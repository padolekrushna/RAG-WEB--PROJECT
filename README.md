# RAG Document Q&A System - Azure Deployment

A modern, scalable RAG (Retrieval Augmented Generation) system for document question-answering using React frontend, FastAPI backend, FAISS vector search, and Google Gemini AI. Designed for Azure Container Apps deployment with proper separation of concerns.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  Azure Storage  │
│   (Nginx + SPA)  │◄──►│   (Python API)   │◄──►│   (Blob + Files)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │  Azure Container │
                    │      Apps        │
                    └─────────────────┘
```

## 🚀 Features

- **Modern Tech Stack**: React 18, FastAPI, FAISS, Google Gemini AI
- **Cloud-Native**: Azure Container Apps with auto-scaling
- **Multi-Format Support**: PDF, TXT, DOCX document processing
- **Vector Search**: FAISS-powered semantic search with TF-IDF embeddings
- **Real-time Chat**: Interactive Q&A interface with source citations
- **Production Ready**: Docker containers, health checks, monitoring
- **Secure Storage**: Azure Blob Storage for documents and indexes

## 📁 Project Structure

```
rag-document-qa-azure/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Business logic (RAG, Vector Store)
│   │   ├── models/         # Pydantic schemas
│   │   └── main.py         # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service layer
│   │   ├── styles/         # CSS styling
│   │   └── App.js          # Main React app
│   ├── Dockerfile
│   └── package.json
├── azure/                  # Azure deployment
│   ├── arm-templates/      # Infrastructure as Code
│   ├── scripts/           # Deployment scripts
│   └── docker-compose.azure.yml
└── storage/               # Local development storage
```

## 🛠️ Prerequisites

### Development
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Google Gemini API key

### Azure Deployment
- Azure CLI installed and configured
- Azure subscription with Container Apps enabled
- Docker for building images

## 🔧 Local Development Setup

### 1. Clone and Setup Environment

```bash
git clone <your-repo>
cd rag-document-qa-azure
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file:
```bash
GOOGLE_API_KEY=your_actual_gemini_api_key_here
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend will be available at: http://localhost:3000

### 5. Using Docker Compose (Recommended)

```bash
# Build and run both services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ☁️ Azure Deployment

### 1. Prepare Azure Environment

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Navigate to deployment scripts
cd azure/scripts
```

### 2. Configure Deployment

Edit variables in `deploy.sh`:
```bash
RESOURCE_GROUP="rag-document-qa-rg"
LOCATION="eastus"  # Choose your preferred region
APP_NAME="rag-document-qa"
```

### 3. Run Deployment

```bash
# Make scripts executable
chmod +x deploy.sh setup-storage.sh

# Run complete deployment
./deploy.sh
```

This will:
- Create Azure Resource Group
- Deploy Container Registry
- Deploy Container Apps Environment
- Deploy Storage Account
- Build and push Docker images
- Deploy backend and frontend apps
- Configure networking and scaling

### 4. Post-Deployment Configuration

The script will output your deployment URLs:
```
Frontend: https://your-frontend-app.azurecontainerapps.io
Backend: https://your-backend-app.azurecontainerapps.io
API: https://your-backend-app.azurecontainerapps.io/api/v1
```

Update your frontend environment variables if needed:
```bash
# In Azure Portal or via CLI
az containerapp update \
    --name rag-document-qa-frontend \
    --resource-group rag-document-qa-rg \
    --set-env-vars REACT_APP_API_URL=https://your-backend-domain/api/v1
```

## 📖 Usage Guide

### 1. Access the Application
Open your deployed frontend URL in a browser.

### 2. Configure API Key
- Enter your Google Gemini API key in the sidebar
- The key is stored in browser localStorage for convenience

### 3. Upload Documents
- Drag and drop or click to select PDF, TXT, or DOCX files
- Multiple files supported
- Files are uploaded to Azure Blob Storage

### 4. Process Documents
- Click "Process Documents" after uploading
- This creates vector embeddings and FAISS index
- Processing status shown in sidebar

### 5. Ask Questions
- Type questions in the chat interface
- System provides answers with source citations
- Confidence scores indicate answer quality

### 6. Monitor System
- View document statistics in sidebar
- Check processing status and memory usage
- Clear chat or reset system as needed

## 🔧 API Endpoints

### Document Management
- `POST /api/v1/documents/upload` - Upload documents
- `POST /api/v1/documents/process` - Process documents and create index
- `GET /api/v1/documents/stats` - Get system statistics
- `DELETE /api/v1/documents/clear` - Clear all documents

### Query Interface
- `POST /api/v1/query` - Query documents with RAG
- `GET /api/v1/documents/similar-questions/{query}` - Get similar questions

### Health & Monitoring
- `GET /api/v1/health` - Health check endpoint
- `GET /` - Root endpoint with service info

## 🔐 Security Considerations

### API Key Management
- Store Gemini API key securely (Azure Key Vault recommended for production)
- Use environment variables, never hardcode keys
- Implement API key rotation policies

### Azure Security
- Container Apps with managed identity
- Storage account with private endpoints
- Network security groups and firewall rules
- HTTPS-only communication

### Input Validation
- File type and size validation
- Query sanitization
- Rate limiting on API endpoints

## 📊 Monitoring & Observability

### Built-in Monitoring
- Azure Container Apps logs
- Application Insights integration
- Health check endpoints
- Custom metrics and dashboards

### Log Analysis
```bash
# View container logs
az containerapp logs show \
    --name rag-document-qa-backend \
    --resource-group rag-document-qa-rg \
    --follow

# View frontend logs
az containerapp logs show \
    --name rag-document-qa-frontend \
    --resource-group rag-document-qa-rg \
    --follow
```

## 🔄 CI/CD Pipeline

### GitHub Actions Setup (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and deploy
      run: |
        cd azure/scripts
        ./deploy.sh
```

## 🐛 Troubleshooting

### Common Issues

**1. Backend fails to start**
```bash
# Check logs
az containerapp logs show --name rag-document-qa-backend --resource-group rag-document-qa-rg

# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Storage connection issues
```

**2. Frontend can't connect to backend**
```bash
# Check CORS settings in backend
# Verify REACT_APP_API_URL is correct
# Check network connectivity
```

**3. Document processing fails**
```bash
# Check file formats are supported
# Verify API key is valid
# Check storage permissions
```

**4. Vector search returns no results**
```bash
# Ensure documents were processed successfully
# Check embedding creation
# Verify FAISS index was built
```

### Debug Mode

Enable debug logging:
```bash
# Backend
export DEBUG=true
export LOG_LEVEL=DEBUG

# Frontend
export REACT_APP_DEBUG=true
```

## 🔧 Customization

### Adding New Document Types
1. Update `document_processor.py` with new extraction logic
2. Add MIME type to allowed types in config
3. Update frontend file validation

### Custom Embedding Models
1. Modify `vector_store.py` to use different embedding providers
2. Update embedding dimension configuration
3. Rebuild FAISS indexes

### UI Customization
1. Modify `main.css` for styling changes
2. Update React components for new features
3. Add new API endpoints as needed

## 📈 Scaling Considerations

### Horizontal Scaling
- Container Apps auto-scaling configured
- Stateless backend design
- Shared storage for documents and indexes

### Performance Optimization
- Implement caching for frequent queries
- Optimize embedding batch processing
- Use Azure CDN for static assets

### Cost Optimization
- Monitor resource usage
- Implement auto-shutdown for development
- Use spot instances for non-production workloads

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Test full pipeline
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📚 Additional Resources

### Documentation Links
- [Azure Container Apps](https://docs.microsoft.com/en-us/azure/container-apps/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Google Gemini AI](https://ai.google.dev/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)

### Learning Resources
- RAG system architecture patterns
- Vector database optimization
- Azure Container Apps best practices
- React performance optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write comprehensive tests
- Update documentation for changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with:
   - Environment details
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs

## 🔮 Roadmap

### Planned Features
- Multi-language support
- Advanced analytics dashboard
- Batch document processing
- Integration with other AI models
- Enhanced security features
- Mobile app support

### Performance Improvements
- Redis caching layer
- Streaming responses
- Progressive document loading
- Advanced query optimization

---

**Built with ❤️ for scalable document intelligence**
