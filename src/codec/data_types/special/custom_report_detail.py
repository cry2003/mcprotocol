# src/codec/data_types/special/custom_report_detail.py

from dataclasses import dataclass

from codec.data_types.data_type import DataType
from codec.data_types.primitives.string import String


@dataclass(slots=True, frozen=True)
class CustomReportDetail(DataType):
    """
    One custom report detail entry.

    Fields:
        title (String): Entry title, max 128 characters.
        description (String): Entry description, max 4096 characters.
    """

    title: String
    description: String

    def __post_init__(self) -> None:
        if not isinstance(self.title, String):
            raise TypeError("CustomReportDetail.title must be a String")
        if not isinstance(self.description, String):
            raise TypeError("CustomReportDetail.description must be a String")

        if len(self.title.value) > 128:
            raise ValueError(
                f"CustomReportDetail title too long: {len(self.title.value)} (max 128)"
            )
        if len(self.description.value) > 4096:
            raise ValueError(
                "CustomReportDetail description too long: "
                f"{len(self.description.value)} (max 4096)"
            )

    def __bytes__(self) -> bytes:
        return bytes(self.title) + bytes(self.description)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["CustomReportDetail", int]:
        offset = 0

        title, consumed = String.from_bytes(data[offset:])
        offset += consumed

        description, consumed = String.from_bytes(data[offset:])
        offset += consumed

        return cls(title=title, description=description), offset
