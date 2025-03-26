#!/usr/bin/env python3
import subprocess
import sys


def open_terminal(command: str):
    """
    Opens a new terminal window or tab (depending on OS) to run `command`.
    """
    os_name = sys.platform
    print(f'RUNNING CMD: {command}')
    if os_name.startswith('win'):
        command = command.replace('/', '\\')
        # Windows
        # /k keeps the window open; /c closes on completion
        subprocess.Popen(f'start cmd /k "{command}"', shell=True)

    elif os_name.startswith('darwin'):
        # macOS (using AppleScript + Terminal)
        # If you prefer iTerm, you'd have to adjust the AppleScript accordingly.
        script = f'tell application "Terminal" to do script "{command}"'
        subprocess.run(['osascript', '-e', script])

    elif os_name.startswith('linux'):
        # Linux, example with GNOME Terminal
        # If you have Konsole, xfce4-terminal, or another terminal, adjust accordingly.
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'])

    else:
        print(f"Unsupported OS: {os_name} – cannot open new terminal.")
        # Fallback: just run in the current shell
        subprocess.Popen(command, shell=True)

def main():
    """
    Usage: python open_terminals.py <command1> <command2> ...

    Each command is opened in its own new terminal window/tab.
    """
    if len(sys.argv) < 2:
        print("Provide at least one command to run in a new terminal.\n"
              "Example: python make_sift.py \"python myscript.py\" \"./bin/some_app\"")
        sys.exit(1)

    # Each argument after the script name is treated as a separate command.
    commands = sys.argv[1:]

    for cmd in commands:
        open_terminal(cmd)

if __name__ == "__main__":
    main()
