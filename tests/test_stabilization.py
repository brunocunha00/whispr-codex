import unittest

from whispr.stabilization import StablePrefixCommitter, longest_common_prefix, trim_to_word_boundary


class StabilizationTests(unittest.TestCase):
    def test_longest_common_prefix(self) -> None:
        self.assertEqual(longest_common_prefix("ola mundo", "ola maria"), "ola m")

    def test_trim_to_word_boundary(self) -> None:
        self.assertEqual(trim_to_word_boundary("ola mun"), "ola ")
        self.assertEqual(trim_to_word_boundary("ola "), "ola ")

    def test_committer_only_releases_stable_prefix(self) -> None:
        committer = StablePrefixCommitter()
        self.assertEqual(committer.observe("ola mun"), "")
        self.assertEqual(committer.observe("ola mundo"), "ola ")
        self.assertEqual(committer.flush("ola mundo bonito"), "mundo bonito")


if __name__ == "__main__":
    unittest.main()
