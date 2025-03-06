# Latest Combined model on Jetson Orin 64GB

## Pre-requisites:
* Python 3.10.
* Install the requirements mentioned in requirements.txt inside virtual environment

## Creating virtual environment
* Create a folder object_tracking before creating virtual environment.
* Inside object tracking folder install virtual environment.
* Install Virtualenv using sudo apt install virtualenv.
* Create a virtual environment in a folder of using virtualenv venv where venv is the name of virtual environment.
* Activate the environment using source venv/bin/activate.
* Install the pip packages using command pip install -r requirements.txt 
(Note: Please dont install tensorflow using pip install tensorflow it has a seperate procedure to install tensorflow on Jetson to utilize gpu).

## Required folders inside object_tracking.
* After cloning this repo inside object_tracking make sure you create these empty folders which are mentioned below,
* mkdir image_to_ui
* mkdir images
* mkdir payloads
* mkdir predicted_images
* mkdir order_status_payloads

## Install tensorflow inside virtual environment
* Installing Tensorflow and other packages on Jetson Orin.
* Follow the instructions below to install TensorFlow in Jetson Orin,
* Install system packages required by TensorFlow:
* sudo apt-get update
* sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran
* Upgrade pip:
* python3 -m pip install --upgrade pip
* pip3 install -U testresources setuptools==65.5.0
* Install the Python package dependencies:
* pip install -U numpy==1.22 future==0.18.2 mock==3.0.5 keras_preprocessing==1.1.2 keras_applications==1.0.8 gast==0.4.0 protobuf==3.20.3 pybind11 cython pkgconfig packaging h5py==3.6.0
* Install tensorflow using this command: pip3 install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v512 tensorflow==2.12.0+nv23.06
* To check Jetpack version: sudo apt show nvidia-jetpack or jtop
* Follow this link to install jtop https://jetsonhacks.com/2023/02/07/jtop-the-ultimate-tool-for-monitoring-nvidia-jetson-devices/
* check tensorflow is installed properly through import tensorflow 

 


 
