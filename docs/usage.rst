Using the decoder
=================

Run Python from the project root to make the package importable.

.. code-block:: python

   from ecoadapt_exporter.decoder import DataType, decode_registers

   number = decode_registers([0x0001, 0x0002], DataType.UINT32)
   assert number == 65538

   temperature = decode_registers([0x3F80, 0x0000], DataType.FLOAT32)
   assert temperature == 1.0

Supported types
---------------

.. list-table::
   :header-rows: 1

   * - DataType member
     - Register count
     - Python result
   * - UINT16 / INT16
     - 1
     - int
   * - UINT32 / INT32
     - 2
     - int
   * - FLOAT32
     - 2
     - float
   * - FLOAT64
     - 4
     - float

Ordering and validation
-----------------------

Defaults are ``ByteOrder.MSB_FIRST`` and ``WordOrder.MSW_FIRST``.
``WordOrder.LSW_FIRST`` reverses the register sequence before packing.
``ByteOrder`` controls both the byte order used to pack each register and the
endianness used to unpack the complete value. These describe the current
implementation; check device-specific examples when selecting non-default
combinations.

An incorrect register count, a non-integer register, or a register outside
0 through 65535 raises ``ValueError``. Pass ``DataType``, ``ByteOrder``, and
``WordOrder`` members for their respective arguments.
