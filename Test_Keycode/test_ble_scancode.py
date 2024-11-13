import re
import subprocess
from util import print_error, print_warning


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
                    if str(expected_ble_scancode).lower() in value:
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
def test_ble_key(device, key_name, ble_scancode, linux_keycode):
    print_warning(f"Please press {key_name}")

    ret_ble, ret_linux, msg = run_evtest(device, ble_scancode, linux_keycode)
    if ret_ble and ret_linux:
        print(f"{key_name} --> {ble_scancode, linux_keycode}, Success!\n\n")
    else:
        print_error(f"{key_name} --> {ble_scancode, linux_keycode}, Failed!({msg})\n\n")
    
    return ret_ble, ret_linux