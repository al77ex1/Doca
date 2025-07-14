# Doca - Document Assistant

Doca is a system that enables semantic search over markdown documents using embeddings and Elasticsearch.

## Setup

1. Make sure Elasticsearch is running:
```bash
docker-compose up -d
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Indexing Documents

To index your markdown documents, use the `indexer.py` script:

```bash
python indexer.py /path/to/your/markdown/documents
```

### Options

- `--es-host`: Elasticsearch host URL (default: http://localhost:9200)
- `--index-name`: Elasticsearch index name (default: doca_documents)
- `--model`: Sentence transformer model name (default: paraphrase-multilingual-MiniLM-L12-v2)
- `--chunk-size`: Text chunk size in characters (default: 512)
- `--chunk-overlap`: Overlap between chunks in characters (default: 128)
- `--no-recursive`: Don't recursively search for markdown files

## Examples

Index documents in a specific folder:
```bash
python indexer.py ~/Documents/notes
```

Use a different embedding model:
```bash
python indexer.py ~/Documents/notes --model all-MiniLM-L6-v2
```

Change chunk size and overlap:
```bash
python indexer.py ~/Documents/notes --chunk-size 1024 --chunk-overlap 256
```
