"""
Landsat Connector
Uses USGS/Landsat STAC APIs for historical imagery.
Collections: landsat-c2-l2 (Collection 2 Level 2)
"""
import httpx
import os
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from app.config import get_settings


@dataclass
class LandsatItem:
    """Landsat STAC item"""
    id: str
    datetime: str
    geometry: Dict
    properties: Dict
    assets: Dict
    cloud_cover: float
    path: int
    row: int


@dataclass
class LandsatSearchResult:
    """Landsat search result"""
    items: List[LandsatItem]
    total_matched: int


class LandsatConnector:
    """
    Connector for Landsat via USGS/LandsatLook STAC API.

    STAC Endpoints:
    - https://landsatlook.usgs.gov/stac-server
    - https://planetarycomputer.microsoft.com/api/stac/v1 (includes Landsat)

    Collections: landsat-c2-l2 (Collection 2 Level 2 Surface Reflectance)

    Some downloads may require Earthdata/USGS authentication.
    """

    def __init__(self):
        self.settings = get_settings()
        # Primary: LandsatLook STAC
        self.stac_url = "https://landsatlook.usgs.gov/stac-server"
        # Alternative: Microsoft Planetary Computer (no auth for search)
        self.pc_stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
        self.username = os.getenv("EARTHDATA_USERNAME")
        self.password = os.getenv("EARTHDATA_PASSWORD")

    async def search(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        max_cloud: float = 30.0,
        collections: List[str] = None
    ) -> LandsatSearchResult:
        """Search Landsat imagery via STAC"""
        if collections is None:
            collections = ["landsat-c2-l2"]

        search_body = {
            "collections": collections,
            "datetime": f"{start_date.isoformat()}T00:00:00Z/{end_date.isoformat()}T23:59:59Z",
            "intersects": geometry,
            "query": {
                "eo:cloud_cover": {"lt": max_cloud}
            },
            "limit": 100,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            # Try Planetary Computer first (no auth needed)
            try:
                response = await client.post(
                    f"{self.pc_stac_url}/search",
                    json=search_body,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                results = response.json()
            except Exception:
                # Fallback to LandsatLook
                response = await client.post(
                    f"{self.stac_url}/search",
                    json=search_body,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                results = response.json()

        items = []
        for feature in results.get("features", []):
            props = feature.get("properties", {})
            item = LandsatItem(
                id=feature.get("id", ""),
                datetime=props.get("datetime", ""),
                geometry=feature.get("geometry", {}),
                properties=props,
                assets=feature.get("assets", {}),
                cloud_cover=props.get("eo:cloud_cover", 100),
                path=props.get("landsat:wrs_path", props.get("wrs:path", 0)),
                row=props.get("landsat:wrs_row", props.get("wrs:row", 0)),
            )
            items.append(item)

        return LandsatSearchResult(
            items=items,
            total_matched=results.get("context", {}).get("matched", len(items))
        )

    async def get_available_dates(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        max_cloud: float = 30.0
    ) -> List[Dict[str, Any]]:
        """Get available Landsat dates"""
        result = await self.search(geometry, start_date, end_date, max_cloud)

        dates = []
        for item in result.items:
            dates.append({
                "date": item.datetime[:10] if item.datetime else "",
                "cloud_cover": item.cloud_cover,
                "path": item.path,
                "row": item.row,
                "item_id": item.id,
                "landsat_product": item.properties.get("landsat:product_id", ""),
                "assets": list(item.assets.keys()),
            })

        return dates

    def get_band_assets(self, item: LandsatItem) -> Dict[str, str]:
        """Map Landsat band names to asset keys"""
        band_map = {
            "coastal": "SR_B1",
            "blue": "SR_B2",
            "green": "SR_B3",
            "red": "SR_B4",
            "nir": "SR_B5",
            "swir1": "SR_B6",
            "swir2": "SR_B7",
            "qa": "QA_PIXEL",
            "saturation": "QA_RADSAT",
            "st": "ST_B10",  # Surface Temperature
        }

        assets = {}
        for name, key in band_map.items():
            if key in item.assets:
                assets[name] = item.assets[key].get("href")

        return assets


# Singleton
_landsat = None

def get_landsat_connector() -> LandsatConnector:
    global _landsat
    if _landsat is None:
        _landsat = LandsatConnector()
    return _landsat