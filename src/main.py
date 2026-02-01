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
    host = "mc.hypixel.net"
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

            # Receive and set compression from Login Compression packet
            login_compression = packet_io.read()
            print("Login Compression:", login_compression)
            packet_io.set_compression_threshold(login_compression.threshold.value)
            
            # Read Login Finished packet
            login_finished = packet_io.read()
            print("Login Success:", login_finished)
            

    except ConnectionRefusedError:
        print(f"Could not connect to {host}:{port}")
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
