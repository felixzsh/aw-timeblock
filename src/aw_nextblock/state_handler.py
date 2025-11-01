from shared import SessionState, SessionStatus, TimeBlock
from .plans import SessionPlan
from datetime import datetime



def session_state_from_plan(plan: SessionPlan) -> SessionState:
    """Create a new session state from a plan."""
    return SessionState(
        name=plan.name,
        blocks=plan.blocks,
        current_block_idx=0,
        status=SessionStatus.ACTIVE,
        start_dt=datetime.now()
    )


def advance_session_state(session_state: SessionState) -> SessionState:
    """Advance the session state to the next block."""
    # Mark current block as completed
    if session_state.current_block:
        session_state.blocks[session_state.current_block_idx].end_dt = datetime.now()
    
    # Move to next block
    next_block_idx = session_state.current_block_idx + 1
    
    if next_block_idx < len(session_state.blocks):
        # Start next block
        session_state.current_block_idx = next_block_idx
        session_state.blocks[next_block_idx].start_dt = datetime.now()
    else:
        # No more blocks, end session
        session_state.status = SessionStatus.INACTIVE
        session_state.end_dt = datetime.now()
    
    return session_state

