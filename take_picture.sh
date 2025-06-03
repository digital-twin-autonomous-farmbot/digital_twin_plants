#!/bin/bash

OUTDIR="calib_images"
mkdir -p $OUTDIR

for i in $(seq -f "%02g" 1 15); do
    echo "Aufnahme $i"

    libcamera-jpeg --camera 0 -o $OUTDIR/left_$i.jpg --width 640 --height 480
    libcamera-jpeg --camera 1 -o $OUTDIR/right_$i.jpg --width 640 --height 480

    echo "Bildpaar $i aufgenommen"
    sleep 2
done
