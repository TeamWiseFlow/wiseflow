#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI tool for running data mining analysis on demand.
"""
import os
import sys
import asyncio
import argparse
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from utils.general_utils import get_logger
from utils.pb_api import PbTalker
from analysis.data_mining import get_analysis_for_focus, analyze_info_items
from agents.insights import generate_insights_for_focus

project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)
cli_logger = get_logger('data_mining_cli', project_dir)
pb = PbTalker(cli_logger)

async def run_analysis(focus_id: str, force: bool = False):
    """
    Run data mining analysis for a specific focus point.
    
    Args:
        focus_id: ID of the focus point
        force: Force regeneration of analysis even if recent analysis exists
    """
    cli_logger.info(f"Running data mining analysis for focus ID: {focus_id}")
    
    # Get the focus point
    focus = pb.read_one(collection_name='focus_point', id=focus_id)
    if not focus:
        cli_logger.error(f"Focus point with ID {focus_id} not found")
        return
    
    cli_logger.info(f"Focus point: {focus.get('focuspoint', '')}")
    
    # Get information items for this focus point
    info_items = pb.read(collection_name='infos', filter=f"tag='{focus_id}'")
    
    if not info_items:
        cli_logger.warning(f"No information items found for focus ID {focus_id}")
        return
    
    cli_logger.info(f"Found {len(info_items)} information items")
    
    # Run analysis
    if force:
        cli_logger.info("Forcing regeneration of analysis")
        analysis = await analyze_info_items(info_items, focus_id)
    else:
        analysis = await get_analysis_for_focus(focus_id, max_age_hours=0)
    
    # Generate insights
    cli_logger.info("Generating insights")
    insights = await generate_insights_for_focus(focus_id, force=force)
    
    cli_logger.info(f"Analysis and insights generation completed for focus ID: {focus_id}")
    
    # Print summary
    print("\n" + "="*80)
    print(f"ANALYSIS SUMMARY FOR: {focus.get('focuspoint', '')}")
    print("="*80)
    print(f"Entities extracted: {len(analysis.get('entities', []))}")
    print(f"Topics identified: {len(analysis.get('topics', []))}")
    print(f"Relationships found: {len(analysis.get('relationships', []))}")
    print(f"Knowledge graph: {analysis.get('knowledge_graph_path', 'Not generated')}")
    print("\nINSIGHTS SUMMARY:")
    print("-"*80)
    print(insights.get('insight_summary', 'No insights generated'))
    print("="*80)

async def list_focus_points():
    """List all focus points with their IDs."""
    cli_logger.info("Listing all focus points")
    
    focus_points = pb.read(collection_name='focus_point')
    
    if not focus_points:
        print("No focus points found")
        return
    
    print("\n" + "="*80)
    print("FOCUS POINTS")
    print("="*80)
    for focus in focus_points:
        status = "ACTIVE" if focus.get('activated', False) else "INACTIVE"
        print(f"ID: {focus['id']}")
        print(f"Name: {focus.get('focuspoint', 'Unnamed')}")
        print(f"Status: {status}")
        print(f"Sites: {len(focus.get('sites', []))}")
        print("-"*80)

def main():
    parser = argparse.ArgumentParser(description="Data Mining CLI for WiseFlow")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List focus points command
    list_parser = subparsers.add_parser("list", help="List all focus points")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run data mining analysis for a focus point")
    analyze_parser.add_argument("focus_id", help="ID of the focus point to analyze")
    analyze_parser.add_argument("--force", action="store_true", help="Force regeneration of analysis")
    
    args = parser.parse_args()
    
    if args.command == "list":
        asyncio.run(list_focus_points())
    elif args.command == "analyze":
        asyncio.run(run_analysis(args.focus_id, args.force))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()