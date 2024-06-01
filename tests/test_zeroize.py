import unittest
import zeroize

class TestStringMethods(unittest.TestCase):

    def test_zeroize(self):
        arr = bytearray(b'1234567890')
        zeroize.zeroize1(arr)
        self.assertEqual(arr, bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))

if __name__ == '__main__':
    unittest.main()