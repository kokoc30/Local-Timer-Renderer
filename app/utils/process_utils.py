import subprocess
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

def run_command(args: List[str], timeout: int = 5) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Runs a subprocess command safely with a timeout and error capture.
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (Success, stdout, stderr/error_msg)
    """
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False
        )
        if result.returncode == 0:
            return True, result.stdout, None
        else:
            return False, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, None, f"Command timed out after {timeout} seconds."
    except FileNotFoundError:
        return False, None, f"Executable not found: {args[0]}"
    except Exception as e:
        logger.error(f"Error running command {args}: {e}")
        return False, None, str(e)
