FROM balenalib/raspberrypi4-64-debian:bullseye-build
# use `install_packages` if you need to install dependencies,
# for instance if you need git, just uncomment the line below.
# RUN install_packages git

# Trick to get apt-get to not prompt for timezone in tzdata
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
  apt-get install -yq \
    libcamera-dev \
    libcamera-apps-lite \
    vim \
    ffmpeg \
    python3 \
    htop \
    v4l-utils \
    python3-picamera2 --no-install-recommends \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . camera_server
WORKDIR /usr/src/app/camera_server
RUN chmod +x start.sh
# from https://github.com/balena-io-experimental/libcamera-apps/blob/master/Dockerfile.template
RUN usermod -a -G video root
ENV UDEV=on

CMD ["sh","./start.sh"]
