import struct
from enum import Enum


class ByteOrder(Enum):
    MSB_FIRST = "big"
    LSB_FIRST = "little"


class WordOrder(Enum):
    MSW_FIRST = "msw"
    LSW_FIRST = "lsw"


class DataType(Enum):
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
    """
    Decode one or more 16-bit Modbus registers into a Python value.

    The number of registers required depends on the data type.

    Examples:
        UINT16  -> 1 register
        FLOAT32 -> 2 registers
        FLOAT64 -> 4 registers
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
    """
    Split one 16-bit register into two unsigned 8-bit values.

    Example:

        0x0106 -> (1, 6)

    when byte_order is MSB_FIRST.
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