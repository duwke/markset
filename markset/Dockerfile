FROM balenalib/raspberrypi4-64-ubuntu-python:jammy-build 
# use `install_packages` if you need to install dependencies,
# for instance if you need git, just uncomment the line below.
# RUN install_packages git

# Trick to get apt-get to not prompt for timezone in tzdata
ENV DEBIAN_FRONTEND=noninteractive

# Install MAVROS and some other dependencies for later
RUN apt-get update && \
    apt-get install -q -y \
        apt-transport-https \
        curl \
        gnupg2 \
        htop \
        vim \
        python3-pyaudio \
        portaudio19-dev \
        libsdl2-mixer-dev  libsdl2-image-dev libsdl2-ttf-dev libfreetype6-dev \
        software-properties-common && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get remove -q -y \
    python3-blinker && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/pip3 install \
        python-dateutil>=2.8.1 \
        asyncio quart coloredlogs apscheduler pyyaml  pygame \
        && \
    rm -rf ~/.cache/pip 


RUN /usr/local/bin/pip3 install \
        gpiod adafruit-circuitpython-framebuf adafruit-circuitpython-lis3dh adafruit-circuitpython-neopixel RPi.GPIO rpi_ws281x \
        && \
    rm -rf ~/.cache/pip 

# Set our working directory
WORKDIR /usr/src/app

# Copy requirements.txt first for better cache on later pushes
# COPY requirements.txt requirements.txt

# pip install python deps from requirements.txt on the resin.io build server
# RUN pip install -r requirements.txt

# This will copy all files in our root to the working  directory in the container
# COPY . ./
RUN git clone https://github.com/duwke/markset.git 

WORKDIR /usr/src/app/markset/markset

COPY music ./music
COPY config.yaml ./config.yaml

# Enable udevd so that plugged dynamic hardware devices show up in our container.
ENV UDEV=1

RUN git config --global user.email "darin@keever.cc" && \
    git config --global user.name "Darin Keever"

# main.py will run when container starts up on the device
#CMD ["/bin/bash"]
#CMD ["./code", "tunnel", "--accept-server-license-terms", "--name", "%%BALENA_MACHINE_NAME%%a"]
CMD ["python3", "main.py"]