"""Command-line interface for aw-nextblock."""
import logging
import sys
from pathlib import Path
from datetime import datetime
import click
import asyncio
from desktop_notifier import DesktopNotifier
from .session import Session, session_exists, save_session, load_session, delete_session
from . import __version__

logger = logging.getLogger(__name__)

@click.group(
    context_settings={'help_option_names': ['-h', '--help']},
    invoke_without_command=True
)
@click.pass_context
@click.option('--testing', is_flag=True, help='Enable testing mode for the watcher')
@click.option('--verbose', is_flag=True, help='Enable verbose logging for the watcher')
def cli(ctx, testing, verbose):
    """aw-nextblock: Flexible time blocking for ActivityWatch
    
    Run without commands to start the watcher process.
    Use commands for session management.
    """
    ctx.obj = {
        'testing': testing,
        'verbose': verbose
    }
    
    if ctx.invoked_subcommand is None:
        from .watcher import watcher_async
        asyncio.run(watcher_async(testing=testing, verbose=verbose))

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
    if session.current_block:
        session.current_block.start_dt = datetime.now()

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
        if session.current_block:
            session.current_block.start_dt = datetime.now()
            if save_session(session):
                click.echo(f"Moved to next block: {session.current_block.name}")

                notifier = DesktopNotifier(
                    app_name="aw-nextblock",
                    app_icon=None
                )
                asyncio.run(notifier.send(
                    title=f"{session.name}",
                    message=f"{session.current_block.name} just started!",
                    icon=None
                ))
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
