import librouteros
from typing import Optional, Union
from config import ROUTER_HOST, ROUTER_PORT, ROUTER_USER, ROUTER_PASS, ROUTER_TIMEOUT

MANAGEMENT_INTERFACES = {'ether2', 'bridge'}
MANAGEMENT_IPS = {'192.168.88.1', '192.168.88.1/24'}


class MikroTikAdapter:
    def __init__(self, host=ROUTER_HOST, port=ROUTER_PORT, user=ROUTER_USER, password=ROUTER_PASS, timeout=ROUTER_TIMEOUT):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.api = None

    def connect(self):
        if not self.api:
            self.api = librouteros.connect(
                host=self.host,
                username=self.user,
                password=self.password,
                port=self.port,
                timeout=self.timeout
            )
        return self.api

    def close(self):
        if self.api:
            try:
                self.api.close()
            except Exception:
                pass
            self.api = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # QoS Domain (/queue/simple)
    def apply_bandwidth_limit(self, name: str, target: str, max_limit: str) -> dict:
        self.connect()
        q = self.api.path('queue', 'simple')
        target_clean = target.split('/')[0]
        existing = next(
            (r for r in q if r.get('target', '').split('/')[0] == target_clean or r.get('target') == target or r.get('name') == name),
            None
        )
        if existing:
            q.update(**{'.id': existing['.id'], 'name': name, 'target': target, 'max-limit': max_limit})
            return {'action': 'updated', 'id': existing['.id'], 'name': name, 'target': target, 'max_limit': max_limit}
        new_id = q.add(name=name, target=target, **{'max-limit': max_limit})
        return {'action': 'added', 'id': new_id, 'name': name, 'target': target, 'max_limit': max_limit}

    def remove_bandwidth_limit(self, target: str) -> int:
        self.connect()
        q = self.api.path('queue', 'simple')
        if str(target).lower() in ("all", "semua", "seluruh"):
            matches = [
                r for r in q
                if 'IBN' in str(r.get('comment', '')) or str(r.get('name', '')).startswith('qos_')
            ]
        else:
            target_clean = target.split('/')[0]
            matches = [
                r for r in q
                if r.get('target', '').split('/')[0] == target_clean
                or r.get('target') == target
                or r.get('name') == target
                or r.get('name') == f"qos_{target}"
            ]
        for m in matches:
            q.remove(m['.id'])
        return len(matches)

    def get_bandwidth_limits(self) -> list:
        self.connect()
        return list(self.api.path('queue', 'simple'))

    # Firewall Domain (/ip/firewall/filter)
    def apply_firewall_block(
        self,
        target: Optional[str] = None,
        dst_port: Optional[Union[str, int]] = None,
        protocol: str = 'tcp',
        site: Optional[str] = None,
        comment: str = 'IBN_DROP'
    ) -> dict:
        if not target and dst_port is None and not site:
            raise ValueError("Target IP, dst_port, atau nama situs wajib diisi")

        target_ip = target.split('/')[0] if target and not site else None
        if target_ip and target_ip in ('192.168.88.1', self.host):
            raise ValueError(f"Anti-lockout: dilarang memblokir IP router/gateway ({target_ip})")

        port_str = str(dst_port) if dst_port is not None else ('443' if site else None)
        proto_str = protocol.lower() if protocol else 'tcp'
        rule_comment = comment if comment != 'IBN_DROP' else (f'IBN_BLOCK_{site.upper()}' if site else 'IBN_DROP')

        self.connect()
        fw = self.api.path('ip', 'firewall', 'filter')

        def _match_existing(r):
            if r.get('chain') != 'forward' or r.get('action') != 'drop':
                return False
            if site:
                return r.get('tls-host') == f"*{site}*" or site.lower() in str(r.get('comment', '')).lower()

            r_src = r.get('src-address', '').split('/')[0] if r.get('src-address') else None
            r_port = str(r['dst-port']) if 'dst-port' in r else None

            if target_ip:
                if r_src != target_ip:
                    return False
            else:
                if r_src is not None:
                    return False

            if port_str is not None:
                if r_port != port_str:
                    return False
                if r.get('protocol', '').lower() != proto_str:
                    return False
            else:
                if r_port is not None:
                    return False
            return True

        existing = next((r for r in fw if _match_existing(r)), None)
        if existing:
            return {
                'action': 'noop',
                'id': existing['.id'],
                'target': target or site,
                'dst_port': dst_port or ('443' if site else None),
                'protocol': proto_str,
                'comment': existing.get('comment', ''),
            }

        params = {'chain': 'forward', 'action': 'drop', 'comment': rule_comment}
        if site:
            params['protocol'] = 'tcp'
            params['dst-port'] = '443'
            params['tls-host'] = f"*{site}*"
        else:
            if target:
                params['src-address'] = target
            if dst_port is not None:
                params['protocol'] = proto_str
                params['dst-port'] = port_str

        new_id = fw.add(**params)
        return {
            'action': 'added',
            'id': new_id,
            'target': target or site,
            'dst_port': dst_port or ('443' if site else None),
            'protocol': proto_str,
            'comment': rule_comment,
        }

    def remove_firewall_block(
        self,
        target: Optional[str] = None,
        dst_port: Optional[Union[str, int]] = None,
        site: Optional[str] = None,
        comment: Optional[str] = None
    ) -> int:
        self.connect()
        fw = self.api.path('ip', 'firewall', 'filter')
        target_str = str(target).lower() if target else ""

        if target_str in ("all", "semua", "seluruh"):
            matches = [
                r for r in fw
                if r.get('chain') == 'forward' and r.get('action') == 'drop' and (
                    'IBN' in str(r.get('comment', '')) or 'IBN' in str(r.get('tls-host', ''))
                )
            ]
            for m in matches:
                fw.remove(m['.id'])
            return len(matches)

        target_ip = target.split('/')[0] if target and not site else None
        port_str = str(dst_port) if dst_port is not None else None

        matches = []
        for r in fw:
            if r.get('chain') != 'forward' or r.get('action') != 'drop':
                continue
            if site:
                if site.lower() in str(r.get('tls-host', '')).lower() or site.lower() in str(r.get('comment', '')).lower():
                    matches.append(r)
                continue

            r_src = r.get('src-address', '').split('/')[0] if r.get('src-address') else None
            r_port = str(r['dst-port']) if 'dst-port' in r else None

            hit = False
            if target_ip and port_str:
                if r_src == target_ip and r_port == port_str:
                    hit = True
            elif target_ip:
                if r_src == target_ip:
                    hit = True
            elif port_str:
                if r_port == port_str:
                    hit = True
            elif comment:
                if r.get('comment') == comment:
                    hit = True

            if hit:
                matches.append(r)

        for m in matches:
            fw.remove(m['.id'])
        return len(matches)

    def get_firewall_blocks(self) -> list:
        self.connect()
        fw = self.api.path('ip', 'firewall', 'filter')
        return [
            r for r in fw
            if r.get('chain') == 'forward' and r.get('action') == 'drop' and (
                'src-address' in r or 'dst-port' in r or r.get('comment') == 'IBN_DROP'
            )
        ]

    # Interface Domain (/interface)
    def get_interface_states(self) -> list:
        self.connect()
        return list(self.api.path('interface'))

    def enable_interface(self, name: str) -> dict:
        self.connect()
        ifaces = self.api.path('interface')
        target = next((i for i in ifaces if i.get('name') == name), None)
        if not target:
            raise ValueError(f"Interface '{name}' tidak ditemukan")
        if not target.get('disabled', False):
            return {'action': 'noop', 'id': target['.id'], 'name': name, 'disabled': False}
        ifaces.update(**{'.id': target['.id'], 'disabled': False})
        return {'action': 'enabled', 'id': target['.id'], 'name': name, 'disabled': False}

    def disable_interface(self, name: str) -> dict:
        if name in MANAGEMENT_INTERFACES:
            raise ValueError("Anti-lockout: Dilarang mematikan interface manajemen (ether2 / bridge)!")
        self.connect()
        ifaces = self.api.path('interface')
        target = next((i for i in ifaces if i.get('name') == name), None)
        if not target:
            raise ValueError(f"Interface '{name}' tidak ditemukan")
        if target.get('disabled', False):
            return {'action': 'noop', 'id': target['.id'], 'name': name, 'disabled': True}
        ifaces.update(**{'.id': target['.id'], 'disabled': True})
        return {'action': 'disabled', 'id': target['.id'], 'name': name, 'disabled': True}

    # NAT Domain (/ip/firewall/nat)
    def get_nat_rules(self) -> list:
        self.connect()
        return list(self.api.path('ip', 'firewall', 'nat'))

    def enable_nat(self, out_interface: str = 'ether1', comment: str = 'IBN_NAT_MASQ') -> dict:
        self.connect()
        nat = self.api.path('ip', 'firewall', 'nat')
        existing = next(
            (
                r for r in nat
                if r.get('chain') == 'srcnat'
                and r.get('action') == 'masquerade'
                and (r.get('out-interface') == out_interface or (comment and r.get('comment') == comment))
            ),
            None
        )
        if existing:
            if not existing.get('disabled', False):
                return {'action': 'noop', 'id': existing['.id'], 'out_interface': out_interface, 'comment': comment}
            nat.update(**{'.id': existing['.id'], 'disabled': False})
            return {'action': 'enabled', 'id': existing['.id'], 'out_interface': out_interface, 'comment': comment}
        new_id = nat.add(chain='srcnat', action='masquerade', **{'out-interface': out_interface, 'comment': comment})
        return {'action': 'added', 'id': new_id, 'out_interface': out_interface, 'comment': comment}

    def disable_nat(self, out_interface: str = 'ether1', comment: str = 'IBN_NAT_MASQ') -> dict:
        self.connect()
        nat = self.api.path('ip', 'firewall', 'nat')
        matches = [
            r for r in nat
            if r.get('chain') == 'srcnat'
            and r.get('action') == 'masquerade'
            and ((comment and r.get('comment') == comment) or (out_interface and r.get('out-interface') == out_interface))
        ]
        for m in matches:
            nat.remove(m['.id'])
        return {'action': 'removed', 'count': len(matches)}

    def add_port_forward(
        self,
        dst_port: Union[int, str],
        to_address: str,
        to_port: Optional[Union[int, str]] = None,
        protocol: str = 'tcp',
        comment: Optional[str] = None
    ) -> dict:
        port_num = int(dst_port)
        if not (1 <= port_num <= 65535):
            raise ValueError(f"Port eksternal tidak valid: {dst_port} (harus 1-65535)")

        to_p = int(to_port) if to_port is not None else port_num
        if not (1 <= to_p <= 65535):
            raise ValueError(f"Port internal tidak valid: {to_port} (harus 1-65535)")

        proto = protocol.lower() if protocol else 'tcp'
        if proto not in ('tcp', 'udp'):
            raise ValueError(f"Protokol tidak valid: {protocol} (harus tcp atau udp)")

        to_addr_clean = to_address.split('/')[0].strip() if to_address else ''
        if not to_addr_clean:
            raise ValueError("Alamat IP internal (to_address) wajib diisi")

        rule_comment = comment or f"IBN_PORT_FWD_{port_num}"

        self.connect()
        nat = self.api.path('ip', 'firewall', 'nat')

        # ponytail: exact match on chain=dstnat, action=dst-nat, dst-port, protocol. upgrade path: multi-port range
        existing = next(
            (
                r for r in nat
                if r.get('chain') == 'dstnat'
                and r.get('action') == 'dst-nat'
                and str(r.get('dst-port')) == str(port_num)
                and r.get('protocol', 'tcp').lower() == proto
            ),
            None
        )

        if existing:
            ext_addr = str(existing.get('to-addresses', '')).strip()
            ext_port = str(existing.get('to-ports', '')).strip()
            if ext_addr == to_addr_clean and ext_port == str(to_p):
                if existing.get('disabled', False):
                    nat.update(**{'.id': existing['.id'], 'disabled': False})
                    return {
                        'action': 'enabled',
                        'id': existing['.id'],
                        'dst_port': port_num,
                        'to_address': to_addr_clean,
                        'to_port': to_p,
                        'protocol': proto,
                        'comment': rule_comment,
                    }
                return {
                    'action': 'noop',
                    'id': existing['.id'],
                    'dst_port': port_num,
                    'to_address': to_addr_clean,
                    'to_port': to_p,
                    'protocol': proto,
                    'comment': existing.get('comment', ''),
                }
            nat.update(**{
                '.id': existing['.id'],
                'to-addresses': to_addr_clean,
                'to-ports': str(to_p),
                'disabled': False,
                'comment': rule_comment,
            })
            return {
                'action': 'updated',
                'id': existing['.id'],
                'dst_port': port_num,
                'to_address': to_addr_clean,
                'to_port': to_p,
                'protocol': proto,
                'comment': rule_comment,
            }

        new_id = nat.add(
            chain='dstnat',
            action='dst-nat',
            protocol=proto,
            **{
                'dst-port': str(port_num),
                'to-addresses': to_addr_clean,
                'to-ports': str(to_p),
                'comment': rule_comment,
            }
        )
        return {
            'action': 'added',
            'id': new_id,
            'dst_port': port_num,
            'to_address': to_addr_clean,
            'to_port': to_p,
            'protocol': proto,
            'comment': rule_comment,
        }

    def remove_port_forward(
        self,
        dst_port: Optional[Union[int, str]] = None,
        to_address: Optional[str] = None,
        protocol: Optional[str] = None,
        comment: Optional[str] = None
    ) -> dict:
        self.connect()
        nat = self.api.path('ip', 'firewall', 'nat')
        port_str = str(dst_port) if dst_port is not None and str(dst_port).lower() not in ("all", "semua", "seluruh") else None
        to_clean = to_address.split('/')[0].strip() if to_address else None
        proto = protocol.lower() if protocol else None

        matches = []
        for r in nat:
            if r.get('chain') != 'dstnat' or r.get('action') != 'dst-nat':
                continue

            hit = False
            if port_str:
                if str(r.get('dst-port')) == port_str:
                    hit = (r.get('protocol', 'tcp').lower() == proto) if proto else True
            elif to_clean:
                if str(r.get('to-addresses', '')).strip() == to_clean:
                    hit = True
            elif comment:
                if r.get('comment') == comment:
                    hit = True
            elif str(dst_port).lower() in ("all", "semua", "seluruh") or not dst_port:
                if 'IBN' in str(r.get('comment', '')):
                    hit = True

            if hit:
                matches.append(r)

        for m in matches:
            nat.remove(m['.id'])

        return {'action': 'removed', 'count': len(matches), 'dst_port': dst_port}

    def _is_mgmt_ip(self, ip: Optional[str]) -> bool:
        if not ip:
            return False
        clean = ip.split('/')[0].strip()
        return clean in ('192.168.88.1', self.host) or ip.strip() in MANAGEMENT_IPS

    # IP Address Domain (/ip/address) & Telemetry
    def get_ip_addresses(self, interface: Optional[Union[str, list[str]]] = None) -> list:
        self.connect()
        records = list(self.api.path('ip', 'address'))
        if not interface:
            return records
        target_ifaces = {interface.lower()} if isinstance(interface, str) else {i.lower() for i in interface}
        return [
            r for r in records
            if r.get('interface', '').lower() in target_ifaces
            or r.get('actual-interface', '').lower() in target_ifaces
        ]

    def get_interface_telemetry(self, interfaces: Optional[Union[str, list[str]]] = None) -> list:
        self.connect()
        all_ifaces = self.get_interface_states()
        all_ips = self.get_ip_addresses()

        if interfaces:
            target_names = {interfaces.lower()} if isinstance(interfaces, str) else {i.lower() for i in interfaces}
            selected_ifaces = [
                i for i in all_ifaces
                if i.get('name', '').lower() in target_names
                or i.get('default-name', '').lower() in target_names
            ]
        else:
            selected_ifaces = all_ifaces

        telemetry = []
        for iface in selected_ifaces:
            name = iface.get('name', '')
            name_lower = name.lower()
            ips = [
                r['address']
                for r in all_ips
                if (r.get('interface', '').lower() == name_lower or r.get('actual-interface', '').lower() == name_lower)
                and 'address' in r
            ]
            telemetry.append({
                'name': name,
                'type': iface.get('type', ''),
                'mac': iface.get('mac-address', ''),
                'disabled': bool(iface.get('disabled', False)),
                'running': bool(iface.get('running', False)),
                'ips': ips,
            })
        return telemetry

    def add_ip_address(self, address: str, interface: str, comment: str = 'IBN_IP') -> dict:
        if self._is_mgmt_ip(address):
            raise ValueError(f"Anti-lockout: Dilarang mengubah IP manajemen ({address})")

        self.connect()
        ip_path = self.api.path('ip', 'address')
        addr_clean = address.split('/')[0].strip()

        existing = next(
            (r for r in ip_path if r.get('address') == address or r.get('address', '').split('/')[0].strip() == addr_clean),
            None
        )

        if existing:
            r_iface = existing.get('interface', '').lower()
            r_actual = existing.get('actual-interface', '').lower()
            if r_iface == interface.lower() or r_actual == interface.lower():
                return {
                    'action': 'noop',
                    'id': existing['.id'],
                    'address': address,
                    'interface': interface,
                    'comment': existing.get('comment', ''),
                }
            raise ValueError(f"Address '{address}' sudah ada di interface lain ('{existing.get('interface')}')")

        new_id = ip_path.add(address=address, interface=interface, comment=comment)
        return {
            'action': 'added',
            'id': new_id,
            'address': address,
            'interface': interface,
            'comment': comment,
        }

    def remove_ip_address(self, address: Optional[str] = None, interface: Optional[str] = None) -> dict:
        if not address and not interface:
            raise ValueError("Harap tentukan address atau interface yang ingin dihapus")

        if address and self._is_mgmt_ip(address):
            raise ValueError(f"Anti-lockout: Dilarang menghapus IP manajemen ({address})")

        self.connect()
        ip_path = self.api.path('ip', 'address')
        addr_clean = address.split('/')[0].strip() if address else None

        matches = []
        for r in ip_path:
            r_addr = r.get('address', '')
            r_clean = r_addr.split('/')[0].strip()
            r_iface = r.get('interface', '').lower()
            r_actual = r.get('actual-interface', '').lower()

            match_addr = True
            if address:
                match_addr = (r_addr == address or r_clean == addr_clean)

            match_iface = True
            if interface:
                match_iface = (r_iface == interface.lower() or r_actual == interface.lower())

            if match_addr and match_iface:
                if self._is_mgmt_ip(r_addr):
                    raise ValueError(f"Anti-lockout: Dilarang menghapus IP manajemen ({r_addr})")
                matches.append(r)

        for m in matches:
            ip_path.remove(m['.id'])

        return {'action': 'removed', 'count': len(matches)}

    def update_ip_address(
        self,
        interface: str,
        new_address: str,
        old_address: Optional[str] = None,
        comment: str = 'IBN_IP'
    ) -> dict:
        if interface.lower() in MANAGEMENT_INTERFACES:
            raise ValueError(f"Anti-lockout: Dilarang mengubah IP pada interface manajemen ({interface})")
        if self._is_mgmt_ip(new_address):
            raise ValueError(f"Anti-lockout: Dilarang menggunakan IP manajemen ({new_address})")

        self.connect()
        ip_path = self.api.path('ip', 'address')
        new_clean = new_address.split('/')[0].strip()

        for r in ip_path:
            r_addr = r.get('address', '')
            r_clean = r_addr.split('/')[0].strip()
            if r_addr == new_address or r_clean == new_clean:
                r_iface = r.get('interface', '').lower()
                r_actual = r.get('actual-interface', '').lower()
                if r_iface != interface.lower() and r_actual != interface.lower():
                    raise ValueError(f"Address '{new_address}' sudah ada di interface lain ('{r.get('interface')}')")

        old_rec = None
        if old_address:
            old_clean = old_address.split('/')[0].strip()
            for r in ip_path:
                r_iface = r.get('interface', '').lower()
                r_actual = r.get('actual-interface', '').lower()
                if r_iface == interface.lower() or r_actual == interface.lower():
                    r_addr = r.get('address', '')
                    r_clean = r_addr.split('/')[0].strip()
                    if r_addr == old_address or r_clean == old_clean:
                        old_rec = r
                        break
        else:
            for r in ip_path:
                r_iface = r.get('interface', '').lower()
                r_actual = r.get('actual-interface', '').lower()
                if r_iface == interface.lower() or r_actual == interface.lower():
                    old_rec = r
                    break

        if old_rec:
            old_addr = old_rec.get('address', '')
            old_clean_val = old_addr.split('/')[0].strip()
            if old_addr == new_address or old_clean_val == new_clean:
                return {
                    'action': 'noop',
                    'id': old_rec['.id'],
                    'interface': interface,
                    'old_address': old_addr,
                    'new_address': new_address,
                    'comment': old_rec.get('comment', comment),
                }
        else:
            old_addr = None

        new_id = ip_path.add(address=new_address, interface=interface, comment=comment)

        if old_rec:
            ip_path.remove(old_rec['.id'])

        return {
            'action': 'updated' if old_rec else 'added',
            'id': new_id,
            'interface': interface,
            'old_address': old_addr,
            'new_address': new_address,
            'comment': comment,
        }

    # Diagnostics & Utility Domain (OTHER)
    def ping_host(self, host: str, count: int = 4) -> dict:
        if not host or not str(host).strip():
            raise ValueError("Target host untuk ping tidak boleh kosong")
        cnt = min(max(int(count), 1), 4)  # INV-DIAG-01: Bound count 1-4
        target_str = str(host).strip()

        self.connect()
        try:
            ping_path = self.api.path('ping')
            res = list(ping_path(address=target_str, count=str(cnt)))
        except Exception:
            res = list(self.api('ping', **{'address': target_str, 'count': str(cnt)}))

        received = 0
        rtts = []
        for r in res:
            if 'time' in r or 'status' not in r or r.get('status') == 'alive':
                received += 1
                t_val = r.get('time')
                if t_val:
                    clean_t = str(t_val).replace('ms', '').replace('s', '').strip()
                    try:
                        rtts.append(float(clean_t))
                    except ValueError:
                        pass

        packet_loss = int(((cnt - received) / cnt) * 100) if cnt > 0 else 0
        min_rtt = min(rtts) if rtts else 0.0
        avg_rtt = round(sum(rtts) / len(rtts), 2) if rtts else 0.0
        max_rtt = max(rtts) if rtts else 0.0

        return {
            'action': 'ping_completed',
            'target': target_str,
            'sent': cnt,
            'received': received,
            'packet_loss_pct': packet_loss,
            'min_rtt_ms': min_rtt,
            'avg_rtt_ms': avg_rtt,
            'max_rtt_ms': max_rtt,
            'details': res,
        }

    def flush_dns_cache(self) -> dict:
        self.connect()
        try:
            dns_cache = self.api.path('ip', 'dns', 'cache')
            try:
                dns_cache('flush')
            except Exception:
                self.api('ip/dns/cache/flush')
        except Exception:
            self.api('ip/dns/cache/flush')

        return {
            'action': 'dns_cache_flushed',
            'status': 'success',
            'message': 'Cache DNS router berhasil dibersihkan',
        }

    def get_system_health(self) -> dict:
        self.connect()
        res_list = list(self.api.path('system', 'resource'))
        info = res_list[0] if res_list else {}

        free_mem_mb = round(int(info.get('free-memory', 0)) / (1024 * 1024), 2)
        total_mem_mb = round(int(info.get('total-memory', 32 * 1024 * 1024)) / (1024 * 1024), 2)
        free_hdd_mb = round(int(info.get('free-hdd-space', 0)) / (1024 * 1024), 2)

        return {
            'action': 'system_health_inspected',
            'platform': info.get('platform', 'MikroTik'),
            'version': info.get('version', 'RouterOS v6'),
            'uptime': info.get('uptime', '-'),
            'cpu_load_pct': int(info.get('cpu-load', 0)),
            'cpu_model': info.get('cpu', 'MIPS 24KEc'),
            'cpu_count': int(info.get('cpu-count', 1)),
            'cpu_freq_mhz': int(info.get('cpu-frequency', 650)),
            'free_memory_mb': free_mem_mb,
            'total_memory_mb': total_mem_mb,
            'free_hdd_mb': free_hdd_mb,
            'board_name': info.get('board-name', 'hAP lite'),
        }


_default_adapter = MikroTikAdapter()

def apply_bandwidth_limit(name: str, target: str, max_limit: str) -> dict:
    return _default_adapter.apply_bandwidth_limit(name, target, max_limit)

def remove_bandwidth_limit(target: str) -> int:
    return _default_adapter.remove_bandwidth_limit(target)

def get_bandwidth_limits() -> list:
    return _default_adapter.get_bandwidth_limits()

def apply_firewall_block(
    target: Optional[str] = None,
    dst_port: Optional[Union[str, int]] = None,
    protocol: str = 'tcp',
    site: Optional[str] = None,
    comment: str = 'IBN_DROP'
) -> dict:
    return _default_adapter.apply_firewall_block(target, dst_port, protocol, site, comment)

def remove_firewall_block(
    target: Optional[str] = None,
    dst_port: Optional[Union[str, int]] = None,
    site: Optional[str] = None,
    comment: Optional[str] = None
) -> int:
    return _default_adapter.remove_firewall_block(target, dst_port, site, comment)

def get_firewall_blocks() -> list:
    return _default_adapter.get_firewall_blocks()

def get_interface_states() -> list:
    return _default_adapter.get_interface_states()

def enable_interface(name: str) -> dict:
    return _default_adapter.enable_interface(name)

def disable_interface(name: str) -> dict:
    return _default_adapter.disable_interface(name)

def get_nat_rules() -> list:
    return _default_adapter.get_nat_rules()

def enable_nat(out_interface: str = 'ether1', comment: str = 'IBN_NAT_MASQ') -> dict:
    return _default_adapter.enable_nat(out_interface, comment)

def disable_nat(out_interface: str = 'ether1', comment: str = 'IBN_NAT_MASQ') -> dict:
    return _default_adapter.disable_nat(out_interface, comment)

def get_ip_addresses(interface: Optional[Union[str, list[str]]] = None) -> list:
    return _default_adapter.get_ip_addresses(interface)

def get_interface_telemetry(interfaces: Optional[Union[str, list[str]]] = None) -> list:
    return _default_adapter.get_interface_telemetry(interfaces)

def add_ip_address(address: str, interface: str, comment: str = 'IBN_IP') -> dict:
    return _default_adapter.add_ip_address(address, interface, comment)

def remove_ip_address(address: Optional[str] = None, interface: Optional[str] = None) -> dict:
    return _default_adapter.remove_ip_address(address, interface)

def update_ip_address(interface: str, new_address: str, old_address: Optional[str] = None, comment: str = 'IBN_IP') -> dict:
    return _default_adapter.update_ip_address(interface, new_address, old_address, comment)

def add_port_forward(
    dst_port: Union[int, str],
    to_address: str,
    to_port: Optional[Union[int, str]] = None,
    protocol: str = 'tcp',
    comment: Optional[str] = None
) -> dict:
    return _default_adapter.add_port_forward(dst_port, to_address, to_port, protocol, comment)

def remove_port_forward(
    dst_port: Optional[Union[int, str]] = None,
    to_address: Optional[str] = None,
    protocol: Optional[str] = None,
    comment: Optional[str] = None
) -> dict:
    return _default_adapter.remove_port_forward(dst_port, to_address, protocol, comment)

def ping_host(host: str, count: int = 4) -> dict:
    return _default_adapter.ping_host(host, count)

def flush_dns_cache() -> dict:
    return _default_adapter.flush_dns_cache()

def get_system_health() -> dict:
    return _default_adapter.get_system_health()



