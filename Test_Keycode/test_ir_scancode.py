import subprocess
import re
from util import print_error, print_warning

"""
Read the output of dmesg and compare the keycode.
[ 9163.680256] meson-ir:receive scancode=0x0
:param process: The subprocess.Popen process
:param expected_ir_scancode: The expected RCU/IR-scancode
:param expected_linux_keycode: The expected linux-keycode
:return: True/False, True/False, failed_msg
"""
def read_dmesg_output(process, expected_ir_scancode, expected_linux_keycode):
    ret_ir = False
    ret_linux = False
    msg = ""

    for line in iter(process.stdout.readline, ''):
        if "meson-ir:receive scancode" in line:
            print(line)

            pattern = r"scancode=(\S+)"
            match = re.search(pattern, line)
            if match:
                #[<time>] meson-ir:receive scancode=<value>
                value = match.group(1)
                print(value)
                
                if int(expected_ir_scancode, 16) == int(value, 16):
                    ret_ir = True
                else:
                    msg += f"ir-scancode({expected_ir_scancode, value}) not matched"
            else:
                msg += f"Invalid dmesg: {line}"
            
            return ret_ir, ret_linux, msg

"""
Start dmesg and read its output, searching for the specified keycode.
:param expected_ir_scancode: The expected RCU/IR-scancode
:param expected_linux_keycode: The expected linux-keycode
:return: Whether the keycode was successfully found
"""
def run_dmesg(expected_ir_scancode, expected_linux_keycode):
    subprocess.run(['dmesg', '-C']) #Clear ring buffer without printing
    process = subprocess.Popen(
        ['dmesg', '-w'], 
        stdout=subprocess.PIPE, 
        text=True
    )

    try:
        ret_ir, ret_linux, msg = read_dmesg_output(process, expected_ir_scancode, expected_linux_keycode)
        return ret_ir, ret_linux, msg

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    
    finally:
        process.stdout.close()
        process.wait()

"""
Display a prompt message and test if the button corresponds to the correct keycode.
:param device: The device path (e.g., '/dev/input/event8')
:param key_name: The name of the button(key) to be tested
:param ble_scancode: The expected RCU/BLE-scancode
:param linux_keycode: The expected linux-keycode
"""
def test_ir_key(key_name, ir_scancode, linux_keycode):
    print_warning(f"Please press {key_name}\n>>>>")

    ret_ir, ret_linux, msg = run_dmesg(ir_scancode, linux_keycode)
    if ret_ir:
        print(f"{key_name} --> {ir_scancode, linux_keycode}, Success!\n\n")
    else:
        print_error(f"{key_name} --> {ir_scancode, linux_keycode}, Failed!({msg})\n\n")
    
    return ret_ir, ret_linux