import click
from pathlib import Path
import signal
import sys

from .config import config
from . import __version__
from .main_loop import MainLoop

@click.group()
def cli():
    """aw-nextblock: Flexible time blocking for ActivityWatch"""
    pass

@cli.command()
@click.argument('plan_file', type=click.Path(exists=True, path_type=Path))
def start(plan_file: Path):
    """Start a new work session from a plan file"""
    # TODO: Load and validate the plan file
    
    # Create and run the main loop
    main_loop = MainLoop()
    
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
    pass

@cli.command()
def status():
    """Show current session status"""
    pass

@cli.command()
def stop():
    """Stop the current session"""
    pass

@cli.command()
def version():
    """Show version information"""
    click.echo(f"aw-nextblock v{__version__}")