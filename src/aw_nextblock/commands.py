"""Command-line interface for aw-nextblock."""
import logging
import sys
from pathlib import Path

import click

from shared import load_session_state, save_session_state
from .state_handler import session_state_from_plan, advance_session_state
from .plans import load_session_plan
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

    # Check if a session already exists
    if load_session_state():
        click.echo("A session is already running. Use 'next' to advance or delete the session state file manually.", err=True)
        sys.exit(1)

    # Load and validate the plan file
    session_plan = load_session_plan(str(plan_file))
    if not session_plan:
        click.echo("Failed to load session plan", err=True)
        sys.exit(1)

    click.echo(f"Loaded session: {session_plan.name}")
    click.echo(f"Found {len(session_plan.blocks)} time blocks")

    session_state = session_state_from_plan(session_plan)

    if save_session_state(session_state):
        click.echo(f"Session '{session_state.name}' started successfully!")
        click.echo(f"Current block: {session_state.current_block.name if session_state.current_block else 'None'}")
    else:
        click.echo("Failed to save session state", err=True)
        sys.exit(1)


@click.command()
def next():
    """Advance to the next time block"""
    click.echo("Advancing to next time block...")

    session_state = load_session_state()
    if not session_state or not session_state.is_active:
        click.echo("No active session found. Start a session first with 'start <plan_file>'", err=True)
        sys.exit(1)

    # Advance to next block
    updated_state = advance_session_state(session_state)

    if save_session_state(updated_state):
        if updated_state.is_active and updated_state.current_block:
            click.echo(f"Moved to next block: {updated_state.current_block.name}")
        elif not updated_state.is_active:
            click.echo("All blocks completed. Session ended.")
        else:
            click.echo("Failed to advance to next block")
    else:
        click.echo("Failed to save session state", err=True)
        sys.exit(1)


@click.command()
def status():
    """Show current session status"""
    session_state = load_session_state()
    if not session_state:
        click.echo("No active session")
        return

    click.echo(f"Session: {session_state.name}")
    click.echo(f"Status: {session_state.status.value}")
    click.echo(f"Current block: {session_state.current_block_idx + 1}/{len(session_state.blocks)}")

    if session_state.current_block:
        click.echo(f"Block: {session_state.current_block.name}")
        click.echo(f"Planned duration: {session_state.current_block.planned_duration} minutes")

    if session_state.start_dt:
        elapsed_minutes = int(session_state.elapsed_time / 60)
        click.echo(f"Elapsed time: {elapsed_minutes} minutes")


@click.command()
def version():
    """Show version information"""
    click.echo(f"aw-nextblock v{__version__}")


cli.add_command(start)
cli.add_command(next)
cli.add_command(status)
cli.add_command(version)
