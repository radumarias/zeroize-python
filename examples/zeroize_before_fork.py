""" In the case of [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write) you need to zeroize the memory before forking the child process. """

import os
from zeroize import zeroize1, mlock, munlock


if __name__ == "__main__":
    try:
        # Maximum you can mlock is 2662 KB
        sensitive_data = bytearray(b"Sensitive Information")
        mlock(sensitive_data)

        print("Before zeroization:", sensitive_data)

        zeroize1(sensitive_data)
        print("After zeroization:", sensitive_data)

        # Forking after zeroization to ensure no sensitive data is copied
        pid = os.fork()
        if pid == 0:
            # This is the child process
            print("Child process memory after fork:", sensitive_data)
        else:
            # This is the parent process
            os.wait()  # Wait for the child process to exit
        
        print("all good, bye!")

    finally:
        # Unlock the memory
        print("unlocking memory")
        munlock(sensitive_data)
