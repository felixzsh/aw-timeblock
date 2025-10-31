import click
from pathlib import Path

from .config import config
from . import __version__

@click.group()
def cli():
    """aw-nextblock: Flexible time blocking for ActivityWatch"""
    pass

@cli.command()
@click.argument('plan_file', type=click.Path(exists=True, path_type=Path))
def start(plan_file: Path):
    """Start a new work session from a plan file"""
    pass

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
