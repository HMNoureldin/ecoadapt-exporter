import pytest

from ecoadapt_exporter.decoder import (
    ByteOrder,
    DataType,
    WordOrder,
    decode_registers,
)

def test_decode_pe6_float32_lsw_first():
    registers = [49709, 17262]

    result = decode_registers(
        registers=registers,
        data_type=DataType.FLOAT32,
        byte_order=ByteOrder.MSB_FIRST,
        word_order=WordOrder.LSW_FIRST,
    )

    assert result == pytest.approx(238.7585, abs=0.001)
