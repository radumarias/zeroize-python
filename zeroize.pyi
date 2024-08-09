from typing import Union
import numpy as np

def mlock(arr: Union[bytearray, np.ndarray]) -> None:
    """
    Locks and prevents data from being swapped to disk.
    Can lock a maximum of 2662 KB at a time.

    Args
        arr (bytearray | numpy array): A mutable byte array.

    Returns
        None

    Raises
        Err if arr is not of type bytearray or numpy array.

    Example
    ```python
    import numpy as np
    from zeroize import mlock, munlock

    data = np.array([1, 2, 3], dtype=np.uint8) # Create numpy ubyte array
    try:
        mlock(data)
        # Do some operations with the array
    finally:
        munlock(arr)
        print("Memory unlocked successfully")
    ```
    """

def munlock(arr: Union[bytearray, np.ndarray]) -> None:
    """
    Unlocks a mutable array in memory.
    Used to unlock the memory when the sensitive data is no longer needed, or right before releasing it from memory.

    Args
        arr (bytearray | numpy array): A mutable byte array.

    Returns
        None

    Raises
        Err if arr is not of type bytearray or numpy array.

    Example
        ```python
        from zeroize import mlock, munlock

        data = bytearray(b'hello') # Create a mutable bytearray

        mlock(data) # Lock the memory

        munlock(data) # Unlock the memory
        ```
    """

def zeroize1(arr: Union[bytearray, np.ndarray]) -> None:
    """
    Zeroize a bytearray or numpy array in memory.
    Overrides the memory with zeroes and ensures the data is no longer accessible.

    Args
        arr (bytearray | numpy array): A mutable byte array.

    Returns
        None

    Raises
        Err if arr is not of type bytearray or numpy array.

    Example
    ```python
    from zeroize import mlock, munlock, zeroize
    fn secure_and_delete_data(data):
        mlock(data)  # Lock the data in memory
        zeroize1(data)  # Wipe the data
        munlock(data)  # Unlock the data when done
    ```
    """