#!/bin/bash

OUTDIR="calib_images"
mkdir -p $OUTDIR

for i in $(seq -f "%02g" 1 15); do
    echo "Aufnahme $i"

    # Capture with normal camera (left)
    libcamera-jpeg --camera 0 -o $OUTDIR/left_plant$i.jpg --width 640 --height 480

    # Capture with AI camera (right)
    libcamera-jpeg --camera 1 -o $OUTDIR/right_plant$i.jpg --width 640 --height 480

    # Run AI detection on the right image and save bounding box
    rpicam-hello \
      --timeout 1s \
      --post-process-file /usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json \
      --post-process-output $OUTDIR/bbox_plant$i.json \
      --input $OUTDIR/right_plant$i.jpg \
      --width 640 --height 480

    echo "Bildpaar $i aufgenommen und Bounding Box gespeichert"
    sleep 2
done