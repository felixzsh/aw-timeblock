"""Command-line interface for aw-nextblock."""
import logging
import signal
import sys
from pathlib import Path

import click

from .config import config
from .core.plans import load_session_plan
from . import __version__
from .main_loop import MainLoop


logger = logging.getLogger(__name__)


@click.group()
def cli():
    """aw-nextblock: Flexible time blocking for ActivityWatch"""
    pass


@cli.command()
@click.argument('plan_file', type=click.Path(exists=True, path_type=Path))
def start(plan_file: Path):
    """Start a new work session from a plan file"""
    click.echo(f"Loading session plan from {plan_file}")
    
    # Load and validate the plan file
    session_plan = load_session_plan(str(plan_file))
    if not session_plan:
        click.echo("Failed to load session plan", err=True)
        sys.exit(1)
    
    click.echo(f"Loaded session: {session_plan.name}")
    click.echo(f"Found {len(session_plan.blocks)} time blocks")
    
    # Create and run the main loop
    main_loop = MainLoop(session_plan)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        click.echo("\nStopping session...")
        main_loop.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    click.echo(f"Starting session from {plan_file}")
    click.echo("Press Ctrl+C to stop the session")
    
    try:
        main_loop.run()
    except KeyboardInterrupt:
        click.echo("\nSession stopped")


@cli.command()
async def next():
    """Advance to the next time block"""
    click.echo("Advancing to next time block...")
    # TODO: Implement next functionality


@cli.command()
def status():
    """Show current session status"""
    click.echo("Session status: Not implemented yet")


@cli.command()
def stop():
    """Stop the current session"""
    click.echo("Stopping session...")
    # TODO: Implement stop functionality


@cli.command()
def version():
    """Show version information"""
    click.echo(f"aw-nextblock v{__version__}")
