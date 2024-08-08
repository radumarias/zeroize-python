def mlock(arr: bytearray) -> None:
    """
    Locks and prevents data from being overwritten or swapped to disk.
    Can lock a maximum of 2662 KB at a time.

    Args
        arr (bytearray): A mutable byte array.

    Returns
        None

    Raises
        TypeError: If the provided object is not mutable or does not support the buffer protocol.

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

def munlock(arr: bytearray) -> None:
    """
    Unlocks a mutable array in memory.
    Used to release the memory lock when the sensitive data is no longer needed.

    Args
        arr (bytearray): A mutable byte array.

    Returns
        None

    Raises
        TypeError: If the provided object is not mutable or does not support the buffer protocol.

    Example
        ```python
        from zeroize import mlock, munlock

        # Create a mutable bytearray
        data = bytearray(b'hello')

        # Lock the memory
        mlock(data)

        # Unlock the memory
        munlock(data)
        ```
    """

def zeroize1(arr):
    """
    Wipes a mutable array in memory.
    Overrides the memory with zeroes and ensures the data is no longer accessible.

    Args
        arr (bytearray): A mutable byte array.

    Returns
        None

    Raises
        TypeError: If the provided object is not mutable or does not support the buffer protocol.

    Example
    ```python
    from zeroize import mlock, munlock, zeroize
    fn secure_and_delete_data(data):
        mlock(data)  # Lock the data in memory
        zeroize1(data)  # Wipe the data
        munlock(data)  # Unlock the data when done
    ```
    """