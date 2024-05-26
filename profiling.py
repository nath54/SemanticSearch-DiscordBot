import time


class Profile():
    # Start of the monitored code
    def __init__(self, code_line: str):
        # Line of code to display
        self.code_line: str = code_line
        # Time of the start of the code execution, in seconds
        self.start_time: float = time.time()
        # For intermediar monitor
        self.last_intermediate_time: float = time.time()
    
    # Intermediate update monitor, for buffered operations for instance
    def intermediate_update(self, extra_args: list[str] = []):
        # Time the code execution took, in seconds
        time_taken: float = time.time() - self.last_intermediate_time
        # Update last intermediate time
        self.last_intermediate_time = time.time()
        # Display Primary info
        print( "\n\x1b[1;33mIntermediate Profiling:\n"
              f"   \x1b[1;33m- Code line: \x1b[m{self.code_line}\n"
              f"   \x1b[1;33m- Time taken: \x1b[m{time_taken} sec\n")
        # Display extra args
        for ex in extra_args:
            print(f"   - {ex}\n")
    
    # End of the monitored code
    def finished(self, extra_args: list[str]= []):
        # Time the code execution took, in seconds
        time_taken: float = time.time() - self.start_time
        # Display Primary info
        print( "\n\x1b[1;33mProfiling:\n"
              f"   \x1b[1;33m- Code line: \x1b[m{self.code_line}\n"
              f"   \x1b[1;33m- Time taken: \x1b[m{time_taken} sec\n")
        # Display extra args
        for ex in extra_args:
            print(f"   \x1b[1;33m-\x1b[m {ex}\n")
