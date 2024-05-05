from pathlib import Path
from s2f_client.core import commands
import logging


MEDIA_ROOT = Path(__file__).parent / "experiments"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Structurally Informed Features"
    )
    subparsers = parser.add_subparsers(
        help="sub-command help",
        dest="subcommand")

    # progress on all jobs
    step_jobs = subparsers.add_parser(
        "step",
        help="Loads all the local jobs and steps through each of them",
    )

    step_jobs.set_defaults(func=commands.step_all_jobs)
    step_jobs.add_argument("-r", "--media-root",
                           help="Path to the directory where jobs are stored",
                           type=Path,
                           default=MEDIA_ROOT)

    # delete all azure containers
    delete_all_containers = subparsers.add_parser(
        "delete_all_containers",
        help="Deletes all the containers in the configured Azure account",
    )
    delete_all_containers.set_defaults(func=commands.delete_all_containers)

    # delete all azure containers
    list_all_containers = subparsers.add_parser(
        "list_all_containers",
        help="List all containers and blobs in the configured Azure account",
    )
    list_all_containers.set_defaults(func=commands.list_all_containers)

    # Parse the arguments and route the function call
    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError as e:
        print(e)
        parser.parse_args(['--help'])
