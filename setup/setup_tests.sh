#!/bin/bash 

export CONDA_TEMP_PREFIX=$(mktemp -d)
echo "Deploying environment in "${CONDA_TEMP_PREFIX}
echo "Make sure you are running this with conda >=4.2"
echo "Check with 'conda -V'"
echo "Upgrade with 'conda update conda' from the *root* environment"


echo "Setting up blank environment"
conda create --prefix ${CONDA_TEMP_PREFIX} python=3.6
source activate ${CONDA_TEMP_PREFIX}

echo "Downloading packages"
curl -o /tmp/cachetools-2.1.0-py_0.tar.bz2 -L https://anaconda.org/conda-forge/cachetools/2.1.0/download/noarch/cachetools-2.1.0-py_0.tar.bz2
curl -o /tmp/geojson-2.3.0-py_0.tar.bz2 -L https://anaconda.org/conda-forge/geojson/2.3.0/download/noarch/geojson-2.3.0-py_0.tar.bz2
curl -o /tmp/jsonpickle-0.9.6-py_1.tar.bz2 -L https://anaconda.org/conda-forge/jsonpickle/0.9.6/download/noarch/jsonpickle-0.9.6-py_1.tar.bz2
curl -o /tmp/more-itertools-8.2.0-py_0.tar.bz2 -L https://anaconda.org/conda-forge/more-itertools/8.2.0/download/noarch/more-itertools-8.2.0-py_0.tar.bz2
curl -o /tmp/pyasn1-0.4.8-py_0.tar.bz2 -L https://anaconda.org/conda-forge/pyasn1/0.4.8/download/noarch/pyasn1-0.4.8-py_0.tar.bz2
curl -o /tmp/pyasn1-modules-0.2.7-py_0.tar.bz2 -L https://anaconda.org/conda-forge/pyasn1-modules/0.2.7/download/noarch/pyasn1-modules-0.2.7-py_0.tar.bz2

echo "Installing manually downloaded packages"
conda install /tmp/*.bz2

conda env update --file setup/environment36.yml
# python bin/deploy/habitica_conf.py
python bin/deploy/push_conf.py
python bin/deploy/model_copy.py
