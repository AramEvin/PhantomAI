"""
Target classifier — determines if input is an IP or domain
Provides: classify_target, resolve_to_ip, TargetType (for backward compat)
"""
import re
import socket


# String constants for backward compat — tools that import TargetType
# can use TargetType.IP / TargetType.DOMAIN or just compare to "ip"/"domain"
class TargetType:
    IP = "ip"
    DOMAIN = "domain"


def classify_target(target: str) -> str:
    """Returns 'ip' or 'domain'."""
    target = target.strip().lower()

    # IPv4
    if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", target):
        parts = target.split(".")
        if all(0 <= int(p) <= 255 for p in parts):
            return TargetType.IP

    # IPv6 (basic)
    if ":" in target and re.match(r"^[0-9a-f:]+$", target):
        return TargetType.IP

    return TargetType.DOMAIN


def resolve_to_ip(target: str) -> str:
    """Resolve a domain to its IP address. Returns the IP, or target unchanged if already an IP."""
    target = target.strip().lower()
    if classify_target(target) == TargetType.IP:
        return target
    try:
        return socket.gethostbyname(target)
    except Exception:
        return target
