
import os
import time

FAIL_MODE = os.getenv("FAIL_MODE", "none")
_server_error_triggered = False


def before_submit() -> None:
    """Simulate a controlled failure before an invoice is inserted."""
    global _server_error_triggered

    if FAIL_MODE == "server_error_once" and not _server_error_triggered:
        _server_error_triggered = True
        raise RuntimeError("SIMULATED_SERVER_ERROR_ONCE")

    if FAIL_MODE == "slow":
        time.sleep(3)


def submit_button_text() -> str:
    """Return the button label used by the HTML form."""
    if FAIL_MODE == "rename_submit":
        return "Submit entry now"

    return "Submit entry"
