import re
from typing import Dict
from uuid import UUID


def validate_uuid(text: str) -> bool:
    try:
        uuid_test = UUID(text, version=4)
    except ValueError:
        return False
    return str(uuid_test) == text


def validate_sequence(sequence) -> bool:
    valid_aminoacids = set(["A", "B", "C", "D", "E", "F",
                            "G", "H", "I", "K", "L", "M",
                            "N", "P", "Q", "R", "S", "T",
                            "V", "W", "X", "Y", "Z"])
    return len(set(sequence) - valid_aminoacids) == 0


def fasta_validator(fname) -> Dict:
    status = "nothing"
    seq = ""
    message_bad_sequence = "A sequence should be composed of only"\
                           " ABCDEFGHIKLMNPQRSTVWXYZ"
    message_empty_structure = "Our system does not support FASTA files with"\
                              " empty sequences"
    message_orphan_seq = "Our system detected a sequence without ID, which is"\
                         " not supported"
    print(f"validating fasta {fname}")
    with open(fname) as f:
        for lineno, line in enumerate(f):
            if line[0] == ">":
                if status == "seqID":
                    return {
                        "status": "empty_sequence",
                        "message": message_empty_structure,
                        "lineno": lineno
                    }
                if status == "seq":
                    if not validate_sequence(seq):
                        return {
                            "status": "bad_sequence",
                            "message": message_bad_sequence,
                            "lineno": lineno
                        }
                seq = ""
                status = "seqID"
            else:
                if status == "nothing":
                    return {
                        "status": "orphan_sequence",
                        "message": message_orphan_seq,
                        "lineno": lineno
                    }
                status = "seq"
                seq += line.strip()
        if not seq:
            return {
                "status": "empty_sequence",
                "message": message_empty_structure,
                "lineno": "last"
            }
        elif not validate_sequence(seq):
            return {
                "status": "bad_sequence",
                "message": message_bad_sequence,
                "lineno": "last"
            }
    return {"status": "valid", "message": "valid"}


def annotation_validator(fname) -> Dict:
    message_bad_columns = "The annotation file has more than 2 columns"
    message_bad_goterm = "The annotation file contains invalid GO terms"
    re_go = re.compile("^GO:[0-9]{7}")
    print(f"validating annotation {fname}")
    for lineno, line in enumerate(open(fname)):
        parts = line.replace("\n", "").split("\t")
        if len(parts) != 2:
            return {
                "status": "bad_columns",
                "message": message_bad_columns,
                "lineno": lineno
            }
        goterm = parts[1]
        if not re_go.match(goterm):
            return {
                "status": "bad_goterm",
                "message": message_bad_goterm,
                "lineno": lineno
            }
    return {"status": "valid", "message": "valid"}
