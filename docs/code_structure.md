# Wiseflow Code Structure and Implementation Plan

This document outlines the current code structure of Wiseflow and provides guidance on where to implement the upcoming features described in the upgrade plan.

## Current Code Structure

```
wiseflow/
├── core/
│   ├── agents/                  # LLM agent implementations
│   │   ├── __init__.py
│   │   ├── action_dict_scraper.py
│   │   ├── get_info.py          # Main information extraction logic
│   │   ├── get_info_prompts.py  # Prompts for information extraction
│   │   └── insights.py
│   ├── crawl4ai/                # Web crawling functionality
│   │   ├── __init__.py
│   │   ├── async_configs.py
│   │   ├── async_crawler_strategy.py
│   │   ├── async_database.py
│   │   ├── async_logger.py
│   │   ├── async_webcrawler.py  # Main crawler implementation
│   │   └── ...
│   ├── llms/                    # LLM integration
│   │   ├── __init__.py
│   │   ├── litellm_wrapper.py   # LiteLLM integration
│   │   └── openai_wrapper.py
│   ├── scrapers/                # Custom scrapers for specific sites
│   │   ├── __init__.py
│   │   ├── mp_scraper.py
│   │   └── scraper_data.py
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── exa_search.py
│   │   ├── export_example.py
│   │   ├── export_infos.py
│   │   ├── general_utils.py
│   │   ├── pb_api.py            # PocketBase API integration
│   │   ├── pb_exporter.py
│   │   └── zhipu_search.py
│   ├── general_process.py       # Main processing logic
│   ├── run_task.py              # Task scheduling and execution
│   └── windows_run.py
├── dashboard/                   # Web dashboard (optional)
│   ├── __init__.py
│   ├── backend.py
│   ├── general_utils.py
│   ├── get_report.py
│   ├── get_search.py
│   ├── main.py
│   ├── mp_crawler.py
│   ├── simple_crawler.py
│   └── tranlsation_volcengine.py
├── pb/                          # PocketBase database
│   └── ...
├── test/                        # Test scripts
│   └── ...
└── weixin_mp/                   # WeChat integration
    └── __init__.py
```

## Implementation Plan for New Features

### Phase 1: Foundation

#### 1. Plugin System Implementation

**New Directories and Files:**
```
wiseflow/
├── core/
│   ├── plugins/                 # NEW: Plugin system
│   │   ├── __init__.py          # Plugin base classes and manager
│   │   ├── processors/          # Content processors
│   │   │   ├── __init__.py
│   │   │   ├── text/            # Text processors
│   │   │   │   └── __init__.py  # Focus point processor
│   │   │   └── ...
│   │   └── ...
│   ├── connectors/              # NEW: Data source connectors
│   │   ├── __init__.py          # Connector base classes
│   │   ├── web/                 # Web connector (enhanced)
│   │   │   └── __init__.py
│   │   ├── github/              # GitHub connector
│   │   │   └── __init__.py
│   │   └── ...
```

**Modifications to Existing Files:**
- `core/general_process.py`: Refactor to use the plugin system
- `core/run_task.py`: Enhance with concurrency support
- `core/llms/litellm_wrapper.py`: Add support for specialized prompting

#### 2. Concurrency Implementation

**New Files:**
```
wiseflow/
├── core/
│   ├── task/                    # NEW: Task management
│   │   ├── __init__.py
│   │   ├── manager.py           # Task manager with concurrency
│   │   ├── scheduler.py         # Enhanced scheduler
│   │   └── monitor.py           # Resource monitoring
```

**Modifications to Existing Files:**
- `core/run_task.py`: Replace frequency-based scheduling with concurrent task execution

#### 3. Reference Support

**New Files:**
```
wiseflow/
├── core/
│   ├── references/              # NEW: Reference management
│   │   ├── __init__.py
│   │   ├── manager.py           # Reference manager
│   │   ├── extractor.py         # Content extraction from references
│   │   └── indexer.py           # Reference indexing
```

**Database Schema Updates:**
- Add `references` table to PocketBase
- Add reference fields to `focus_points` table

### Phase 2: Expansion

#### 1. New Connectors

**New Directories and Files:**
```
wiseflow/
├── core/
│   ├── connectors/
│   │   ├── academic/            # NEW: Academic archives connector
│   │   │   └── __init__.py
│   │   ├── youtube/             # NEW: YouTube connector
│   │   │   └── __init__.py
│   │   └── code/                # NEW: Code search connector
│   │       └── __init__.py
```

#### 2. Cross-Source Analysis

**New Directories and Files:**
```
wiseflow/
├── core/
│   ├── analysis/                # NEW: Cross-source analysis
│   │   ├── __init__.py
│   │   ├── entity_linking.py    # Entity recognition and linking
│   │   ├── topic_modeling.py    # Topic modeling
│   │   └── trend_analysis.py    # Trend analysis
```

### Phase 3: Intelligence

**New Directories and Files:**
```
wiseflow/
├── core/
│   ├── knowledge/               # NEW: Knowledge graph
│   │   ├── __init__.py
│   │   ├── graph.py             # Knowledge graph implementation
│   │   ├── enrichment.py        # Automatic enrichment
│   │   └── visualization.py     # Graph visualization
│   ├── insights/                # NEW: Insight generation
│   │   ├── __init__.py
│   │   ├── pattern_recognition.py # Pattern recognition
│   │   ├── anomaly_detection.py # Anomaly detection
│   │   └── recommendations.py   # Recommendation system
```

### Phase 4: Refinement

**New Directories and Files:**
```
wiseflow/
├── core/
│   ├── api/                     # NEW: API for integration
│   │   ├── __init__.py
│   │   ├── routes.py            # API routes
│   │   └── webhooks.py          # Webhook support
│   ├── export/                  # NEW: Export capabilities
│   │   ├── __init__.py
│   │   ├── pdf.py               # PDF export
│   │   ├── csv.py               # CSV export
│   │   └── json.py              # JSON export
```

**Dashboard Enhancements:**
```
wiseflow/
├── dashboard/
│   ├── visualization/           # NEW: Enhanced visualization
│   │   ├── __init__.py
│   │   ├── knowledge_graph.py   # Knowledge graph visualization
│   │   ├── trends.py            # Trend visualization
│   │   └── entities.py          # Entity visualization
```

## Database Schema Updates

### Current Schema

```
PocketBase:
- focus_points: Focus points for information extraction
  - focuspoint: Focus point description
  - explanation: Detailed explanation
  - activated: Whether the focus point is active
  - per_hour: Crawl frequency in hours
  - search_engine: Whether to use search engine
  - sites: Related sites

- sites: Information sources
  - url: Source URL
  - type: Source type (web or rss)

- infos: Extracted information
  - url: Source URL
  - url_title: Source title
  - tag: Related focus point
  - content: Extracted content
  - references: References to sources
```

### Schema Updates

```
PocketBase:
- focus_points: (Updates)
  - ADD references: List of reference IDs
  - ADD concurrency: Number of concurrent tasks
  - ADD auto_shutdown: Whether to auto-shutdown when complete
  - REMOVE per_hour: (Replace with task-based execution)

- references: (New table)
  - id: Reference ID
  - focus_id: Related focus point
  - type: Reference type (file, website, document)
  - path: Path to reference
  - content: Extracted content from reference

- tasks: (New table)
  - id: Task ID
  - focus_id: Related focus point
  - status: Task status (pending, running, complete, failed)
  - start_time: Task start time
  - end_time: Task end time
  - resources: Resource usage statistics

- entities: (New table)
  - id: Entity ID
  - name: Entity name
  - type: Entity type
  - sources: Sources where the entity appears
  - relations: Relations to other entities

- insights: (New table)
  - id: Insight ID
  - focus_id: Related focus point
  - type: Insight type
  - content: Insight content
  - entities: Related entities
  - confidence: Confidence score
```

## Implementation Priorities

1. **First Priority: Plugin System and Connectors**
   - Implement the plugin system infrastructure
   - Create the base connector classes
   - Enhance the web connector
   - Implement the GitHub connector

2. **Second Priority: Concurrency and Task Management**
   - Implement the task manager
   - Add concurrency support to the scheduler
   - Implement resource monitoring

3. **Third Priority: Reference Support**
   - Implement the reference manager
   - Add reference support to focus points
   - Implement reference content extraction

4. **Fourth Priority: Cross-Source Analysis**
   - Implement entity recognition and linking
   - Add topic modeling
   - Implement trend analysis

## Conclusion

This implementation plan provides a roadmap for gradually enhancing the Wiseflow codebase to support the features described in the upgrade plan. By following this structure, we can ensure a smooth transition from the current architecture to the enhanced system while maintaining compatibility with existing functionality.
