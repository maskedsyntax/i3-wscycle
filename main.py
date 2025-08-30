#!/usr/bin/env python3
import sys
import i3ipc

# Parse workspace number (handles "3:web" → 3)
def parse_name(name: str) -> int:
    try:
        return int(name.split(":", 1)[0])
    except ValueError:
        return 9999  # fallback for non-numeric names


# Get current (focused) workspace and all workspaces
def get_current_workspace(i3):
    workspaces = i3.get_workspaces()
    current = next((ws for ws in workspaces if ws.focused), None)
    if current is None:
        print("No focused workspace found", file=sys.stderr)
        sys.exit(1)
    return current, workspaces


# Cycle workspace on the same output
def cycle_workspace(i3, direction: int):
    current, workspaces = get_current_workspace(i3)

    # filter same output
    same_output = [ws for ws in workspaces if ws.output == current.output]

    # sort numerically by workspace number
    same_output.sort(key=lambda ws: parse_name(ws.name))

    # find index of current
    idx = next((i for i, ws in enumerate(same_output) if ws.name == current.name), 0)

    # wrap around
    new_idx = (idx + direction) % len(same_output)
    next_ws = same_output[new_idx]

    i3.command(f"workspace {next_ws.name}")


# Toggle output between eDP-1 and HDMI-1-0
def toggle_output(i3):
    current, _ = get_current_workspace(i3)

    target = "HDMI-1-0" if current.output != "HDMI-1-0" else "eDP-1"

    i3.command(f"move workspace to output {target}")
    i3.command(f"workspace {current.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: i3-wscycle.py [toggle|next|prev]")
        sys.exit(1)

    i3 = i3ipc.Connection()
    cmd = sys.argv[1]

    if cmd == "toggle":
        toggle_output(i3)
    elif cmd == "next":
        cycle_workspace(i3, +1)
    elif cmd == "prev":
        cycle_workspace(i3, -1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
