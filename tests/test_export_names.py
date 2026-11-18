import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from opus2txt import process_opus_absorbance, process_opus_file


def sample(value):
    trace = SimpleNamespace(x=[1000], y=[value])
    return SimpleNamespace(
        a=trace, sm=trace, data_keys=["a", "sm"],
        print_parameters=lambda: print(f"Measurement {value}"),
    )


class ExportNameTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.output = Path(temp.name)

    def snapshot(self):
        return {p.relative_to(self.output).as_posix(): p.read_bytes()
                for p in self.output.rglob("*.txt")}

    def test_numeric_extensions_and_repeated_exports(self):
        with patch("opus2txt.read_opus", side_effect=[sample(1), sample(2), sample(3)]):
            process_opus_file("first/test.run.0", self.output)
            process_opus_file("first/test.run.01", self.output)
            first = self.snapshot()
            process_opus_file("second/test.run.0", self.output)
        saved = self.snapshot()
        self.assertEqual(len(saved), 9)
        for name, content in first.items():
            self.assertEqual(saved[name], content)
        for name, value in [("test.run.0", 1), ("test.run.01", 2), ("test.run.0_2", 3)]:
            self.assertEqual(saved[f"METADATA/{name}_META.txt"].splitlines()[-1], f"Measurement {value}".encode())
            for kind in ("ABS", "SRay"):
                self.assertEqual(saved[f"{kind}/{name}_{kind}.txt"].splitlines()[-1], f"1000\t{value}".encode())

    def test_absorbance_respects_existing_partial_export(self):
        old = self.output / "SRay" / "sample.0_SRay.txt"
        old.parent.mkdir()
        old.write_bytes(b"previous run")
        with patch("opus2txt.read_opus", side_effect=[sample(1), sample(10)]):
            process_opus_absorbance("sample.0", "reference.0", self.output)
        saved = self.snapshot()
        self.assertEqual(set(saved), {
            "SRay/sample.0_SRay.txt", "METADATA/sample.0_2_META.txt",
            "ABS/sample.0_2_ABS.txt", "SRay/sample.0_2_SRay.txt",
        })
        self.assertEqual(old.read_bytes(), b"previous run")
        self.assertEqual(saved["ABS/sample.0_2_ABS.txt"].splitlines()[-1], b"1000\t1.0")

    def test_failed_write_releases_the_name(self):
        broken = sample(1)
        del broken.sm
        with patch("opus2txt.read_opus", side_effect=[broken, sample(2)]):
            with self.assertRaises(AttributeError):
                process_opus_file("scan.0", self.output)
            self.assertEqual(self.snapshot(), {})
            process_opus_file("scan.0", self.output)
        self.assertTrue((self.output / "ABS/scan.0_ABS.txt").is_file())
