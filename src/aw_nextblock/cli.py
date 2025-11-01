"""Command-line interface for aw-nextblock."""
import logging
import sys
from pathlib import Path
import click

from .session import Session, session_exists, save_session, load_session, delete_session
from . import __version__

logger = logging.getLogger(__name__)

@click.group()
def cli():
    """aw-nextblock: Flexible time blocking for ActivityWatch"""
    pass

@click.command()
@click.argument('plan_file', type=click.Path(exists=True, path_type=Path))
def start(plan_file: Path):
    """Start a new work session from a plan file"""
    click.echo(f"Loading session plan from {plan_file}")

    if session_exists():
        click.echo("A session is already running. Use 'next' to advance or 'stop' to end the active session.", err=True)
        sys.exit(1)

    session = Session.from_plan(str(plan_file))
    if not session:
        click.echo("Failed to load session plan", err=True)
        sys.exit(1)

    click.echo(f"Loaded session: {session.name}")
    click.echo(f"Found {len(session.blocks)} time blocks")


    if save_session(session):
        click.echo(f"Session '{session.name}' started successfully!")
        if session.current_block:
            click.echo(f"Current block: {session.current_block.name if session.current_block else 'None'}")
    else:
        click.echo("Failed to save session state", err=True)
        sys.exit(1)


@click.command()
def next():
    """Advance to the next time block"""
    click.echo("Advancing to next time block...")

    session = load_session()

    if not session:
        click.echo("No active session found. Start a session first with 'start <plan_file>'", err=True)
        sys.exit(1)

    next_block_idx = session.current_block_idx + 1
    if next_block_idx < len(session.blocks):
        session.current_block_idx = next_block_idx
        if session.current_block and save_session(session):
            click.echo(f"Moved to next block: {session.current_block.name}")
        else:
            click.echo("Failed to save session state", err=True)
            sys.exit(1)
    else:
        delete_session()
        click.echo("All blocks completed. Session ended.")

@click.command()
def status():
    """Show current session status"""
    session = load_session()
    if not session:
        click.echo("No active session")
        return

    click.echo(f"Session: {session.name}")
    click.echo(f"Current block: {session.current_block_idx + 1}/{len(session.blocks)}")

    if session.current_block:
        click.echo(f"Block: {session.current_block.name}")
        click.echo(f"Planned duration: {session.current_block.planned_duration} minutes")

    if session.start_dt:
        elapsed_minutes = int(session.elapsed_time / 60)
        click.echo(f"Elapsed time: {elapsed_minutes} minutes")

@click.command()
def stop():
    """Stops session if exists"""
    if delete_session():
        click.echo("session no longer active, start a new one")
    else:
        click.echo("No active session found", err=True)
        sys.exit(1)

@click.command()
def version():
    """Show version information"""
    click.echo(f"aw-nextblock v{__version__}")

cli.add_command(start)
cli.add_command(next)
cli.add_command(status)
cli.add_command(stop)
cli.add_command(version)