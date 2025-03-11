# File: pyCRUMBS/examples/leader_example.py

import sys
import logging
from pyCRUMBS import CRUMBS, CRUMBSMessage

logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG level for more verbosity
logger = logging.getLogger("LeaderExample")


def print_usage():
    print("Usage:")
    print("  To send a message, enter comma-separated values:")
    print(
        "    target_address,typeID,commandType,data0,data1,data2,data3,data4,data5,errorFlags"
    )
    print("  Example:")
    print("    0x08,1,1,75.0,1.0,0.0,65.0,2.0,7.0,0")
    print("")
    print("  To request a message from a target device, type:")
    print("    request,target_address")
    print("  Example:")
    print("    request,0x08")
    print("")
    print("  Type 'exit' to quit.")


def parse_message(input_str: str):
    logger.debug("Parsing input string: %s", input_str)  # Debug input string
    parts = input_str.split(",")
    if len(parts) != 10:
        logger.error("Incorrect number of fields. Expected 10, got %d.", len(parts))
        return None, None
    try:
        # Parse target address (supports hex and decimal)
        target_address_str = parts[0].strip()
        logger.debug("Parsed target address string: %s", target_address_str)
        if target_address_str.lower().startswith("0x"):
            target_address = int(target_address_str, 16)
        else:
            target_address = int(target_address_str)
        typeID = int(parts[1].strip())
        commandType = int(parts[2].strip())
        data = [float(x.strip()) for x in parts[3:9]]
        errorFlags = int(parts[9].strip())
        msg = CRUMBSMessage(
            typeID=typeID, commandType=commandType, data=data, errorFlags=errorFlags
        )
        logger.debug("Parsed message: %s", msg)  # Debug the resulting message object
        return target_address, msg
    except Exception as e:
        logger.error("Failed to parse message: %s", e)
        return None, None


def main():
    logger.debug("Starting main()")
    bus_number = 1  # Default I2C bus on Raspberry Pi
    crumbs = CRUMBS(bus_number)
    crumbs.begin()
    logger.debug("I2C bus initialized")

    print("pyCRUMBS Leader Example (Master) Running")
    print_usage()

    while True:
        try:
            line = input("Enter command: ").strip()
            logger.debug("User entered command: %s", line)  # Debug user input
            if line.lower() == "exit":
                logger.debug("Exit command received")
                break
            if line.lower().startswith("request"):
                # Format: request,target_address
                parts = line.split(",")
                if len(parts) != 2:
                    logger.error("Invalid request format.")
                    continue
                target_address_str = parts[1].strip()
                if target_address_str.lower().startswith("0x"):
                    target_address = int(target_address_str, 16)
                else:
                    target_address = int(target_address_str)
                logger.debug("Requesting message from address: 0x%02X", target_address)
                response = crumbs.request_message(target_address)
                logger.debug("Response raw data: %s", response)
                if response:
                    print("Received response:")
                    print(response)
                else:
                    print("No valid response received.")
            else:
                target_address, msg = parse_message(line)
                if msg is None:
                    print("Failed to parse message. Please check your input.")
                    continue
                logger.debug(
                    "Sending message %s to address 0x%02X", msg, target_address
                )
                crumbs.send_message(msg, target_address)
                print("Message sent.")
        except KeyboardInterrupt:
            logger.debug("KeyboardInterrupt received, exiting loop")
            break
        except Exception as e:
            logger.error("Error in main loop: %s", e)

    crumbs.close()
    print("Exiting pyCRUMBS Leader Example.")
    logger.debug("I2C bus closed, program exiting")


if __name__ == "__main__":
    # Optionally, print sys.path for debug:
    import sys

    logger.debug("sys.path: %s", sys.path)
    main()
