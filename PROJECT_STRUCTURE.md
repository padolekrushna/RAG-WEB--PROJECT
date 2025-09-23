rag-document-qa-azure/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── document_processor.py
│   │   │   ├── vector_store.py
│   │   │   └── rag_pipeline.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUpload.js
│   │   │   ├── ChatInterface.js
│   │   │   ├── FileManager.js
│   │   │   └── SearchResults.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   └── main.css
│   │   ├── utils/
│   │   │   └── helpers.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── storage/
│   ├── uploads/
│   ├── indexes/
│   └── logs/
├── azure/
│   ├── arm-templates/
│   │   ├── main.json
│   │   └── parameters.json
│   ├── scripts/
│   │   ├── deploy.sh
│   │   └── setup-storage.sh
│   └── docker-compose.azure.yml
├── .env.example
├── .gitignore
└── README.md
