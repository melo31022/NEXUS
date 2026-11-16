"""Small local safety checks for actions that may affect the Windows system."""
import re

RISKY_COMMAND_PATTERNS = (
    r"\b(remove-item|remove-content|clear-content|set-content|out-file|move-item|rename-item|copy-item|del|erase|rmdir|rd|rm|format|clear-disk|initialize-disk)\b",
    r"\b(shutdown|restart-computer|stop-computer|stop-process)\b",
    r"\b(reg\s+(delete|add)|remove-itemproperty|set-itemproperty|new-itemproperty|set-executionpolicy|start-process)\b",
    r"\b(diskpart|bcdedit|bootrec|takeown|icacls)\b",
    r"\b(invoke-expression|iex)\b|\b(downloadstring|downloadfile)\b",
    r"\b(invoke-webrequest|start-bitstransfer)\b",
)


def command_needs_confirmation(command: str) -> bool:
    """Return True for common destructive/system-changing PowerShell commands."""
    return any(re.search(pattern, command, flags=re.IGNORECASE) for pattern in RISKY_COMMAND_PATTERNS)
