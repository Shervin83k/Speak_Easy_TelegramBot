import subprocess
import shutil
import sys
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


def colored(text: str, color: str) -> str:
    """Wrap text with color codes."""
    return f"{color}{text}{Style.RESET_ALL}"


def main():
    # Find pytest executable
    pytest_cmd = shutil.which("pytest")
    if pytest_cmd is None:
        print(colored("Install pytest: pip install pytest pytest-asyncio", Fore.RED))
        sys.exit(1)

    # Prepare command
    cmd = [pytest_cmd, "-q", "--disable-warnings", "--maxfail=1", "--showlocals"]
    print(colored("Running tests with command:", Fore.CYAN))
    print(" ".join(cmd) + "\n")

    # Run tests
    proc = subprocess.run(cmd, capture_output=True, text=True)

    # Print stdout with colored hints
    for line in proc.stdout.splitlines():
        line_lower = line.lower()
        if "passed" in line_lower:
            print(colored(line, Fore.GREEN))
        elif "failed" in line_lower or "error" in line_lower:
            print(colored(line, Fore.RED))
        elif "skipped" in line_lower or "warning" in line_lower:
            print(colored(line, Fore.YELLOW))
        else:
            print(line)

    # Print stderr if exists
    if proc.stderr:
        print(colored("\n=== STDERR ===\n", Fore.RED + Style.BRIGHT))
        print(proc.stderr)

    # Show summary
    summary = None
    for line in reversed(proc.stdout.splitlines()):
        if any(keyword in line.lower() for keyword in ["passed", "failed", "error", "skipped", "warning"]):
            summary = line
            break

    print("\n" + "=" * 50)
    print(colored("TEST SUMMARY", Fore.MAGENTA + Style.BRIGHT))
    print("=" * 50)
    if summary:
        line_lower = summary.lower()
        if "failed" in line_lower or "error" in line_lower:
            print(colored(summary, Fore.RED + Style.BRIGHT))
        elif "skipped" in line_lower or "warning" in line_lower:
            print(colored(summary, Fore.YELLOW + Style.BRIGHT))
        else:
            print(colored(summary, Fore.GREEN + Style.BRIGHT))
    else:
        print(colored("No summary found; see output above.", Fore.YELLOW))

    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
