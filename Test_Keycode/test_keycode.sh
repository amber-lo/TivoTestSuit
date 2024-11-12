#!/bin/bash

EVTEST_TOOL="evtest"
KEYCODE_TEST_TOOL="test_keycode.py"

DEVICE=$1
KEY_CODE_MAP=$2

echo "****Install evtest tool****"
mount -o rw,remount /
cp "$EVTEST_TOOL" /usr/bin/
chmod +x /usr/bin/"$FILE_PATH"

echo "****Keycode Test Start****"
echo "Device: $DEVICE, Keycode mapping file: $KEY_CODE_MAP"
python3 $KEYCODE_TEST_TOOL $DEVICE $KEY_CODE_MAP
