import unittest

from processing.preprocessing import is_expensive, needs_warm_clothes


class PreprocessingTests(unittest.TestCase):
    def test_warm_clothes_boundary(self):
        self.assertTrue(needs_warm_clothes(-0.1))
        self.assertFalse(needs_warm_clothes(0))

    def test_expensive_boundary(self):
        self.assertFalse(is_expensive(100))
        self.assertTrue(is_expensive(100.01))


if __name__ == "__main__":
    unittest.main()
