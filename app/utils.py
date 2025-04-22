import psutil
import requests
import time

def block_until_server_is_alive(
    url: str | bytes,
    timeout: float,
    requests_interval=0.1
):
    """
    Sends GET requests synchronously to the given URL until it responds or the timeout is reached.

    This is useful to wait for a server to be ready before continuing with the execution.

    Args:
        url: The URL to check.
        timeout: Timeout in seconds.
        requests_interval: Interval between requests in seconds.

    Returns:
        bool: True if the server is reachable, False if the timeout has reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(url)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(requests_interval)
    else:
        return False
    return True

def terminate_process_and_children(
    pid: int,
    children_timeout=5.0,
    process_timeout=5
):
    """
    Terminates (SIGTERM) any process's children then itself.

    When timeouts are reached, the processes are killed (SIGKILL).

    As there are two timeouts, the max. time to wait is the sum of the two.

    Args:
        pid: The PID of the process to terminate.
        children_timeout: Timeout in seconds for all children to terminate before being all killed.
        process_timeout: Timeout in seconds for the process to terminate before being killed.

    Returns:
        bool: True if any process was killed, False if it was already dead.
    """
    has_killed = False

    parent = psutil.Process(pid)
    if not parent.is_running():
        return has_killed  # False

    children = parent.children(recursive=True)
    for process in children :
        process.terminate()
    _, alive_children = psutil.wait_procs(children, children_timeout)
    for process in alive_children:
        process.kill()
        has_killed = True

    parent.terminate()
    try:
        parent.wait(process_timeout)
    except psutil.TimeoutExpired:
        parent.kill()
        has_killed = True

    return has_killed
