EcoAdapt Exporter
=================

From sensor registers to WebSocket measurements
-----------------------------------------------

This proof of concept reads an Eco-Adapt device over Modbus TCP, decodes
registers into typed measurements, and sends JSON messages to a WebSocket
receiver. The application selects RMS voltage and frequency on connector 1,
channel 1. Device metadata can also be queried through the Python API.

.. container:: overview-grid

   .. container:: overview-card

      **Run the project**

      Set up Python 3.7, start the receiver, and configure the exporter.

      :doc:`Read the usage guide <usage>`

   .. container:: overview-card

      **Explore the API**

      Browse device access, registers, decoding, sending, and orchestration.

      :doc:`Browse the Python API <api>`

   .. container:: overview-card

      **Understand the design**

      Follow dependencies, startup callbacks, measurement flow, and shutdown.

      :doc:`View the architecture <architecture>`

Start without hardware
----------------------

The unit tests inject fake transports, devices, and senders. The integration
smoke test combines fake Modbus data with a real local WebSocket connection.
See :doc:`testing` for what each test actually verifies.

Documentation scope
-------------------

:doc:`project` maps every source, development, test, and configuration file to
its role. Public package APIs use Sphinx docstrings; script sources are shown
without importing scripts that start networking as a side effect.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   usage
   architecture
   testing
   project

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   scripts

.. toctree::
   :hidden:
   :caption: Browse

   genindex
