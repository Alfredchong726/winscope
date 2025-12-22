import pytest
from pathlib import Path
import tempfile
import shutil
from src.services.hash_calculator import HashCalculator


class TestHashCalculator:

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.txt"
        self.test_file.write_text("Hello, World!")

    def teardown_method(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_calculate_md5(self):
        calc = HashCalculator()
        hashes = calc.calculate_file_hashes(self.test_file, ['md5'])

        expected_md5 = "65a8e27d8879283831b664bd8b7f0ad4"
        assert hashes['md5'] == expected_md5

    def test_calculate_multiple_hashes(self):
        calc = HashCalculator()
        hashes = calc.calculate_file_hashes(self.test_file, ['md5', 'sha256'])

        assert 'md5' in hashes
        assert 'sha256' in hashes
        assert len(hashes) == 2

    def test_nonexistent_file(self):
        calc = HashCalculator()
        hashes = calc.calculate_file_hashes(Path("nonexistent.txt"))

        assert hashes == {}

    def test_verify_hash_success(self):
        calc = HashCalculator()
        expected = "65a8e27d8879283831b664bd8b7f0ad4"

        result = calc.verify_file_hash(self.test_file, expected, 'md5')
        assert result is True

    def test_verify_hash_failure(self):
        calc = HashCalculator()
        wrong_hash = "0000000000000000000000000000000"

        result = calc.verify_file_hash(self.test_file, wrong_hash, 'md5')
        assert result is False

    def test_get_supported_algorithms(self):
        calc = HashCalculator()
        algorithms = calc.get_supported_algorithms()

        assert 'md5' in algorithms
        assert 'sha1' in algorithms
        assert 'sha256' in algorithms
