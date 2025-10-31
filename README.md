# aw-nextblock

**WIP** service for ActivityWatch

## What is this?

aw-nextblock reimagines [time blocking](https://en.wikipedia.org/wiki/Timeblocking) by reducing your responsibility to a single action: deciding when to move to the next task.

Traditional time blocking tools force you to manage timers, pause/resume tracking, and fight against rigid schedules. aw-nextblock takes a different approach: you create a plan with reasonable time estimates, start your session, and simply use [`next`](#triggering-next) when you're ready to move forward. The system handles time-aware notifications relative to your planned durations, keeping you conscious of time without being intrusive.

## Requirements

- Python 3.13+
- ActivityWatch (installed and running)
- Linux/macOS/Windows

**Note:** Early development focuses on Linux. macOS and Windows support planned for first release.

## Installation

In active development. Installation instructions coming with first release.

## Core Philosophy

**Your only responsibility: decide when to advance.**

You handle:
- Creating work plans
- Doing the work
- Using [`next`](#triggering-next) to advance

## How aw-nextblock works with ActivityWatch

ActivityWatch excels at tracking *what you're actually doing*. aw-nextblock complements this by telling ActivityWatch *what you intended to do*.

This service sends structured timeblock events to ActivityWatch, enriching your activity data with your intentional planning context.

## How it Works

### 1. Define Your Plan

Create a YAML file with your work session:

```yaml
session_name: "Morning Deep Work"

blocks:
  - name: "Architecture Design"
    duration: 45
    
  - name: "Core Implementation"
    duration: 90
    
  - name: "Testing"
    duration: 30
```

Durations are estimates, not limits.

### 2. Start Your Session

```bash
aw-nextblock start plan.yaml
```

This initiates a monitoring process that tracks elapsed time to send notifications at key moments relative to your planned durations.

### 3. Work and Advance

Focus on your current task. When ready to move forward:

```bash
aw-nextblock next
```

See [Triggering Next](#triggering-next) for recommended setup.


### 4. Analyze with Custom Visualization

**TBD** - A custom visualization for ActivityWatch's web UI will display your planned blocks contrasted with actual activity data.

## Notifications

**TBD** - The notification system will keep you aware of time relative to your planned durations without being intrusive. Notifications will be configurable and triggered at key moments during each block.

## Commands

```bash
aw-nextblock start <plan.yaml>    # Start a work session
aw-nextblock next                 # Move to next block
aw-nextblock status               # Check current status
aw-nextblock stop                 # Stop current session
```

## Triggering Next

While you can run `aw-nextblock next` from a terminal, the recommended approach is using a keybinding for instant access during your workflow.

Example Hyprland keybinding:
```
bind = $mainMod ALT, N, exec, aw-nextblock next
```

## Why This Approach?

Traditional time blocking assumes perfect estimates and rigid adherence. Reality is messier: tasks take longer or shorter than expected, flow state matters, interruptions happen.

aw-nextblock provides structure without rigidity. Plans are guides, not rules. You stay aware of time without being controlled by it.

## Project Status

### Milestone 1: Core Functionality
- [x] YAML plan parsing
- [ ] Configuration file loading
- [ ] Session state management
- [ ] Basic CLI commands (`start`, `next`, `status`, `stop`)
- [ ] ActivityWatch client integration

### Milestone 2: Time Awareness
- [ ] Background time monitoring
- [ ] Notification system implementation
- [ ] Configurable notification triggers

### Milestone 3: Polish & Visualization
- [ ] Define visualization approach for contrasting data
- [ ] Implement custom ActivityWatch visualization

### Milestone 4: Distribution
- [ ] Package for PyPI
- [ ] Installation instructions
- [ ] Setup automation
- [ ] Cross-platform testing

## Contributing

Contributions welcome. Open an issue to discuss changes before submitting PRs.

## License

MIT License

## Related

- [ActivityWatch](https://activitywatch.net/) - Automatic time tracking
- [ActivityWatch Watchers](https://github.com/ActivityWatch?q=aw-watcher) - Activity tracking extensions
