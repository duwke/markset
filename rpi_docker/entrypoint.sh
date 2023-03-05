#!/bin/bash

fd=0
source /opt/ros/rolling/setup.bash
cd /home/root
echo "$@"
exec "$@"   