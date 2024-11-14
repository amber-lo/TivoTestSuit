# How to use it

## Table of Contents
1. [Introduction](#introduction)
2. [Usage](#usage)

---
## Introduction
Provide a simple tool to verify if the remote control behavior is correct via checking RCU IR/BLE-scancode and Linux-keycode for the platform.

## Usage
1. Download Test_Keycode to device, @/testing/
2. ```bash
   ./test_keycode.sh [BLE/IR] [file(.csv)]
* BLE: Remote control via bluetooth connection
* IR: Remote control via IR settin
* file: A map for BLE-/IR-scancode and linux-keycide in .csv format (Please refer to TiVo_Sharp_US_RCU_for_Turnkey.csv)
3. Test step-by-step, and the result will be saved @/testing/test_keycode_result.csv
