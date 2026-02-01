# src/main.py

import traceback
import socket
from network.packet_io import PacketIO


def main() -> None:
    """
    Execute a basic status request against a Minecraft server.

    This script connects to a Hypixel server on mc.hypixel.net:25565,
    sends a handshake and status request, and prints the server response.
    """
    host = "localhost"
    port = 25565
    protocol_version = 774

    try:
        # Establish a TCP connection to the server
        with socket.create_connection((host, port)) as sock:
            packet_io = PacketIO(sock)

            # Send handshake (intent=1 for Status)
            packet_io.send(
                packet_id="0x00",
                protocol_version=protocol_version,
                server_address=host,
                server_port=port,
                intent=2,
            )

            # Switch to Status state
            packet_io.set_state("Login")

            # Send Status Request (packet_id=0x00)
            packet_io.send(packet_id="0x00", name="cry2003_bot")

            # Read server response
            response = packet_io.read() 
            print("Server Response:", response)

    except ConnectionRefusedError:
        print(f"Could not connect to {host}:{port}")
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
