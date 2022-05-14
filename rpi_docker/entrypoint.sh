#!/bin/bash

FCUURL=$1

source /opt/ros/melodic/setup.bash
roscd mavros
echo ${FCUURL}
bash