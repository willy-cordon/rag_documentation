import unittest

from app.config import EMBEDDING_FINGERPRINT, QDRANT_EFFECTIVE_COLLECTION


class EmbeddingVersioningTest(unittest.TestCase):
    def test_effective_collection_contains_a_stable_fingerprint(self) -> None:
        self.assertTrue(EMBEDDING_FINGERPRINT)
        base, separator, suffix = QDRANT_EFFECTIVE_COLLECTION.rpartition("__")
        self.assertTrue(base)
        self.assertEqual(separator, "__")
        self.assertEqual(len(suffix), 10)


if __name__ == "__main__":
    unittest.main()
