# Developer Guide: Consuming Parsed Packets

Future IDS processing modules (Flow Generator, Feature Extractor, Threat Detector) consume parsed packets directly from the `PacketQueue`:

```python
from agent.capture.capture_engine import CaptureEngine

engine = CaptureEngine()
engine.start()

# Downstream consumer loop
async def process_packets():
    while True:
        parsed_packet = await engine.queue.get()
        print(f"Captured {parsed_packet.protocol} packet from {parsed_packet.ip_header.src_ip}")
```
