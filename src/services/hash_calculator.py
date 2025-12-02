import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from src.services.logger import get_logger


class HashCalculator:
    CHUNK_SIZE = 8192

    def __init__(self):
        """Initialize hash calculator."""
        self.logger = get_logger()
        self.supported_algorithms = ['md5', 'sha1', 'sha256']

    def calculate_file_hashes(
        self,
        file_path: Path,
        algorithms: Optional[List[str]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, str]:
        if algorithms is None:
            algorithms = self.supported_algorithms

        invalid = [alg for alg in algorithms if alg not in self.supported_algorithms]
        if invalid:
            self.logger.warning(
                f"Unsupported algorithms: {invalid}. Using only supported algorithms.",
                module="HashCalculator"
            )
            algorithms = [alg for alg in algorithms if alg in self.supported_algorithms]

        if not algorithms:
            self.logger.error("No valid algorithms specified", module="HashCalculator")
            return {}

        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}", module="HashCalculator")
                return {}

            file_size = file_path.stat().st_size
            bytes_processed = 0

            hash_objects = {
                'md5': hashlib.md5(),
                'sha1': hashlib.sha1(),
                'sha256': hashlib.sha256()
            }

            hash_objects = {alg: obj for alg, obj in hash_objects.items() if alg in algorithms}

            self.logger.debug(
                f"Calculating {', '.join(algorithms)} hashes for {file_path.name}",
                module="HashCalculator"
            )

            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break

                    for hash_obj in hash_objects.values():
                        hash_obj.update(chunk)

                    bytes_processed += len(chunk)

                    if progress_callback and file_size > 0:
                        progress_callback(bytes_processed, file_size)

            # Get hex digests
            result = {alg: hash_obj.hexdigest() for alg, hash_obj in hash_objects.items()}

            self.logger.debug(
                f"Hash calculation complete for {file_path.name}",
                module="HashCalculator"
            )

            return result

        except PermissionError:
            self.logger.error(
                f"Permission denied reading file: {file_path}",
                module="HashCalculator"
            )
            return {}
        except Exception as e:
            self.logger.error(
                f"Error calculating hashes for {file_path}: {e}",
                module="HashCalculator",
                exc_info=True
            )
            return {}

    def verify_file_hash(
        self,
        file_path: Path,
        expected_hash: str,
        algorithm: str = 'sha256'
    ) -> bool:
        if algorithm not in self.supported_algorithms:
            self.logger.error(f"Unsupported algorithm: {algorithm}", module="HashCalculator")
            return False

        calculated = self.calculate_file_hashes(file_path, [algorithm])

        if not calculated:
            return False

        actual_hash = calculated.get(algorithm, "")
        matches = actual_hash.lower() == expected_hash.lower()

        if matches:
            self.logger.info(
                f"Hash verification successful for {file_path.name}",
                module="HashCalculator"
            )
        else:
            self.logger.warning(
                f"Hash mismatch for {file_path.name}! "
                f"Expected: {expected_hash}, Got: {actual_hash}",
                module="HashCalculator"
            )

        return matches

    def get_supported_algorithms(self) -> List[str]:
        return self.supported_algorithms.copy()
