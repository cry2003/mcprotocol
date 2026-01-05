# src/codec/packets/registry.py

from .clientbound.status.status_response import StatusResponse
from .clientbound.status.pong_response import PongResponse
# from .serverbound.handshaking.serverbound_handshake import Handshake

CLIENTBOUND_REGISTRY = {
    0x00: StatusResponse,
    0x01: PongResponse,
}

SERVERBOUND_REGISTRY = {
    # 0x00: Handshake,
}
