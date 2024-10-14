# emission/tests/funcTests/TestFunctionTiming.py

import logging
import time
import typing as t

# Import the store_dashboard_time and store_dashboard_error functions
import emission.storage.decorations.stats_queries as sdq

# Import the existing Timer context manager
import emission.core.timer as ec_timer

# Import the database module for verification
import emission.core.get_database as gdb

# Define test functions
def test_function_1():
    logging.info("Executing test_function_1")
    time.sleep(1)  # Simulate processing time
    return True  # Indicate successful execution

def test_function_2():
    logging.info("Executing test_function_2")
    time.sleep(2)
    return True

def test_function_faulty():
    logging.info("Executing test_function_faulty")
    time.sleep(1)
    raise ValueError("Simulated error in test_function_faulty")

def test_function_3():
    logging.info("Executing test_function_3")
    time.sleep(3)
    return True

def execute_and_time_function(func: t.Callable[[], bool]):
    """
    Executes a given function, measures its execution time using ECT_Timer,
    stores the timing information using store_dashboard_time, and verifies
    that the data was stored successfully by querying the timeseries database.
    If the function raises an exception, it stores the error using store_dashboard_error
    and verifies the error storage.

    Parameters:
    - func (Callable[[], bool]): The test function to execute and time.
    """
    function_name = func.__name__
    timestamp = time.time()

    logging.info(f"Starting timing for function: {function_name}")

    try:
        with ec_timer.Timer() as timer:
            result = func()  # Execute the test function

        elapsed_seconds = timer.elapsed  # Accessing the float attribute directly
        elapsed_ms = elapsed_seconds * 1000  # Convert to milliseconds

        # Store the execution time
        sdq.store_dashboard_time(
            code_fragment_name=function_name,
            ts=timestamp,
            reading=elapsed_ms
        )
        print(f"Function '{function_name}' executed successfully in {elapsed_ms:.2f} ms.")
        logging.info(f"Function '{function_name}' executed successfully in {elapsed_ms:.2f} ms.")

        # Verification: Adjusted Query to Match Document Structure
        timeseries_db = gdb.get_timeseries_db()
        

        query = {
            "metadata.key": "stats/dashboard_time",
            "data.name": function_name,
            "data.ts": {"$gte": timestamp, "$lte": timestamp},
            "data.reading": {"$gte": elapsed_ms, "$lte": elapsed_ms} 
        }
        
        # Retrieve the most recent document for the function
        stored_document = timeseries_db.find_one(
            query,
            sort=[("data.ts", -1)]
        )

        if stored_document:
            # Inspect the stored document
            stored_ts = stored_document.get("data", {}).get("ts", 0)
            stored_reading = stored_document.get("data", {}).get("reading", 0)
            logging.debug(f"Stored Document for '{function_name}': ts={stored_ts}, reading={stored_reading}")

            # Check if the reading is within a reasonable tolerance (e.g., ±100 ms)
            if abs(stored_reading - elapsed_ms) <= 100:
                print(f"Verification passed: Data for '{function_name}' is stored correctly.")
                logging.info(f"Verification passed: Data for '{function_name}' is stored correctly.")
            else:
                print(f"Verification failed: 'reading' value for '{function_name}' is outside the expected range.")
                logging.error(f"Verification failed: 'reading' value for '{function_name}' is outside the expected range.")
        else:
            print(f"Verification failed: Data for '{function_name}' was not found in the database.")
            logging.error(f"Verification failed: Data for '{function_name}' was not found in the database.")

    except Exception as e:
        # Even if the function fails, capture the elapsed time up to the exception
        elapsed_seconds = timer.elapsed if 'timer' in locals() else 0  # Accessing the float attribute directly
        elapsed_ms = elapsed_seconds * 1000

        # Store the error timing
        sdq.store_dashboard_error(
            code_fragment_name=function_name,
            ts=timestamp,
            reading=elapsed_ms
        )
        print(f"Function '{function_name}' failed after {elapsed_ms:.2f} ms with error: {e}")
        logging.error(f"Function '{function_name}' failed after {elapsed_ms:.2f} ms with error: {e}")

        # Verification: Adjusted Error Query to Match Document Structure
        timeseries_db = gdb.get_timeseries_db()

        error_query = {
            "metadata.key": "stats/dashboard_error",
            "data.name": function_name,
            "data.ts": {"$gte": timestamp, "$lte": timestamp},
            "data.reading": {"$gte": elapsed_ms, "$lte": elapsed_ms}
        }
        stored_error = timeseries_db.find_one(
            error_query,
            sort=[("data.ts", -1)]
        )

        if stored_error:
            stored_ts = stored_error.get("data", {}).get("ts", 0)
            stored_reading = stored_error.get("data", {}).get("reading", 0)
            logging.debug(f"Stored Error Document for '{function_name}': ts={stored_ts}, reading={stored_reading}")

            if abs(stored_reading - elapsed_ms) <= 100:
                print(f"Error verification passed: Error for '{function_name}' is stored correctly.")
                logging.info(f"Error verification passed: Error for '{function_name}' is stored correctly.")
            else:
                print(f"Error verification failed: 'reading' value for '{function_name}' error is outside the expected range.")
                logging.error(f"Error verification failed: 'reading' value for '{function_name}' error is outside the expected range.")
        else:
            print(f"Error verification failed: Error for '{function_name}' was not found in the database.")
            logging.error(f"Error verification failed: Error for '{function_name}' was not found in the database.")

def main():
    # Define the list of test functions, including the faulty one
    function_list: t.List[t.Callable[[], bool]] = [
        test_function_1,
        test_function_2,
        # test_function_faulty,  # This will raise an exception
        test_function_3  # This should execute normally after the faulty function
    ]
    # Execute and time each function
    for func in function_list:
        execute_and_time_function(func)

if __name__ == "__main__":
    main()
