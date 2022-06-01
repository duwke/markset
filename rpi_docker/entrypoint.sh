#!/bin/bash

fd=0
source /opt/ros/melodic/setup.bash
roscd mavros
echo "$@"
exec "$@"   