from pathlib import Path


def handle_upload(origin, destination: Path):
    with destination.open("wb+") as dst:
        for chunk in origin.chunks():
            dst.write(chunk)
