import librouteros
from typing import Optional, Union
from config import ROUTER_HOST, ROUTER_PORT, ROUTER_USER, ROUTER_PASS, ROUTER_TIMEOUT


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
        comment: str = 'IBN_DROP'
    ) -> dict:
        if not target and dst_port is None:
            raise ValueError("Target IP atau dst_port wajib diisi")

        target_ip = target.split('/')[0] if target else None
        if target_ip and target_ip in ('192.168.88.1', self.host):
            raise ValueError(f"Anti-lockout: dilarang memblokir IP router/gateway ({target_ip})")

        port_str = str(dst_port) if dst_port is not None else None
        proto_str = protocol.lower() if protocol else 'tcp'

        self.connect()
        fw = self.api.path('ip', 'firewall', 'filter')

        def _match_existing(r):
            if r.get('chain') != 'forward' or r.get('action') != 'drop':
                return False
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
                'target': target,
                'dst_port': dst_port,
                'protocol': protocol if dst_port is not None else None,
                'comment': existing.get('comment', ''),
            }

        params = {'chain': 'forward', 'action': 'drop', 'comment': comment}
        if target:
            params['src-address'] = target
        if dst_port is not None:
            params['protocol'] = proto_str
            params['dst-port'] = port_str

        new_id = fw.add(**params)
        return {
            'action': 'added',
            'id': new_id,
            'target': target,
            'dst_port': dst_port,
            'protocol': protocol if dst_port is not None else None,
            'comment': comment,
        }

    def remove_firewall_block(
        self,
        target: Optional[str] = None,
        dst_port: Optional[Union[str, int]] = None,
        comment: Optional[str] = None
    ) -> int:
        self.connect()
        fw = self.api.path('ip', 'firewall', 'filter')
        target_ip = target.split('/')[0] if target else None
        port_str = str(dst_port) if dst_port is not None else None

        matches = []
        for r in fw:
            if r.get('chain') != 'forward' or r.get('action') != 'drop':
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
    comment: str = 'IBN_DROP'
) -> dict:
    return _default_adapter.apply_firewall_block(target, dst_port, protocol, comment)

def remove_firewall_block(
    target: Optional[str] = None,
    dst_port: Optional[Union[str, int]] = None,
    comment: Optional[str] = None
) -> int:
    return _default_adapter.remove_firewall_block(target, dst_port, comment)

def get_firewall_blocks() -> list:
    return _default_adapter.get_firewall_blocks()

