"""SSM Inventory match data model."""

from dataclasses import dataclass


@dataclass
class InventoryMatch:
    instance_id: str
    package: str
    version: str
    app_tag: str
    environment: str
    freshness_ts: str
