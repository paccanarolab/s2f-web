import os
from pathlib import Path


# This is the directory where fasta files are downloaded from the submission
# server, and also cotains the manager status file and log files.
MEDIA_ROOT = Path(
    os.getenv("S2F_MEDIA_ROOT",
              str(Path(__file__).parent.parent.parent / "experiments")))

# This is the S2F main configuration file, indicating where the installation
# directory is located
S2F_CONFIG = os.getenv("S2F_CONFIG")

# This is the path to the S2F.py script, used to invoke S2F commands from this
# client
S2F_ENTRY = os.getenv("S2F_ENTRY")
