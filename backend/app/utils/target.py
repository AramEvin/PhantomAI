"""
Utility functions for target classification and validation
"""
import re
import socket
from app.models.schemas import TargetType

def classify_target(target: str) -> TargetType:
    """Determine if target is IP or domain."""
    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    if re.match(ip_pattern, target):
        return TargetType.IP
    return TargetType.DOMAIN

def resolve_to_ip(domain: str) -> str | None:
    """Resolve domain to IP address."""
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None

def is_private_ip(ip: str) -> bool:
    """Check if IP is private/internal."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    first, second = int(parts[0]), int(parts[1])
    return (
        first == 10 or
        (first == 172 and 16 <= second <= 31) or
        (first == 192 and second == 168) or
        first == 127
    )
