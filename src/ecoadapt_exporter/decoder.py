"""Decode numeric Modbus values independently of device access and networking."""

import struct
from enum import Enum


class ByteOrder(Enum):
    """Byte significance within each 16-bit register.
    """
    MSB_FIRST = "big"
    LSB_FIRST = "little"


class WordOrder(Enum):
    """Word significance across a multi-register value.
    """
    MSW_FIRST = "msw"
    LSW_FIRST = "lsw"


class DataType(Enum):
    """Supported signed, unsigned, and IEEE floating-point numeric formats.
    """
    UINT16 = "uint16"
    INT16 = "int16"
    UINT32 = "uint32"
    INT32 = "int32"
    FLOAT32 = "float32"
    FLOAT64 = "float64"


_STRUCT_FORMATS = {
    DataType.UINT16: "H",
    DataType.INT16: "h",
    DataType.UINT32: "I",
    DataType.INT32: "i",
    DataType.FLOAT32: "f",
    DataType.FLOAT64: "d",
}


_REGISTER_COUNTS = {
    DataType.UINT16: 1,
    DataType.INT16: 1,
    DataType.UINT32: 2,
    DataType.INT32: 2,
    DataType.FLOAT32: 2,
    DataType.FLOAT64: 4,
}


def decode_registers(
    registers,
    data_type,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.MSW_FIRST,
):
    """Decode a register sequence without modifying the input.

    :param registers: Iterable of unsigned 16-bit integer register values.
    :param data_type: A :class:`DataType` selecting format and register count.
    :param byte_order: Byte significance within each register.
    :param word_order: Word significance across the register sequence.
    :returns: An integer or float, according to ``data_type``.
    :raises ValueError: If the type, register count, or register values are invalid.

    UINT16 and INT16 require one register; UINT32, INT32, and FLOAT32 require
    two; FLOAT64 requires four. Words and bytes are normalized before a
    big-endian unpack. Pass enum members for ordering arguments.
    """
    words = list(registers)

    _validate_registers(words, data_type)

    # Normalize the word order.
    #
    # For example, a FLOAT32 consists of two 16-bit words:
    #
    #     MSW | LSW
    #
    # If the device sends LSW first, reverse the words so that
    # they are in their canonical MSW-first order.
    if word_order == WordOrder.LSW_FIRST:
        words.reverse()

    normalized_bytes = []

    for word in words:
        # Convert the 16-bit register into two bytes.
        #
        # Start from big-endian because this gives us the bytes
        # in most-significant-byte-first order.
        word_bytes = word.to_bytes(
            2,
            byteorder="big",
            signed=False,
        )

        # If the device uses least-significant-byte-first order,
        # swap the two bytes inside this 16-bit word.
        if byte_order == ByteOrder.LSB_FIRST:
            word_bytes = word_bytes[::-1]

        normalized_bytes.append(word_bytes)

    raw_bytes = b"".join(normalized_bytes)

    format_char = _STRUCT_FORMATS[data_type]

    # At this point the bytes have been normalized into
    # most-significant-first order, so decode them as big-endian.
    return struct.unpack(
        ">" + format_char,
        raw_bytes,
    )[0]


def decode_uint8_pair(
    register,
    byte_order=ByteOrder.MSB_FIRST,
):
    """Split one register into two unsigned bytes in the requested order.

    :param register: Integer from 0 through 65535.
    :param byte_order: Which byte to return first; defaults to MSB first.
    :returns: A pair of integers; ``0x0106`` gives ``(1, 6)`` with MSB first.
    :raises ValueError: If the register is not an unsigned 16-bit integer.
    """
    _validate_register_value(register)

    most_significant_byte = (register >> 8) & 0xFF
    least_significant_byte = register & 0xFF

    if byte_order == ByteOrder.MSB_FIRST:
        return most_significant_byte, least_significant_byte

    return least_significant_byte, most_significant_byte


def _validate_registers(registers, data_type):
    """
    Validate the number and values of registers before decoding.
    """
    if data_type not in _REGISTER_COUNTS:
        raise ValueError(
            "Unsupported data type: {}".format(data_type)
        )

    expected_count = _REGISTER_COUNTS[data_type]

    if len(registers) != expected_count:
        raise ValueError(
            "{} requires {} register(s), got {}".format(
                data_type.value,
                expected_count,
                len(registers),
            )
        )

    for register in registers:
        _validate_register_value(register)


def _validate_register_value(register):
    """
    Validate a single 16-bit Modbus register value.
    """
    if not isinstance(register, int):
        raise ValueError(
            "Register values must be integers"
        )

    if not 0 <= register <= 0xFFFF:
        raise ValueError(
            "Register value must be between 0 and 65535, got {}".format(
                register
            )
        )