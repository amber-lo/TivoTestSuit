import subprocess
import re
from util import print_error, print_warning, read_evtest_output, read_dmesg_output

"""
Start test.
:param device: The device path (e.g., '/dev/input/event3')
:param expected_ir_scancode: The expected RCU/IR-scancode
:param expected_linux_keycode: The expected linux-keycode
:return: Whether the keycode was successfully found
"""
def run_test(device, expected_ir_scancode, expected_linux_keycode):
    subprocess.run(['dmesg', '-C']) #Clear ring buffer without printing
    dmesg_process = subprocess.Popen(
        ['dmesg', '-w'], 
        stdout=subprocess.PIPE, 
        text=True
    )
    evtest_process = subprocess.Popen(
        ['/usr/bin/evtest', device],
        stdout=subprocess.PIPE,
        text=True
    )

    try:
        ret_ir = False
        ret_linux = False
        ret_msg = ""    
            
        ret_ir_scancode, msg = read_dmesg_output(dmesg_process)
        ret_msg += msg
        if int(expected_ir_scancode, 16) == int(ret_ir_scancode, 16):
            ret_ir = True
        else:
            ret_msg += f"ir-scancode({expected_ir_scancode, ret_ir_scancode}) not matched, "

        ret_ble_scancode, ret_linux_keycode, msg = read_evtest_output(evtest_process)
        ret_msg += msg
        if str(expected_linux_keycode) in ret_linux_keycode:
            ret_linux = True
        else:
            ret_msg += f"Linux-keycode({expected_linux_keycode, ret_linux_keycode}) not matched"

        return ret_ir, ret_linux, ret_msg

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    
    finally:
        dmesg_process.stdout.close()
        dmesg_process.wait()

        evtest_process.stdout.close()
        evtest_process.wait()

"""
Display a prompt message and test if the button corresponds to the correct keycode.
:param device: The device path (e.g., '/dev/input/event3')
:param key_name: The name of the button(key) to be tested
:param ir_scancode: The expected RCU/IR-scancode
:param linux_keycode: The expected linux-keycode
"""
def test_ir_key(device, key_name, ir_scancode, linux_keycode):
    print_warning(f"Please press {key_name}\n>>>>")

    ret_ir, ret_linux, msg = run_test(device, ir_scancode, linux_keycode)
    if ret_ir and ret_linux:
        print(f"{key_name} --> {ir_scancode, linux_keycode}, Success!\n\n")
    else:
        print_error(f"{key_name} --> {ir_scancode, linux_keycode}, Failed!({msg})\n\n")
    
    return ret_ir, ret_linux