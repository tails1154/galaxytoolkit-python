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

def stage_command(args: list) -> bool:
    if len(args) < 4:
        print("Usage: stage <StageName> <ScenarioNo> <StarNo>")
        return False

    stage_name = args[1]
    try:
        scenario_no = int(args[2])
        star_no = int(args[3])
    except ValueError:
        print("Invalid ScenarioNo or StarNo.")
        return False

    message_data_address = get_message_data_address()
    if message_data_address is None:
        return False

    if not is_hooked():
        hook()
        if not is_hooked():
            print("Failed to hook Dolphin.")
            return False

    tool_message_address = message_data_address + TOOL_MESSAGE_OFFSET
    stage_name_address = message_data_address + DATA_OFFSET

    write_bytes(stage_name_address, stage_name.encode('ascii') + b'\x00')
    packed_value = (star_no << 16) | (scenario_no << 8) | CODE

    mw = MemWatch("stage_command", tool_message_address, False)
    mw.write_memory_from_string(str(packed_value))

    print(f"Sent stage '{stage_name}' with scenario {scenario_no} and star {star_no} (packed: 0x{packed_value:08X})")
    return True

def crash_command(args: list) -> bool:
    message_data_address = get_message_data_address()
    if message_data_address is None:
        return False

    if not is_hooked():
        hook()
        if not is_hooked():
            print("Failed to hook Dolphin.")
            return False

    tool_message_address = message_data_address + TOOL_MESSAGE_OFFSET

    mw = MemWatch("crash_command", tool_message_address, False)
    mw.write_memory_from_string(str(0xFFFFFFFF))

    print("Crash sent!")
    return True

def warp_command(args: list) -> bool:
    if len(args) < 3:
        print("Usage: warp <Type> <Value>")
        return False

    warp_type = args[1]
    value = args[2]

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

    if warp_type == "Pos":
        try:
            x, y, z = map(float, value.split(",", 2))
        except ValueError:
            print("Invalid value Vector3.")
            return False

        from struct import pack
        write_bytes(data_address, pack("<3f", x, y, z))

        mw = MemWatch("warp_pos", tool_message_address, False)
        mw.write_memory_from_string(str(POS_CODE))
        print(f"Warped to position ({x}, {y}, {z})")
        return True

    elif warp_type == "GeneralPos":
        write_bytes(data_address, value.encode("ascii") + b"\x00")

        mw = MemWatch("warp_general", tool_message_address, False)
        mw.write_memory_from_string(str(GENERAL_POS_CODE))
        print(f"Warped to general position '{value}'")
        return True

    print(f"Unknown warp type '{warp_type}'.")
    return False

def main():
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "stage":
            stagename = input("StageName> ")
            scenariono = input("ScenarioNo> ")
            starno = input("StarNo> ")
            stage_command(["stage", stagename, scenariono, starno])
        elif cmd == "crash":
            crash_command(["crash"])
        elif cmd == "warp":
            warp_type = input("Type (Pos or GeneralPos)> ")
            value = input("Value> ")
            warp_command(["warp", warp_type, value])
        elif cmd in ["exit", "quit"]:
            break

if __name__ == "__main__":
    main()
