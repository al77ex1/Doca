# Doca - Document Assistant

Doca is a system that enables semantic search over markdown documents using embeddings and Elasticsearch. The system allows a locally running LLM (e.g., in LM Studio) to search through documents and provide answers based on the content.

## Project Structure

The project is structured into two main components:

- `back/`: Backend server with WebSocket support for document indexing
- `front/`: React frontend for interacting with the backend

## Setup

### Prerequisites

1. Make sure Elasticsearch is running:

```bash
docker-compose up -d
```

### Backend Setup

1. Install the required Python packages:

```bash
cd back
pip install -r requirements.txt
```

1. Start the backend server:

```bash
python server.py
```

The server will start on [http://localhost:8000](http://localhost:8000)

### Frontend Setup

1. Install the required Node.js packages:

```bash
cd front
npm install
```

1. Start the frontend development server:

```bash
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173)

## Features

### Document Indexing

The system now provides a web interface for indexing documents with real-time progress updates via WebSockets. You can:

- Select a directory to index
- Choose whether to recursively search subdirectories
- View real-time progress during indexing
- See statistics about indexed documents

### Command Line Interface

You can still use the command line interface for indexing:

```bash
cd back
python -m src.cli /path/to/your/markdown/documents
```

#### CLI Options

- `--es-host`: Elasticsearch host URL (default: [http://localhost:9200](http://localhost:9200))
- `--index-name`: Elasticsearch index name (default: doca_documents)
- `--model`: Sentence transformer model name (default: paraphrase-multilingual-MiniLM-L12-v2)
- `--chunk-size`: Text chunk size in characters (default: 512)
- `--chunk-overlap`: Overlap between chunks in characters (default: 128)
- `--no-recursive`: Don't recursively search for markdown files

## Examples

Index documents in a specific folder via CLI:

```bash
cd back
python -m doca.cli ~/Documents/notes
```

Use a different embedding model:

```bash
python -m src.cli ~/Documents/notes --model all-MiniLM-L6-v2
```

Change chunk size and overlap:

```bash
python -m src.cli ~/Documents/notes --chunk-size 1024 --chunk-overlap 256
```
