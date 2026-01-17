# src\codec\packets\registry.py

import sys
import os
import json
import importlib


class PacketRegistry:
    """Resolves and instantiates packet classes."""

    def __init__(self):
        """
        Load packet registry from JSON configuration.
        """
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        )

        with open(
            os.path.join(os.path.dirname(__file__), "packets_registry.json"),
            "r",
        ) as f:
            self._registry = json.load(f)

    def get_class(self, state: str, direction: str, packet_id: str):
        """
        Resolve a packet class.

        Args:
            state: Protocol state.
            direction: Packet direction.
            packet_id: Packet identifier.

        Returns:
            Packet class.

        Raises:
            ValueError: If no packet matches the parameters.
        """
        try:
            full_path = self._registry[state][direction][packet_id]
        except KeyError:
            raise ValueError(f"No packet found for {state}.{direction}.{packet_id}")

        module_path, class_name = full_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

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
        Instantiate a packet.

        Args:
            state: Protocol state.
            direction: Packet direction.
            packet_id: Packet identifier.
            *args: Positional constructor arguments.
            data: Raw payload for clientbound packets.
            **kwargs: Keyword constructor arguments.

        Returns:
            Packet instance.
        """
        cls = self.get_class(state, direction, packet_id)

        if data is not None:
            return cls(data)

        return cls(*args, **kwargs)
