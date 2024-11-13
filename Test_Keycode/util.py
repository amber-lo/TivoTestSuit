import re
import subprocess

def print_error(msg):
    print("\033[31m" + msg + "\033[0m")

def print_warning(msg):
    print("\033[33m" + msg + "\033[0m")

"""
Read the output of dmesg and compare the keycode.
[ 9163.680256] meson-ir:receive scancode=0x0
:param process: The process for dmesg
:return: ir_scancode, msg(for error case)
"""
def read_dmesg_output(process):
    ret_ir_scancode = "N/A"
    msg = ""

    for line in iter(process.stdout.readline, ''):
        if "meson-ir:receive scancode" in line:
            print(line)

            pattern = r"scancode=(\S+)"
            match = re.search(pattern, line)
            if match:
                #[<time>] meson-ir:receive scancode=<value>
                ret_ir_scancode = match.group(1)
                print(ret_ir_scancode)
            else:
                msg += f"Invalid dmesg: {line}"
            
            return ret_ir_scancode, msg


"""
Read the output of evtest and compare the keycode.

case#1: RCU/BLE
Event: time 1731326096.570439, type 4 (EV_MSC), code 4 (MSC_SCAN), value c0088
Event: time 1731326096.570439, type 1 (EV_KEY), code 4 (KEY_3), value 1
Event: time 1731326096.570439, -------------- SYN_REPORT ------------
Exit the loop when got: SYN_REPORT

case#2: RCU/IR
Event: time 1731489019.189864, type 1 (EV_KEY), code 116 (KEY_POWER), value 1
Event: time 1731489019.189864, -------------- SYN_REPORT ------------
Event: time 1731489019.392337, type 1 (EV_KEY), code 116 (KEY_POWER), value 0
Event: time 1731489019.392337, -------------- SYN_REPORT ------------

@param process: The process for evtest
@return: ret_ble_scancode, ret_linux_keycode, msg(for error case)
"""
def read_evtest_output(process):
    ret_ble_scancode = "N/A"
    ret_linux_keycode = "N/A"
    msg = ""

    for line in iter(process.stdout.readline, ''):
        if str("Testing ...") in line:
            print_warning(">>>>")       
        
        if line.startswith("Event: "):
            if "SYN_REPORT" in line:
                return ret_ble_scancode, ret_linux_keycode, msg

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
                    ret_ble_scancode = value
                    continue
                
                if "EV_KEY" in type_description: #Linux-keycod    
                    ret_linux_keycode = code_description
                    continue
            else:
                msg += f"Invalid event: {line}"
