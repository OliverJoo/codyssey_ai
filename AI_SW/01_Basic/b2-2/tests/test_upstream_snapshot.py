"""고정한 원격 commit의 src 스냅샷이 변조되지 않았는지 검사한다."""

from hashlib import sha256
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "count_utils.py": "a50398767ed3ad17c30bca45c2713016c6185685fdaadef7a56e5f4e659d45f6",
    "list_utils.py": "f9657a2bdeb3512b8afae0ab733766a68329798f8b343bad58b4aa760a3fd38a",
    "main.py": "a71940f491b306a8e8ec248fb78da669bab6a2c1451014b60d5ff5614ea2ee5d",
    "math_utils.py": "f5bd85639645068c9ba33320c57a0789ff960eff85b3ff868bd8d0926192fc78",
    "string_utils.py": "39fc4d3050a923d02b13de614f7f9f77cca38fe26aebb3dc8c0601cf270f19a5",
}
EVIDENCE_EXPECTED = {
    "new-file.md": "343215f6553006a54bb15606fc248672aa477dccc2e52ad672c3cea7be2ca249",
    "new_guide.md": "c0ced22429b3957faebf7993cb34c9c93abad03819266f6aa2ba8ef570b358be",
    "git-log.txt": "a58784ab41edce0b9f70be9fce66b5985512a921c3f489d6c05f7877a551389d",
}


class UpstreamSnapshotTest(unittest.TestCase):
    def test_src_matches_upstream_commit_daecf53(self) -> None:
        actual = {
            path.name: sha256(path.read_bytes()).hexdigest()
            for path in sorted((ROOT / "src").glob("*.py"))
        }
        self.assertEqual(actual, EXPECTED)

    def test_evidence_files_match_upstream_commit_daecf53(self) -> None:
        actual = {
            name: sha256((ROOT / "docs" / name).read_bytes()).hexdigest()
            for name in EVIDENCE_EXPECTED
        }
        self.assertEqual(actual, EVIDENCE_EXPECTED)


if __name__ == "__main__":
    unittest.main()
