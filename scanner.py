"""Async scan logic using pyasic for discovering miners on the LAN."""

import asyncio
from typing import Any

from pyasic.network import MinerNetwork
from pyasic import settings

from config import SUBNET, WHATSMINER_PASSWORD


def _configure_pyasic() -> None:
    """Set Whatsminer password and other pyasic settings."""
    settings.update("default_whatsminer_rpc_password", WHATSMINER_PASSWORD)


def _extract_workers(miner_data: Any) -> list[tuple[str, str]]:
    """Extract pool URL and worker (user) from MinerData.config.pools."""
    workers: list[tuple[str, str]] = []
    config = getattr(miner_data, "config", None)
    if not config:
        return workers
    pools = getattr(config, "pools", None)
    if not pools:
        return workers
    pool_list = getattr(pools, "pools", None)
    if pool_list is None:
        pool_list = getattr(pools, "pool_list", None)
    if pool_list is None:
        try:
            pool_list = list(pools) if hasattr(pools, "__iter__") else []
        except Exception:
            pool_list = []
    for i, pool in enumerate(pool_list or []):
        url = getattr(pool, "url", None) or getattr(pool, "stratum", None) or ""
        user = getattr(pool, "user", None) or getattr(pool, "username", None) or ""
        if isinstance(url, bytes):
            url = url.decode("utf-8", errors="replace")
        if isinstance(user, bytes):
            user = user.decode("utf-8", errors="replace")
        url = str(url) if url else ""
        user = str(user) if user else ""
        workers.append((url, user))
    return workers


async def scan_network(subnet: str | None = None) -> list[dict]:
    """
    Scan the LAN for miners and return a list of miner data dicts.
    Each dict contains all MinerData fields plus extracted workers.
    """
    _configure_pyasic()
    net = subnet or SUBNET
    network = MinerNetwork.from_subnet(net)
    miners = await network.scan()

    results: list[dict] = []
    for miner in miners:
        if miner is None:
            continue
        try:
            data = await miner.get_data()
            if data is None:
                continue
            workers = _extract_workers(data)
            results.append(_miner_data_to_dict(data, workers))
        except Exception:
            continue
    return results


def _miner_data_to_dict(data: Any, workers: list[tuple[str, str]]) -> dict:
    """Convert MinerData to a flat dict for GUI display."""
    def _fmt(v: Any) -> str:
        if v is None:
            return ""
        if hasattr(v, "th"):  # AlgoHashRate
            return str(v)
        return str(v)

    hashboards_info = []
    for hb in getattr(data, "hashboards", []) or []:
        hr = getattr(hb, "hashrate", None)
        temp = getattr(hb, "temperature", None)
        chips = getattr(hb, "chips", None)
        hashboards_info.append({
            "hashrate": _fmt(hr),
            "temp": _fmt(temp),
            "chips": _fmt(chips),
        })

    fans_info = []
    for f in getattr(data, "fans", []) or []:
        speed = getattr(f, "speed", None)
        fans_info.append({"speed": _fmt(speed)})

    errors_list = []
    for e in getattr(data, "errors", []) or []:
        errors_list.append(str(e))

    return {
        "ip": getattr(data, "ip", ""),
        "hostname": _fmt(getattr(data, "hostname", None)),
        "model": _fmt(getattr(data, "model", None)),
        "make": _fmt(getattr(data, "make", None)),
        "firmware": _fmt(getattr(data, "firmware", None)),
        "hashrate": _fmt(getattr(data, "hashrate", None)),
        "expected_hashrate": _fmt(getattr(data, "expected_hashrate", None)),
        "wattage": _fmt(getattr(data, "wattage", None)),
        "efficiency": _fmt(getattr(data, "efficiency", None)),
        "temperature_avg": _fmt(getattr(data, "temperature_avg", None)),
        "env_temp": _fmt(getattr(data, "env_temp", None)),
        "uptime": getattr(data, "uptime", None),
        "is_mining": getattr(data, "is_mining", True),
        "fault_light": getattr(data, "fault_light", None),
        "hashboards": hashboards_info,
        "fans": fans_info,
        "workers": workers,
        "errors": errors_list,
    }


def run_scan(subnet: str | None = None) -> list[dict]:
    """Synchronous wrapper for scan_network (for use from non-async code)."""
    return asyncio.run(scan_network(subnet))
