
# Containerize an existing conda environment in a docker container

I use conda environments for environment management during my data
analysis projects. Sometimes I need to revert to install using `pip` or `R`'s
`install.packages` if a package is not on bioconda or conda-forge.

To keep my code reproducible, and make sure my conda environments are portable,
adapted code from another repository
[https://github.com/grst/containerize-conda](https://github.com/grst/containerize-conda)
to containerize my conda environments.

Using the instructions below allows to package an existing environment
into a Singularity container which should be more portable
and can also easily be integrated into a [fully reproducible
data analysis
workflow](https://grst.github.io/bioinformatics/2019/12/23/reportsrender.html)
based on e.g. [Nextflow](https://www.nextflow.io/).

## Usage

```
usage: conda_to_docker.py [-h] [--template TEMPLATE] CONDA_ENV OUTPUT_CONTAINER

Convert a conda env to a singularity container.

positional arguments:
  CONDA_ENV            Absolute path to the conda enviornment. Must be exactely the path as it shows up in `conda env list`, not a symbolic link to it, nor a realpath.
  OUTPUT_CONTAINER     Name of the docker image that will be created.

optional arguments:
  -h, --help           show this help message and exit
  --template TEMPLATE  Path to the Dockerfile template. Must contain a `{conda_env}` placeholder. If not specified, uses the default template shipped with this script.
```

For example

```sh
conda_to_docker.py "/home/jari/miniconda3/envs/genomics" genomics.sif
```

## How it works

Conda envs cannot simply be "moved" as some paths are hardcoded into the environment.
I previously applied `conda-pack` to solve this issue, which works fine in most cases
but breaks in some (especially for old environments that have a long history
of manually installing stuff through R or pip).

This is an other appraoch where the issue is solved by copying the conda environment
with its full absolute path to the container.

After the container is started, a command should be given to activate the conda environment
from that path.

```sh
source /opt/conda/bin/activate {conda_env}
```

For example

```sh
source /opt/conda/bin/activate /home/jari/miniconda3/envs/genomics
```

The tar archive keeps all symbolic links intact *within* the conda environment, but at the
same time include all files that are outside the conda env, but referenced by a symbolic link.
