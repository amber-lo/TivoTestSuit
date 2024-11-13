import argparse
import time
from csv_reader import csv_reader, csv_writer
from test_ble_scancode import test_ble_key
from test_ir_scancode import test_ir_key

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument("device", help="BLE: RCU/BLE")
    parser.add_argument("filepath", help="Keycode mapping file(.csv) for RCU deployment")
    args = parser.parse_args()
    
    start_time = int(time.time()*1000) #ms
    
    # IR/BLE RCU
    if args.device == "BLE":
        device = '/dev/input/event8' #ble_keypad
    elif args.device == "IR":
        device = '/dev/input/event3' #ir_keypad
    else:
        print(f"{args.device} is not supported")

    # Keycode mapping file
    csv_file = args.filepath
    keycode_map = csv_reader(csv_file)

    for item in keycode_map:
        if args.device == "BLE":
            ret_ble, ret_linux = test_ble_key(device, item['key_name'], item['ble_scancode'], item['linux_keycode'])
            item['ble_result'] = ret_ble
            item['linux_result'] = ret_linux
        elif args.device == "IR":
            ret_ir, ret_linux = test_ir_key(item['key_name'], item['ir_scancode'], item['linux_keycode'])
            item['ir_result'] = ret_ir
            item['linux_result'] = ret_linux

    csv_writer("/testing/test_keycode_result.csv", keycode_map)
    
    end_time = int(time.time()*1000) #ms
    duration = end_time-start_time
    print(f"Test Keycode costs: {duration}ms")