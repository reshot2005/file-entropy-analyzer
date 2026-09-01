import collections
import math
import tempfile
import unittest
from pathlib import Path

from entropy_analyzer import (
    classify_entropy,
    analyze_file,
    shannon_entropy_from_counts,
)


class TestEntropyAnalyzer(unittest.TestCase):
    def test_empty_distribution(self):
        self.assertEqual(
            shannon_entropy_from_counts(collections.Counter(), 0),
            0.0,
        )

    def test_single_value_has_zero_entropy(self):
        counts = collections.Counter({65: 100})
        self.assertEqual(shannon_entropy_from_counts(counts, 100), 0.0)

    def test_two_equally_likely_values(self):
        counts = collections.Counter({0: 50, 255: 50})
        self.assertAlmostEqual(
            shannon_entropy_from_counts(counts, 100),
            1.0,
            places=10,
        )

    def test_uniform_256_bytes_has_eight_bits(self):
        counts = collections.Counter({value: 1 for value in range(256)})
        self.assertAlmostEqual(
            shannon_entropy_from_counts(counts, 256),
            8.0,
            places=10,
        )

    def test_analyze_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            path.write_bytes(bytes([0, 1, 2, 3]) * 100)

            size, entropy = analyze_file(path, chunk_size=7)

            self.assertEqual(size, 400)
            self.assertAlmostEqual(entropy, 2.0, places=10)

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.bin"
            path.write_bytes(b"")

            size, entropy = analyze_file(path)

            self.assertEqual(size, 0)
            self.assertEqual(entropy, 0.0)

    def test_classification(self):
        self.assertIn("Low entropy", classify_entropy(2.0))
        self.assertIn("Moderate entropy", classify_entropy(5.0))
        self.assertIn("High entropy", classify_entropy(7.8))

    def test_invalid_chunk_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            path.write_bytes(b"data")

            with self.assertRaises(ValueError):
                analyze_file(path, chunk_size=0)


if __name__ == "__main__":
    unittest.main()
