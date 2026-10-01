EcoAdapt Exporter
=================

From device registers to Python values
--------------------------------------

Decode 16-bit registers into integers and floating-point values, with
configurable byte and word ordering.

.. container:: overview-grid

   .. container:: overview-card

      **Start here**

      Decode your first value and understand supported formats.

      :doc:`Read the usage guide <usage>`

   .. container:: overview-card

      **Explore the API**

      Browse the decoder function and its configuration enums.

      :doc:`Browse the Python API <api>`

   .. container:: overview-card

      **Understand the design**

      Follow registers through validation, packing, and decoding.

      :doc:`View the architecture <architecture>`

Quick example
-------------

.. code-block:: python

   from ecoadapt_exporter.decoder import DataType, decode_registers

   value = decode_registers([0x3F80, 0x0000], DataType.FLOAT32)
   print(value)  # 1.0

Project at a glance
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Component
     - Responsibility
   * - :doc:`decoder module <api>`
     - Convert register sequences into Python numbers.
   * - :doc:`decode_registers <api/decode_registers>`
     - Validate, order, pack, and decode register values.
   * - Configuration enums
     - Select the :doc:`numeric type <api/data_type>`,
       :doc:`byte order <api/byte_order>`, and :doc:`word order <api/word_order>`.

.. toctree::
   :hidden:
   :caption: Guides

   usage
   architecture

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Reference

   api

.. toctree::
   :hidden:
   :caption: Browse

   genindex
