import argparse
import re
import subprocess
import time
from csv_reader import csv_reader, csv_writer

def print_error(msg):
    print("\033[31m" + msg + "\033[0m")

def print_warning(msg):
    print("\033[33m" + msg + "\033[0m")

"""
Read the output of evtest and compare the keycode.
Event: time 1731326096.570439, type 4 (EV_MSC), code 4 (MSC_SCAN), value c0088
Event: time 1731326096.570439, type 1 (EV_KEY), code 4 (KEY_3), value 1
Event: time 1731326096.570439, -------------- SYN_REPORT ------------
Exit the loop when got: SYN_REPORT

:param process: The subprocess.Popen process
:param expected_ble_scancode: The expected RCU/BLE-scancode
:param expected_linux_keycode: The expected linux-keycode
:return: True/False, True/False, failed_msg
"""
def read_evtest_output(process, expected_ble_scancode, expected_linux_keycode):
    ret_ble = False
    ret_linux = False
    msg = ""
    for line in iter(process.stdout.readline, ''):
        if str("Testing ...") in line:
            print_warning(">>>>")
        
        if "SYN_REPORT" in line:
            return ret_ble, ret_linux, msg
        
        if line.startswith("Event: "):
            pattern = r'type (\d+) \((.*?)\), code (\d+) \((.*?)\), value (\w+)'
            match = re.search(pattern, line)
            if match:
                #Event: time <time>, type <type_value> (<type_description>), code <code_value> (<code_description>), value <value>
                type_value = match.group(1)
                type_description = match.group(2)
                code_value = match.group(3)
                code_description = match.group(4)
                value = match.group(5)

                if "EV_MSC" in type_description: #BLE-scancode
                    if str(expected_ble_scancode) in value.lower():
                        ret_ble = True
                        continue
                    else:
                        msg += f"BLE-scancode({expected_ble_scancode, value}) not matched, "
                
                if "EV_KEY" in type_description: #Linux-keycode
                    if str(expected_linux_keycode) in code_description:
                        ret_linux = True
                        continue
                    else:
                        msg += f"Linux-keycode({expected_linux_keycode, code_description}) not matched"
            else:
                msg += f"Invalid event: {line}"

"""
Start evtest and read its output, searching for the specified keycode.
:param device: The device path (e.g. /dev/input/event8)
:param expected_ble_scancode: The expected RCU/BLE-scancode
:param expected_linux_keycode: The expected linux-keycode
:return: Whether the keycode was successfully found
"""
def run_evtest(device, expected_ble_scancode, expected_linux_keycode):
    process = subprocess.Popen(
        ['/usr/bin/evtest', device],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True
    )

    try:
        ret_ble, ret_linux, msg = read_evtest_output(process, expected_ble_scancode, expected_linux_keycode)
        return ret_ble, ret_linux, msg

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    
    finally:
        process.stdout.close()
        process.stderr.close()
        process.stdin.close()
        process.wait()

"""
Display a prompt message and test if the button corresponds to the correct keycode.
:param device: The device path (e.g., '/dev/input/event8')
:param key_name: The name of the button(key) to be tested
:param ble_scancode: The expected RCU/BLE-scancode
:param linux_keycode: The expected linux-keycode
"""
def test_button(device, key_name, ble_scancode, linux_keycode):
    print_warning(f"Please press {key_name}")

    ret_ble, ret_linux, msg = run_evtest(device, ble_scancode, linux_keycode)
    if ret_ble and ret_linux:
        print(f"{key_name} --> {ble_scancode, linux_keycode}, Success!\n\n")
    else:
        print_error(f"{key_name} --> {ble_scancode, linux_keycode}, Failed!({msg})\n\n")
    
    return ret_ble, ret_linux

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument("device", help="BLE: RCU/BLE")
    parser.add_argument("filepath", help="Keycode mapping file(.csv) for RCU deployment")
    args = parser.parse_args()
    
    start_time = int(time.time()*1000) #ms
    
    # IR/BRE RCU
    #device = '/dev/input/event3' #ir_keypad
    if args.device == "BLE":
        device = '/dev/input/event8' #ble_keypad
    else:
        print(f"{args.device} is not supported")

    # Keycode mapping file
    csv_file = args.filepath
    keycode_map = csv_reader(csv_file)

    for item in keycode_map:
        ret_ble, ret_linux = test_button(device, item['key_name'], item['ble_scancode'], item['linux_keycode'])
        item['ble_result'] = ret_ble
        item['linux_result'] = ret_linux

    csv_writer("/testing/test_keycode_result.csv", keycode_map)
    
    end_time = int(time.time()*1000) #ms
    duration = end_time-start_time
    print(f"Test Keycode costs: {duration}ms")