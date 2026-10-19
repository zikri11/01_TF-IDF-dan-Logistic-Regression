"""
Test Suite Fase 1 (Tahap 2): Port Forwarding (Destination NAT) Driver API
Verifies add_port_forward and remove_port_forward idempotency, input validation,
and rule mutations using a mock RouterOS API.
"""

from typing import Any, Dict, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mikrotik_adapter import MikroTikAdapter


class MockPath:
    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records
        self._next_id = len(records) + 1

    def __iter__(self):
        return iter([dict(r) for r in self.records])

    def add(self, **kwargs) -> str:
        new_id = f"*{self._next_id}"
        self._next_id += 1
        item = {".id": new_id, **kwargs}
        self.records.append(item)
        return new_id

    def remove(self, item_id: str) -> None:
        idx = next((i for i, r in enumerate(self.records) if r.get(".id") == item_id), -1)
        if idx != -1:
            self.records.pop(idx)

    def update(self, **kwargs) -> None:
        item_id = kwargs.get(".id")
        for r in self.records:
            if r.get(".id") == item_id:
                for k, v in kwargs.items():
                    if k != ".id":
                        r[k] = v


class MockAPI:
    def __init__(self):
        self.nat_records: List[Dict[str, Any]] = [
            # Default masquerade rule
            {".id": "*0", "chain": "srcnat", "action": "masquerade", "out-interface": "ether1", "comment": "defconf"},
        ]

    def path(self, *parts: str) -> Any:
        if parts == ("ip", "firewall", "nat"):
            return MockPath(self.nat_records)
        raise ValueError(f"Unknown path: {parts}")


def test_port_forward_driver():
    adapter = MikroTikAdapter(host="192.168.88.1")
    adapter.api = MockAPI()  # type: ignore

    print("Running Port Forwarding Driver Tests (Fase 1)...")

    # 1. Validation checks
    try:
        adapter.add_port_forward(dst_port=70000, to_address="192.168.88.50")
        assert False, "Should fail on invalid port > 65535"
    except ValueError:
        pass

    try:
        adapter.add_port_forward(dst_port=8080, to_address="")
        assert False, "Should fail on empty to_address"
    except ValueError:
        pass

    # 2. Add port forward (8080 -> 192.168.88.50:80)
    res1 = adapter.add_port_forward(
        dst_port=8080, to_address="192.168.88.50", to_port=80, protocol="tcp"
    )
    assert res1["action"] == "added", f"Expected added, got {res1['action']}"
    assert res1["dst_port"] == 8080
    assert res1["to_port"] == 80
    print(" [PASS] Add new port forward 8080 -> 192.168.88.50:80")

    # 3. Idempotent check (same call should be noop)
    res2 = adapter.add_port_forward(
        dst_port=8080, to_address="192.168.88.50", to_port=80, protocol="tcp"
    )
    assert res2["action"] == "noop", f"Expected noop, got {res2['action']}"
    print(" [PASS] Idempotent add: action=noop")

    # 4. Update check (change target port to 8081)
    res3 = adapter.add_port_forward(
        dst_port=8080, to_address="192.168.88.50", to_port=8081, protocol="tcp"
    )
    assert res3["action"] == "updated", f"Expected updated, got {res3['action']}"
    assert res3["to_port"] == 8081
    print(" [PASS] Update existing port forward to target port 8081")

    # 5. Add second port forward (2222 -> 192.168.88.99:22)
    res4 = adapter.add_port_forward(
        dst_port=2222, to_address="192.168.88.99", to_port=22, protocol="tcp"
    )
    assert res4["action"] == "added"
    print(" [PASS] Add second port forward 2222 -> 192.168.88.99:22")

    # 6. Remove specific port forward (8080)
    del1 = adapter.remove_port_forward(dst_port=8080)
    assert del1["action"] == "removed"
    assert del1["count"] == 1
    print(" [PASS] Remove specific port forward 8080")

    # 7. Bulk remove remaining IBN port forwards
    del2 = adapter.remove_port_forward(dst_port="all")
    assert del2["action"] == "removed"
    assert del2["count"] == 1  # 2222 rule remaining
    print(" [PASS] Bulk remove remaining IBN port forward rules")

    print("\nALL 7/7 TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_port_forward_driver()
