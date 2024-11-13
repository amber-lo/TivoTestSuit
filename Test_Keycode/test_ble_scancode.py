import subprocess
from util import print_error, print_warning, read_evtest_output

"""
Start test.
:param device: The device path (e.g. /dev/input/event8)
:param expected_ble_scancode: The expected RCU/BLE-scancode
:param expected_linux_keycode: The expected linux-keycode
:return: Whether the keycode was successfully found
"""
def run_test(device, expected_ble_scancode, expected_linux_keycode):
    process = subprocess.Popen(
        ['/usr/bin/evtest', device],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True
    )

    try:
        ret_ble = False
        ret_linux = False
        
        ret_ble_scancode, ret_linux_keycode, msg = read_evtest_output(process)
        if str(expected_ble_scancode).lower() in ret_ble_scancode:
            ret_ble = True
        else:
            msg += f"BLE-scancode({expected_ble_scancode, ret_ble_scancode}) not matched, "
        
        if str(expected_linux_keycode) in ret_linux_keycode:
            ret_linux = True
        else:
            msg += f"Linux-keycode({expected_linux_keycode, ret_linux_keycode}) not matched"
        
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

    ret_ble, ret_linux, msg = run_test(device, ble_scancode, linux_keycode)
    if ret_ble and ret_linux:
        print(f"{key_name} --> {ble_scancode, linux_keycode}, Success!\n\n")
    else:
        print_error(f"{key_name} --> {ble_scancode, linux_keycode}, Failed!({msg})\n\n")
    
    return ret_ble, ret_linux