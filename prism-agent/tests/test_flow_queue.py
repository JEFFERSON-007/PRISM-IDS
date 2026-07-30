"""Unit tests for FlowQueue output buffer."""

import pytest
from agent.flow.flow_models import Flow
from agent.flow.flow_queue import FlowQueue


@pytest.mark.asyncio
async def test_flow_queue_push_and_pop() -> None:
    """Test pushing and popping completed flows."""
    fq = FlowQueue(maxsize=5)
    assert fq.size == 0

    flow = Flow(src_ip="1.1.1.1", dst_ip="2.2.2.2", src_port=80, dst_port=443, protocol="TCP")
    pushed = fq.push_nowait(flow)
    assert pushed is True
    assert fq.size == 1

    popped = await fq.get()
    assert popped.flow_id == flow.flow_id
    assert fq.size == 0
