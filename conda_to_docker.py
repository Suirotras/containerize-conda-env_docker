#!/usr/bin/env python

import tempfile
from subprocess import call
from os.path import abspath, join as join_path, dirname, realpath
import argparse
from pathlib import Path
from time import sleep


def _generate_file_list(conda_env, filelist_path):
    """
    Generate list of all files in the conda env.

    We need to include all files as absolute paths, and also the symbolic links they are pointing to (which
    might be outside the environment). To this end, the first `find` lists all files in the conda env.
    The second find finds the files the links point to. Using sort/uniq removes the duplicates files.

    TODO: While this covered all the cases I encountered so far, I believe this would still fail if there were nested
    symbolic links outside the repository.
    """
    command = f"""\
        #!/bin/bash
        set -o pipefail

        cat <(find {conda_env}) <(find -L {conda_env} -exec readlink -f "{{}}" ";") | \\
            sort | \\
            uniq > {filelist_path}
        """
    call(command, shell=True, executable="/bin/bash")


def _build_tar_archive(filelist_path, archive_path):
    """Build a tar archive from the filelist"""
    call(["tar", "cf", archive_path, "-T", filelist_path])


def _build_container(tmpdir, docker_file, image_name):
    """
    Actually builds the container.

    tmpdir is the temporary directory that already contains the tar archive.
    """
    call(
        [
            "docker",
            "build",
            "-f",
            docker_file,
            "-t",
            image_name,
            ".",
        ],
        cwd=tmpdir,
    )


def conda2docker(conda_env, image_name, template_path):

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        print(f"Using temporary directory: {tmpdir}")
        docker_file_path = tmpdir / "Dockerfile"
        filelist_path = tmpdir / "filelist.txt"
        tar_archive_path = tmpdir / "packed_env.tar"

        # Read Dockerfile template file
        with open(template_path) as f:
            template = "".join(f.readlines())
        template = template.format(conda_env=conda_env)

        # Write formatted template file
        with open(docker_file_path, "w") as f:
            f.write(template)

        print("Building file list...")
        _generate_file_list(conda_env, filelist_path)

        # We are using a tar archive as tar is the only way of getting the symbolic links into the Docker
        # container as symbolic links.
        print("Building tar archive...")
        _build_tar_archive(filelist_path, tar_archive_path)

        print("Building docker image...")
        _build_container(tmpdir, docker_file_path, image_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a conda env to a docker image."
    )
    parser.add_argument(
        "CONDA_ENV",
        help="Absolute path to the conda enviornment. Must be exactly the path as it shows up in `conda env list`, not a symbolic link to it, nor a realpath. ",
    )
    parser.add_argument(
        "OUTPUT_IMAGE",
        help="Name of the docker image that will be created",
    )
    parser.add_argument(
        "--template",
        help="Path to the Dockerfile template. Must contain a `{conda_env}` placeholder. If not specified, uses the default template shipped with this script.",
        default=join_path(dirname(realpath(__file__)), "Dockerfile"),
    )
    args = parser.parse_args()
    conda2docker(args.CONDA_ENV, args.OUTPUT_IMAGE, args.template)
