"""
The networks the terminal may reach: an HPC machine is only added, and only connected to, when its address
is in one of them (ALLOWED_NETWORKS, comma-separated CIDRs, set to the lab's HPC subnet).

Checked against the address the machine's name resolves to at that moment, and the connection is made to
that checked address, so changing a name in DNS later does not lead the terminal anywhere else. Left unset,
only private addresses are allowed (the lab's own networks, never the internet).

This holds in the terminal itself. For a limit that holds even if the service were compromised, the server's
firewall should allow the terminal's container out only to the same networks (see the README).
"""
import ipaddress
import os
import socket
from typing import List, Tuple

PRIVATE = '10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,fc00::/7'


def allowed() -> List[ipaddress._BaseNetwork]:
    raw = os.environ.get('ALLOWED_NETWORKS', '').strip() or PRIVATE
    out = []
    for part in raw.replace(';', ',').split(','):
        part = part.strip()
        if part:
            out.append(ipaddress.ip_network(part, strict=False))
    return out


def describe() -> str:
    return ', '.join(str(n) for n in allowed())


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
                         'An administrator of the suite sets these (TERMINAL_ALLOWED_NETWORKS).')
    return ok
