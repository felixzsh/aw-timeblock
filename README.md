# aw-nextblock

**WIP** CLI tool and [ActivityWatch](https://activitywatch.net) watcher for timeblocking sessions

## Table of Contents

- [What is this](#what-is-this)
- [What it offers](#what-it-offers)
  - [Track Actual vs. Planned activity](#track-actual-vs-planned-activity)
  - [Interactive Session](#interactive-session)
  - [Session Review](#session-review)
- [Why it's useful](#why-its-useful)
- [Getting Started](#getting-started)
  - [Main Components](#main-components)
  - [Setup the watcher](#setup-the-watcher)
  - [Control commands](#control-commands)
  - [Triggering Next](#triggering-next)
  - [Setup Custom Visualization](#setup-custom-visualization)
  - [Usage](#usage)
- [Installation](#installation)
  - [Requirements](#requirements)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)
- [Related](#related)

---

## What is this

aw-nextblock reimagines [time blocking](https://en.wikipedia.org/wiki/Timeblocking) by prioritizing realistic flexibility over rigid scheduling by proposing interactive work sessions where your **only** responsibility is decide **when** to advance to the `next` task. this approach gives insightful planned vs real activity data thanks to the [ActivityWatch](https://activitywatch.net) ecosystem.

## What it offers

### Track Actual vs. Planned activity

aw-nextblock leverages automatic activity tracking (thanks [ActivityWatch](https://activitywatch.net) <3) and enrich that information with real work session timeblocks, where each one represents the time you actually spent (planned time is stored as metadata for custom visualization usage).

### Interactive Session

During a work session, the only input needed by you is [`next`](#triggering-next), what is this ? For now is just a CLI command, but this means you can trigger it any way you want, however, i recommend the keybinding approach.

Session feedback is delivered via system notifications at configurable intervals: before, at, and after the planned duration of timeblocks.

### Session Review

A Custom visualization shows your planned blocks alongside actual activity data in a clear parallel-bar chart. See exactly what happened during each block and use these insights to improve your workflow.

[image placeholder]


## Why it's useful

Traditional time blocking assumes perfect estimates and rigid adherence. Reality is messier, tasks take longer or shorter than expected, flow state matters, interruptions happen.

aw-nextblock provides structure without rigidity. Plans are guides, not rules. You stay aware of time without being controlled by it. The visual analysis of your sessions helps you understand your work patterns and continuously improve your workflow.

## Getting Started

### Main Components

- **`nextblock-ctl`**: Command-line tool for managing work sessions.
- **`aw-watcher-nextblock`**: Background watcher that monitors session state.


### Setup the watcher - **TBD**

### Control commands

Use `nextblock-ctl` for session management:

```bash
nextblock-ctl start <plan.yaml>    # Start a work session
nextblock-ctl next                 # Move to next block
nextblock-ctl status               # Check current status
nextblock-ctl stop                 # Stop current session
```

### Triggering Next

While you can run `nextblock-ctl next` from a terminal, the recommended approach is using a keybinding for instant access during your workflow.

Example Hyprland keybinding:
```
bind = $mainMod ALT, N, exec, nextblock-ctl next
```

### Setup Custom Visualization - **TBD**

### Usage

#### 1. Define Your Plan

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

#### 2. Start Your Session

```bash
nextblock-ctl start plan.yaml
```

This creates a session file that the watcher will monitor.

#### 3. Work and Advance

Focus on your current task. When ready to move forward:

```bash
nextblock-ctl next
```

See [Triggering Next](#triggering-next) for recommended setup.

#### 4. Review Your Session

After completing your work session, use the custom visualization in ActivityWatch's web UI to analyze your planned blocks against actual activity data.

## Installation

In active development. Installation instructions coming with first release.

### Requirements

- Python 3.13+
- ActivityWatch (installed and running)
- Linux/macOS/Windows

**Note:** Early development focuses on Linux. macOS and Windows support planned for first release.

## Project Status

### Milestone 1: core CLI
- [x] YAML plan parsing
- [x] Session state management
- [x] Basic CLI commands (`start`, `next`, `status`, `stop`) via `nextblock-ctl`

### Milestone 2: Watcher Implementation
- [ ] Config file/args loading
- [ ] Main monitor loop
- [ ] aw-client intgration

### Milestone 3: Notifications
- [ ] Define triggers
- [ ] implementation in watcher loop
- [ ] Configurable notification triggers

### Milestone 4: Custom Visualization
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