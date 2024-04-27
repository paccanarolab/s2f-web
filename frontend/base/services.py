from pathlib import Path


def handle_upload(origin, destination: Path):
    with destination.open("wb+") as dst:
        for chunk in origin.chunks():
            dst.write(chunk)


def file_iterator(filepath: Path, chunk_size=512):
    with filepath.open() as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
