# PocketBase MCP Service for RAG Integration

This MCP (Model Context Protocol) service provides read-only access to your PocketBase SQLite database, allowing you to integrate table data into your RAG (Retrieval-Augmented Generation) system.

## Features

- Read-only access to PocketBase database tables
- RESTful API for querying table data
- Support for filtering and pagination
- Table schema information
- CORS support for web integration

## Installation

1. Ensure you have Python 3.6+ installed
2. The service uses only standard Python libraries, so no additional installation is required

## Usage

### Starting the Service

```bash
# Start with default settings (localhost:8765)
python pocketbase_mcp_service.py

# Specify host and port
python pocketbase_mcp_service.py --host 127.0.0.1 --port 9000
```

### API Endpoints

The service provides the following endpoints:

#### List All Tables

```
GET /tables
```

Returns a list of all tables in the database.

Example response:
```json
{
  "tables": ["_collections", "_migrations", "infos", "sites", "users", ...]
}
```

#### Get Table Schema

```
GET /tables/{table_name}/schema
```

Returns the schema information for a specific table.

Example response:
```json
{
  "schema": [
    {"name": "content", "type": "TEXT"},
    {"name": "created", "type": "TEXT"},
    {"name": "id", "type": "TEXT"},
    {"name": "report", "type": "TEXT"},
    {"name": "tag", "type": "TEXT"},
    {"name": "updated", "type": "TEXT"},
    {"name": "url", "type": "TEXT"},
    {"name": "screenshot", "type": "TEXT"},
    {"name": "url_title", "type": "TEXT"},
    {"name": "references", "type": "JSON"}
  ]
}
```

#### Query Table Data

```
GET /tables/{table_name}/data?limit=100&offset=0&{filter_key}={filter_value}
```

Returns data from a specific table with optional filtering and pagination.

Parameters:
- `limit`: Maximum number of records to return (default: 100)
- `offset`: Number of records to skip (default: 0)
- Any other parameter will be treated as a filter (e.g., `tag=poker` will filter records where the tag field contains "poker")

Example response:
```json
{
  "data": [
    {
      "content": "//SplitSuit Poker 2025-01-05//1：\n1. 如何从大盲位防守：GTO批准的方法。\n2. 使用MDF并不是真正的GTO：MDF解释。\n...",
      "created": "2025-01-05 11:07:19.464Z",
      "id": "d9021960q2l1702",
      "report": "",
      "tag": "6w7f5iuv21347av",
      "updated": "2025-01-05 11:07:19.464Z",
      "url": "https://www.getcoach.poker/schools/splitsuit-poker/",
      "screenshot": "",
      "url_title": "SplitSuit Poker poker school | Getcoach.poker",
      "references": "{}"
    },
    ...
  ],
  "count": 100,
  "limit": 100,
  "offset": 0
}
```

## Integration with RAG Systems

### Example: Using with LangChain

```python
import requests
import json
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Connect to the MCP service
MCP_SERVICE_URL = "http://localhost:8765"

# Fetch data from the infos table
response = requests.get(f"{MCP_SERVICE_URL}/tables/infos/data?limit=1000")
data = response.json()["data"]

# Convert to LangChain documents
documents = []
for item in data:
    # Create metadata from all fields except content
    metadata = {k: v for k, v in item.items() if k != "content"}
    
    # Create document
    doc = Document(
        page_content=item["content"],
        metadata=metadata
    )
    documents.append(doc)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

# Now you can use this vectorstore in your RAG pipeline
retriever = vectorstore.as_retriever()
```

### Example: Using with LlamaIndex

```python
import requests
import json
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser

# Connect to the MCP service
MCP_SERVICE_URL = "http://localhost:8765"

# Fetch data from the infos table
response = requests.get(f"{MCP_SERVICE_URL}/tables/infos/data?limit=1000")
data = response.json()["data"]

# Convert to LlamaIndex documents
documents = []
for item in data:
    # Create metadata from all fields except content
    metadata = {k: v for k, v in item.items() if k != "content"}
    
    # Create document
    doc = Document(
        text=item["content"],
        metadata=metadata
    )
    documents.append(doc)

# Parse documents into nodes
parser = SimpleNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# Create vector index
index = VectorStoreIndex(nodes)

# Now you can use this index in your RAG pipeline
query_engine = index.as_query_engine()
```

## Security Considerations

- This service provides read-only access to your database
- No authentication is implemented by default - secure your deployment as needed
- Consider running behind a reverse proxy for additional security
- Limit the service to localhost if you don't need remote access

## Limitations

- The service only provides read access to the database
- Large result sets may impact performance
- The service does not handle database schema changes automatically
