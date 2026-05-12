#!/usr/bin/env python3
import sys
from dolphin_memory_engine import MemWatch, write_bytes, is_hooked, hook

# Constants
CODE = 3
POS_CODE = 4
GENERAL_POS_CODE = (1 << 8) | 4
TOOL_MESSAGE_OFFSET = 0x00  # mToolMessage offset (0x00)
DATA_OFFSET = 0x08          # mData offset (0x08)

# Change this to match Dolphin's reported value
MESSAGE_DATA_ADDRESS_HEX = "0x80800ae8"

def get_message_data_address():
    try:
        return int(MESSAGE_DATA_ADDRESS_HEX, 16)
    except ValueError:
        print("Invalid MessageData address.")
        return None

def start_galaxy(galaxy_name: str, star_no: int, scenario_no: int) -> bool:
    """Start a galaxy with the specified parameters."""
    message_data_address = get_message_data_address()
    if message_data_address is None:
        return False

    if not is_hooked():
        hook()
        if not is_hooked():
            print("Failed to hook Dolphin.")
            return False

    tool_message_address = message_data_address + TOOL_MESSAGE_OFFSET
    data_address = message_data_address + DATA_OFFSET

    # Write galaxy name to data
    write_bytes(data_address, galaxy_name.encode('ascii') + b'\x00')
    
    # Pack the values: star_no (16 bits) | scenario_no (8 bits) | CODE
    packed_value = (star_no << 16) | (scenario_no << 8) | CODE

    mw = MemWatch("start_galaxy", tool_message_address, False)
    mw.write_memory_from_string(str(packed_value))

    print(f"Started galaxy '{galaxy_name}' with scenario {scenario_no} and star {star_no} (packed: 0x{packed_value:08X})")
    return True

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 startgalaxy_param.py <galaxy> <star_no> <scenario_no>")
        print("Example: python3 startgalaxy_param.py GalaxyName 5 1")
        sys.exit(1)

    galaxy_name = sys.argv[1]
    try:
        star_no = int(sys.argv[2])
        scenario_no = int(sys.argv[3])
    except ValueError:
        print("Error: star_no and scenario_no must be integers.")
        sys.exit(1)

    if start_galaxy(galaxy_name, star_no, scenario_no):
        print("Success!")
        sys.exit(0)
    else:
        print("Failed to start galaxy.")
        sys.exit(1)

if __name__ == "__main__":
    main()
