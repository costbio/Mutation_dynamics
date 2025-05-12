# This Dockerfile has been updated from its original version:
# https://hub.docker.com/r/lcbio/cabsflex/
# The original version is outdated. This version includes Modeller setup,
# which requires you to obtain your own Modeller license key.
# For more information on how to use the CABSflex standalone Docker image, visit:
# https://bitbucket.org/lcbio/cabsflex/src/master/
#
# Last modified by: Onur
# Last modified on: May 12, 2025


# Start from an anaconda distribution to be extra safe 
FROM continuumio/anaconda

RUN rm /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-archive/debian buster main contrib non-free" > /etc/apt/sources.list 

# Install gfortran and packages that might be necessary 
RUN apt-get update && apt-get install -y gfortran pkg-config libfreetype6-dev libpng-dev python-dev libgl1-mesa-glx python-tk dssp

# Install CABS
RUN conda install -c lcbio cabs

# Install modeller - uncomment the lines below and replace the XXXX with your Modeller licence key  
ENV KEY_MODELLER="<REPLACE_WITH_YOUR_KEY>" 

# Install the downloaded package using conda
RUN conda install https://anaconda.org/salilab/modeller/10.5/download/linux-64/modeller-10.5-py27h9bf148f_0.tar.bz2 

# Define CABS-Flex as the default entrypoint for faster command writing 
ENTRYPOINT ["/opt/conda/bin/CABSflex"]

# Set the help flag as the default argument 
CMD ["-h"]