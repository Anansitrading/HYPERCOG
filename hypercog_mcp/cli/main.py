#!/usr/bin/env python3
import click
import asyncio
import json
from pathlib import Path
from ..config import load_environment, setup_cognee
from ..orchestrator import HyperCogOrchestrator
from ..llm_client import LLMClient

@click.group()
def cli():
    """HyperCog MCP - Advanced context enrichment orchestration"""
    pass

@cli.command()
def status():
    """Check HyperCog system status"""
    click.echo("✓ HyperCog MCP installed")

if __name__ == "__main__":
    cli()
