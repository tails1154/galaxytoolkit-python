from dolphin_memory_engine import MemWatch, write_bytes, is_hooked, hook

# Constants
CODE = 3
TOOL_MESSAGE_OFFSET = 0x00  # mToolMessage offset (0x00)
STAGE_NAME_OFFSET = 0x08     # mData offset (0x08)

def stage_command(args: list) -> bool:
    if len(args) < 4:
        print("Usage: stage <StageName> <ScenarioNo> <StarNo>")
        return False

    # Get stage name and convert to int
    stage_name = args[1]
    try:
        scenario_no = int(args[2])
        star_no = int(args[3])
    except ValueError:
        print("Invalid ScenarioNo or StarNo.")
        return False

    # Ask for the address of MessageData::sInstance
    message_data_address = input("Enter the address of MessageData::sInstance (e.g., 0x80002FF4): ")
    try:
        message_data_address = int(message_data_address, 16)  # Convert the address to int
    except ValueError:
        print("Invalid address format.")
        return False

    # Hook Dolphin if not already hooked
    if not is_hooked():
        hook()
        if not is_hooked():
            print("Failed to hook Dolphin.")
            return False

    # Calculate addresses for mToolMessage and mData using the base address
    tool_message_address = message_data_address + TOOL_MESSAGE_OFFSET
    stage_name_address = message_data_address + STAGE_NAME_OFFSET

    # Write stage name as string (null-terminated)
    write_bytes(stage_name_address, stage_name.encode('ascii') + b'\x00')

    # Pack the command: [starNo (8 bits) << 16] | [scenarioNo (8 bits) << 8] | Code
    packed_value = (star_no << 16) | (scenario_no << 8) | CODE

    # Write to mToolMessage
    mw = MemWatch("stage_command", tool_message_address, False)
    mw.write_memory_from_string(str(packed_value))  # Expects a decimal string

    print(f"Sent stage '{stage_name}' with scenario {scenario_no} and star {star_no} (packed: 0x{packed_value:08X})")
    return True
# 0xFFFFFFFF crash
def crash_command(args: list) -> bool:
    # if len(args) < 4:
    #     print("Usage: crash")
    #     return False
    #
    # # Get stage name and convert to int
    # stage_name = args[1]
    # try:
    #     scenario_no = int(args[2])
    #     star_no = int(args[3])
    # except ValueError:
    #     print("Invalid ScenarioNo or StarNo.")
    #     return False

    # Ask for the address of MessageData::sInstance
    message_data_address = input("Enter the address of MessageData::sInstance. It should of been OSReported when the game launched.")
    try:
        message_data_address = int(message_data_address, 16)  # Convert the address to int
    except ValueError:
        print("Invalid address format.")
        return False

    # Hook Dolphin if not already hooked
    if not is_hooked():
        hook()
        if not is_hooked():
            print("Failed to hook Dolphin.")
            return False

    # Calculate addresses for mToolMessage and mData using the base address
    tool_message_address = message_data_address + TOOL_MESSAGE_OFFSET
    # stage_name_address = message_data_address + STAGE_NAME_OFFSET

    # Write stage name as string (null-terminated)
    # write_bytes(stage_name_address, stage_name.encode('ascii') + b'\x00')

    # Pack the command: [starNo (8 bits) << 16] | [scenarioNo (8 bits) << 8] | Code
    # packed_value = (star_no << 16) | (scenario_no << 8) | CODE

    # Write to mToolMessage
    mw = MemWatch("crash_command", tool_message_address, False)
    mw.write_memory_from_string(str("4294967295"))  # Expects a decimal string

    print(f"Sent stage '{stage_name}' with scenario {scenario_no} and star {star_no} (packed: 0x{packed_value:08X})")
    return True
def main():
    while True:
        cmd = input(">")
        if cmd.lower() == "stage":
            stagename = input("StageName> ")
            scenariono = input("ScenarioNo> ")
            starno = input("StarNo> ")
            stage_command(["stage", stagename, scenariono, starno])
        elif cmd.lower() in ["exit", "quit"]:
            break

if __name__ == "__main__":
    main()
