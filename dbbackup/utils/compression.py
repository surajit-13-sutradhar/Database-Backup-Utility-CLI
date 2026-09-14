import gzip
import shutil
from pathlib import Path


def compress_file(source_path: str) -> str:
    """
    Compress the file at source_path using gzip, producing source_path + '.gz'.
    Deletes the original uncompressed file afterward.
    Returns the path to the compressed file.
    """
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Cannot compress: {source} does not exist.")

    compressed_path = source.with_suffix(source.suffix + ".gz")

    with open(source, "rb") as f_in:
        with gzip.open(compressed_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    source.unlink()  # remove the original uncompressed file

    return str(compressed_path)

def decompress_file(source_path: str, output_path: str) -> str:
    """
    Decompress a .gz file at source_path into output_path.
    Returns output_path. Does not delete the original .gz file.
    """
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Cannot decompress: {source} does not exist.")

    with gzip.open(source, "rb") as f_in:
        with open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return output_path