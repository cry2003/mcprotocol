# src/codec/packets/packet_registry.py

import sys
import os
import json
import importlib


class PacketRegistry:
    """
    Helper class to manage packet registry and dynamic instantiation of packets.

    Usage:
        registry = PacketRegistry("path/to/packets_registry.json")
        # Serverbound packet
        packet = registry.instantiate(
            "Handshaking",
            "serverbound",
            "0x00",
            protocol_version=754,
            server_address="localhost",
            server_port=25565,
            intent=1
        )
        # Clientbound packet
        packet = registry.instantiate(
            "Status",
            "clientbound",
            "0x01",
            data=raw_bytes
        )
    """

    def __init__(self, registry_path: str):
        # Ensure 'src' is in sys.path to allow import of codec modules
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        )

        # Load the JSON registry
        with open(registry_path, "r") as f:
            self._registry = json.load(f)

    def get_class(self, state: str, direction: str, packet_id: str):
        """
        Return the class object for a given state, direction, and packet_id.
        """
        try:
            full_path = self._registry[state][direction][packet_id]
        except KeyError:
            raise ValueError(f"No packet found for {state}.{direction}.{packet_id}")

        module_path, class_name = full_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls

    def instantiate(
        self,
        state: str,
        direction: str,
        packet_id: str,
        *args,
        data: bytes = None,
        **kwargs,
    ):
        """
        Create an instance of the packet class.

        - Serverbound: pass constructor arguments via *args or **kwargs.
        - Clientbound: pass raw bytes as 'data'.
        """
        cls = self.get_class(state, direction, packet_id)

        if data is not None:
            # Clientbound: construct from raw bytes
            return cls(data)
        # Serverbound: construct using args and keyword arguments
        return cls(*args, **kwargs)


# --- Usage example ---
if __name__ == "__main__":
    # Path to the JSON registry (robust, relative to this file)
    registry_path = os.path.join(os.path.dirname(__file__), "packets_registry.json")

    registry = PacketRegistry(registry_path)

    # Example: instantiate Handshaking packet (serverbound)
    instance = registry.instantiate(
        "Handshaking",
        "serverbound",
        "0x00",
        protocol_version=754,
        server_address="localhost",
        server_port=25565,
        intent=1,
    )

    print(f"Created instance of: {type(instance)}, instance: {instance}")
