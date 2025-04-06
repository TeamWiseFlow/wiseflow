# Wiseflow: Intelligent Continuous Data Mining

Wiseflow is an AI-powered information extraction tool that uses LLMs to mine relevant information from various sources based on user-defined focus points. It employs a "wide search" approach for broad information collection rather than "deep search" for specific questions.

## New Features

- **Plugin System**: Modular architecture with plugins for data sources and processors
- **Multi-threading and Concurrency**: Process multiple data sources concurrently
- **Reference Support**: Attach reference materials to focus points
- **Auto-shutdown**: Automatically shut down tasks when they're completed
- **Enhanced Connectors**: Support for web, GitHub, and more data sources
- **Task Management**: Track and monitor running tasks

## Installation

### Prerequisites

- Python 3.8+
- PocketBase (for database)
- LLM API keys (OpenAI, Anthropic, etc.)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/wiseflow.git
   cd wiseflow
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp core/.env.example core/.env
   ```
   Edit the `.env` file to add your API keys and configuration.

4. Set up PocketBase:
   - Download and run PocketBase from [pocketbase.io](https://pocketbase.io)
   - Create an admin account
   - Run the schema update script:
     ```bash
     python -m core.utils.schema_update
     ```
   - Follow the instructions to create any missing collections

## Usage

### Running Wiseflow

Start the enhanced task runner:

```bash
python -m core.run_task_new
```

### Creating Focus Points

1. Open the PocketBase admin UI (default: http://127.0.0.1:8090/_/)
2. Go to the `focus_points` collection
3. Create a new focus point with:
   - `focuspoint`: The main topic or question you want to focus on
   - `explanation`: Additional context or explanation
   - `sites`: Select websites or data sources to mine
   - `activated`: Set to true to enable the focus point
   - `auto_shutdown`: Set to true to automatically shut down when completed
   - `concurrency`: Number of concurrent threads to use (default: 1)
   - `references`: JSON array of reference materials (optional)

### Adding References

References can be added to focus points to provide additional context. The references field should be a JSON array with objects like:

```json
[
  {
    "type": "url",
    "name": "Example Reference",
    "content": "https://example.com/reference"
  },
  {
    "type": "text",
    "name": "Text Reference",
    "content": "This is a text reference that provides context."
  }
]
```

### Monitoring Tasks

Tasks can be monitored in the PocketBase admin UI by checking the `tasks` collection.

## Plugin System

### Available Plugins

- **Connectors**:
  - `web_connector`: Collects data from web sources
  - `github_connector`: Collects data from GitHub repositories

- **Processors**:
  - `focus_point_processor`: Extracts information based on focus points using LLMs

### Creating Custom Plugins

You can create custom plugins by extending the base classes:

```python
from core.plugins.connectors import ConnectorBase, DataItem

class MyCustomConnector(ConnectorBase):
    name = "my_custom_connector"
    description = "My custom data connector"
    source_type = "custom"
    
    def initialize(self) -> bool:
        # Initialize the connector
        return True
    
    def collect(self, params: Optional[Dict[str, Any]] = None) -> List[DataItem]:
        # Collect data from the source
        # Return a list of DataItem objects
        return []
```

## Architecture

Wiseflow uses a modular architecture with the following components:

- **Core**: Main application logic and task management
- **Plugins**: Modular components for data collection and processing
- **Connectors**: Data source connectors (web, GitHub, etc.)
- **Processors**: Data processors (focus point extraction, etc.)
- **Task**: Task management and concurrency control

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.