"""Unit tests for InterfaceManager."""

from agent.capture.interface_manager import InterfaceManager


def test_list_interfaces() -> None:
    """Test interface listing returns non-empty list."""
    ifaces = InterfaceManager.list_interfaces()
    assert isinstance(ifaces, list)
    assert len(ifaces) > 0
    assert "name" in ifaces[0]
    assert "ip_address" in ifaces[0]


def test_select_best_interface() -> None:
    """Test best interface selection."""
    iface = InterfaceManager.select_best_interface()
    assert isinstance(iface, str)
    assert len(iface) > 0
