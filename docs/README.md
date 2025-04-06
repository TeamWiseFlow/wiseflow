# Wiseflow Documentation

This directory contains documentation for the Wiseflow project, including upgrade plans, architecture diagrams, and implementation guides.

## Contents

- [Upgrade Plan](upgrade_plan.md): Comprehensive plan for transforming Wiseflow into an intelligent continuous data mining system
- [Code Structure](code_structure.md): Current code structure and implementation plan for new features

## Project Overview

Wiseflow is an AI-powered information extraction tool that uses LLMs to mine relevant information from web sources based on user-defined focus points. It employs a "wide search" approach for broad information collection rather than "deep search" for specific questions.

The upgrade plan outlines how to transform Wiseflow into a comprehensive data mining system capable of collecting, analyzing, and generating insights from diverse sources including web, academic archives, YouTube, GitHub, and code repositories.

## Implementation Approach

The implementation will focus on gradually enhancing the existing codebase rather than creating a new project. Key enhancements include:

1. Adding a plugin system for modular data source connectors
2. Implementing multi-threading and concurrency for improved performance
3. Adding reference file support for focus points
4. Developing cross-source analysis capabilities
5. Implementing auto-shutdown for completed mining tasks

See the [Code Structure](code_structure.md) document for detailed implementation plans.
