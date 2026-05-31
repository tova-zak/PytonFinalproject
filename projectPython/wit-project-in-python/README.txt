# WIT Project - Basic Version Control System

## General Description
This project is a basic version control system (VCS) inspired by Git. It allows managing file versions through a command-line interface (CLI).

## Requirements
To run this project, you need to install the following library:
- click

You can install it using:
pip install -r requirements.txt

## How to Run
The system is operated via the `wit.py` file. Use the following commands:

1. Initialize a repository:
   python wit.py init

2. Add files to staging:
   python wit.py add <file_path>
   (Example: python wit.py add .)

3. Create a commit:
   python wit.py commit -m "your message"

4. Check status:
   python wit.py status

5. Checkout a commit:
   python wit.py checkout <commit_id>

## Project Structure
- wit.py: The CLI entry point.
- core.py: The core logic of the system.
- .wit/: Metadata and storage directory.
- .witignore: Configuration for ignored files.

## Example Usage Scenario
1. Run `python wit.py init` to start.
2. Create a file and run `python wit.py add .` to stage it.
3. Run `python wit.py commit -m "Initial version"` to save.
4. Use `python wit.py status` to see current changes.