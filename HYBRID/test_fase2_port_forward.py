"""
Test Suite Fase 2 (Tahap 2): Policy Engine & Safety Guard for Port Forwarding
Verifies validation rules (INV-NAT-02 single host IP, INV-NAT-03 anti-lockout 8728/8291),
smart defaults, and policy generation for add_port_forward and remove_port_forward.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from policy_engine import build_network_policy, execute_policy
from test_fase1_port_forward import MockAPI, MikroTikAdapter


def test_port_forward_policy():
    print("Running Port Forwarding Policy & Safety Guard Tests (Fase 2)...")

    # 1. Valid add_port_forward
    pol1 = build_network_policy(
        intent="add_port_forward",
        target="192.168.88.50",
        dst_port=8080,
        to_port=80,
        protocol="tcp",
    )
    assert pol1["is_valid"] is True, f"Policy 1 must be valid: {pol1.get('error')}"
    assert pol1["dst_port"] == 8080
    assert pol1["to_port"] == 80
    assert pol1["target"] == "192.168.88.50"
    print(" [PASS] Valid policy generation: 8080 -> 192.168.88.50:80 (tcp)")

    # 2. Smart default: to_port defaults to dst_port if not specified
    pol2 = build_network_policy(
        intent="add_port_forward",
        target="192.168.88.99",
        dst_port=2222,
        protocol="tcp",
    )
    assert pol2["is_valid"] is True
    assert pol2["to_port"] == 2222
    print(" [PASS] Smart default: internal port equals external port (2222)")

    # 3. INV-NAT-02: Rejection of subnet CIDR as internal target
    pol3 = build_network_policy(
        intent="add_port_forward",
        target="192.168.88.0/24",
        dst_port=8080,
    )
    assert pol3["is_valid"] is False
    assert "INV-NAT-02" in pol3["error"]
    print(" [PASS] INV-NAT-02 Guard: Rejection of subnet CIDR (/24) as target")

    # 4. INV-NAT-03: Anti-lockout protection for API port 8728
    pol4 = build_network_policy(
        intent="add_port_forward",
        target="192.168.88.50",
        dst_port=8728,
    )
    assert pol4["is_valid"] is False
    assert "8728" in pol4["error"]
    print(" [PASS] INV-NAT-03 Guard: Anti-lockout rejection for API port 8728")

    # 5. INV-NAT-03: Anti-lockout protection for Winbox port 8291
    pol5 = build_network_policy(
        intent="add_port_forward",
        target="192.168.88.50",
        dst_port=8291,
    )
    assert pol5["is_valid"] is False
    assert "8291" in pol5["error"]
    print(" [PASS] INV-NAT-03 Guard: Anti-lockout rejection for Winbox port 8291")

    # 6. Rejection of invalid port > 65535
    pol6 = build_network_policy(
        intent="add_port_forward",
        target="192.168.88.50",
        dst_port=70000,
    )
    assert pol6["is_valid"] is False
    print(" [PASS] Port boundary check: Rejection of port 70000")

    # 7. Valid remove_port_forward
    pol7 = build_network_policy(
        intent="remove_port_forward",
        dst_port=8080,
    )
    assert pol7["is_valid"] is True
    assert pol7["dst_port"] == 8080
    print(" [PASS] Valid remove_port_forward policy for port 8080")

    # 8. Execution test with MockAdapter
    adapter = MikroTikAdapter(host="192.168.88.1")
    adapter.api = MockAPI()  # type: ignore

    exec_res1 = execute_policy(pol1, adapter)
    assert exec_res1["status"] == "success"
    assert exec_res1["result"]["action"] == "added"
    print(" [PASS] Execution test: add_port_forward executed successfully")

    exec_res2 = execute_policy(pol7, adapter)
    assert exec_res2["status"] == "success"
    assert exec_res2["result"]["action"] == "removed"
    print(" [PASS] Execution test: remove_port_forward executed successfully")

    print("\nALL 8/8 POLICY & SAFETY GUARD TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_port_forward_policy()
