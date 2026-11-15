"""
The networks the terminal may reach: an HPC machine is only added, and only connected to, when its address
is in one of them. An administrator sets them on the suite's dashboard (HPC Terminal), kept in the suite's
database (settings 'terminal.networks') and read here on every check, so a change counts at once. Until one
is saved, ALLOWED_NETWORKS (comma-separated CIDRs) counts. NETWORK_LIMIT, if set on the server, is a bound
no list goes beyond, so a stolen administrator sign-in cannot point the terminal elsewhere.

Checked against the address the machine's name resolves to at that moment, and the connection is made to
that checked address, so changing a name in DNS later does not lead the terminal anywhere else. Left unset,
only private addresses are allowed (the lab's own networks, never the internet).

This holds in the terminal itself. For a limit that holds even if the service were compromised, the server's
firewall should allow the terminal's container out only to the same networks (see the README).
"""
import ipaddress
import json
import os
import socket
import sqlite3
from typing import List, Optional, Tuple

PRIVATE = '10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,fc00::/7'


def _parse(raw: str) -> list:
    out = []
    for part in (raw or '').replace(';', ',').split(','):
        part = part.strip()
        if part:
            try:
                out.append(ipaddress.ip_network(part, strict=False))
            except ValueError:
                pass                    # a bad entry allows nothing, never everything
    return out


def from_dashboard() -> Optional[list]:
    """The networks saved on the suite's dashboard, or None when none were."""
    path = os.environ.get('SUITE_DATABASE_PATH', '/suite/suite.db')
    try:
        conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True, timeout=5)
        try:
            row = conn.execute("SELECT value FROM settings WHERE key = 'terminal.networks'").fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        return None
    if row is None:
        return None
    try:
        return _parse(','.join(str(e.get('network', '')) for e in json.loads(row[0])))
    except (ValueError, AttributeError, TypeError):
        return []                       # unreadable: nothing, rather than everything


def source() -> str:
    if from_dashboard() is not None:
        return 'dashboard'
    return 'env' if os.environ.get('ALLOWED_NETWORKS', '').strip() else 'default'


def allowed() -> List[ipaddress._BaseNetwork]:
    nets = from_dashboard()
    if nets is None:
        nets = _parse(os.environ.get('ALLOWED_NETWORKS', '').strip() or PRIVATE)
    limit = _parse(os.environ.get('NETWORK_LIMIT', ''))
    if limit:
        nets = [n for n in nets if any(n.version == l.version and n.subnet_of(l) for l in limit)]
    return nets


def describe() -> str:
    return ', '.join(str(n) for n in allowed()) or 'none'



def permitted(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address.split('%')[0])
    except ValueError:
        return False
    nets = [n for n in allowed() if n.version == ip.version]
    if ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
        # Never the server itself, nor anything but a machine on the network, unless listed outright.
        return any(ip in n and (n.is_loopback or n.is_link_local) for n in nets)
    return any(ip in n for n in nets)


class NotAllowed(Exception):
    pass


def resolve(host: str, port: int) -> List[Tuple[int, int, int, tuple]]:
    """The machine's addresses that are allowed, as (family, type, proto, sockaddr); NotAllowed if none."""
    try:
        found = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise NotAllowed(f'{host} could not be found: {exc.strerror}')
    ok = [(f, t, p, a) for f, t, p, _, a in found if permitted(a[0])]
    if not ok:
        shown = ', '.join(sorted({a[0] for _, _, _, _, a in found}))
        raise NotAllowed(f'{host} ({shown}) is outside the networks the terminal may reach ({describe()}). '
                         'An administrator sets these on the suite\u2019s dashboard, under HPC Terminal.')
    return ok
