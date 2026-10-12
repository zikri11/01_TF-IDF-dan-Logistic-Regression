from mikrotik_adapter import MikroTikAdapter

DUMMY_IP = "192.168.88.250"
QUEUE_NAME = "ibn_test_qos"

def run_tests():
    with MikroTikAdapter() as adapter:
        print("[1/7] Testing connection...")
        assert adapter.api is not None, "Gagal terhubung ke RouterOS"
        print("      OK: Terhubung ke router.")

        print("[2/7] Pre-cleanup dummy rules...")
        adapter.remove_bandwidth_limit(DUMMY_IP)
        adapter.remove_firewall_block(DUMMY_IP)
        print("      OK: Bersih.")

        print("[3/7] Testing QoS: Add bandwidth limit...")
        res_add = adapter.apply_bandwidth_limit(QUEUE_NAME, DUMMY_IP, "2M/2M")
        assert res_add["action"] == "added", f"Expected 'added', got {res_add}"
        limits = adapter.get_bandwidth_limits()
        assert any(r.get("name") == QUEUE_NAME for r in limits), "Queue tidak ditemukan di router"
        print(f"      OK: Queue ditambahkan (id={res_add['id']}).")

        print("[4/7] Testing QoS: Idempotent update limit...")
        res_update = adapter.apply_bandwidth_limit(QUEUE_NAME, DUMMY_IP, "4M/4M")
        assert res_update["action"] == "updated", f"Expected 'updated', got {res_update}"
        limits = [r for r in adapter.get_bandwidth_limits() if r.get("name") == QUEUE_NAME]
        assert len(limits) == 1, f"Duplikasi queue terdeteksi! Total: {len(limits)}"
        print(f"      OK: Queue diperbarui secara idempoten (id={res_update['id']}).")

        print("[5/7] Testing Firewall: Add block rule...")
        res_block = adapter.apply_firewall_block(DUMMY_IP)
        assert res_block["action"] == "added", f"Expected 'added', got {res_block}"
        blocks = adapter.get_firewall_blocks()
        assert any(r.get("src-address", "").split("/")[0] == DUMMY_IP for r in blocks), "Rule block tidak ditemukan"
        print(f"      OK: Drop rule ditambahkan (id={res_block['id']}).")

        print("[6/7] Testing Firewall: Idempotent block check & Anti-lockout...")
        res_block_idempotent = adapter.apply_firewall_block(DUMMY_IP)
        assert res_block_idempotent["action"] == "noop", f"Expected 'noop', got {res_block_idempotent}"
        matching_blocks = [r for r in adapter.get_firewall_blocks() if r.get("src-address", "").split("/")[0] == DUMMY_IP]
        assert len(matching_blocks) == 1, f"Duplikasi rule drop terdeteksi! Total: {len(matching_blocks)}"

        # Anti-lockout test
        try:
            adapter.apply_firewall_block("192.168.88.1")
            assert False, "Anti-lockout gagal: Router IP diizinkan untuk diblokir!"
        except ValueError:
            pass
        print("      OK: Idempotensi filter & proteksi anti-lockout valid.")

        print("[7/7] Testing Cleanup: Remove dummy rules...")
        q_removed = adapter.remove_bandwidth_limit(DUMMY_IP)
        fw_removed = adapter.remove_firewall_block(DUMMY_IP)
        assert q_removed >= 1, "Gagal menghapus queue"
        assert fw_removed >= 1, "Gagal menghapus firewall block"

        remaining_q = [r for r in adapter.get_bandwidth_limits() if r.get("name") == QUEUE_NAME]
        remaining_fw = [r for r in adapter.get_firewall_blocks() if r.get("src-address", "").split("/")[0] == DUMMY_IP]
        assert len(remaining_q) == 0, "Sisa queue masih ada"
        assert len(remaining_fw) == 0, "Sisa firewall block masih ada"
        print("      OK: Semua rule pengujian berhasil dibersihkan.")

    print("\nSEMUA PENGUJIAN FASE 1 SUKSES 100%!")

if __name__ == "__main__":
    run_tests()
