import concurrent.futures
import time

def run_with_timeout(func, args=(), kwargs={}, timeout_seconds=4.0):
    """
    Executes a function with a strict timeout. 
    Crucial for live hackathon demos to prevent UI freezing.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            # Wait for the result until the timeout is reached
            result = future.result(timeout=timeout_seconds)
            return result
        except concurrent.futures.TimeoutError:
            print(f"[WARNING] Operation timed out after {timeout_seconds}s!")
            return None
        except Exception as e:
            print(f"[ERROR] API Call Failed: {e}")
            return None