"""
Sentinel-2 Connector
Uses Copernicus STAC API: https://stac.dataspace.copernicus.eu/v1/
Collection: sentinel-2-l2a (Sentinel-2 Level 2A Surface Reflectance)
Requires authentication for downloads (Copernicus Data Space credentials)
"""
import httpx
import os
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from shapely.geometry import Polygon, mapping
from app.config import get_settings


@dataclass
class SentinelSearchParams:
    """Search parameters for Sentinel-2 imagery"""
    geometry: Dict  # GeoJSON geometry
    start_date: date
    end_date: date
    max_cloud_cover: float = 30.0
    collections: List[str] = None

    def __post_init__(self):
        if self.collections is None:
            # Copernicus Data Space Sentinel-2 L2A collection
            self.collections = ["sentinel-2-l2a"]


@dataclass
class SentinelItem:
    """Sentinel-2 STAC item"""
    id: str
    datetime: str
    geometry: Dict
    properties: Dict
    assets: Dict
    cloud_cover: float
    tile_id: Optional[str] = None
    platform: Optional[str] = None  # S2A or S2B
    orbit_state: Optional[str] = None  # ascending/descending


@dataclass
class SentinelSearchResult:
    """Result of Sentinel-2 search"""
    items: List[SentinelItem]
    total_matched: int
    search_params: SentinelSearchParams


class Sentinel2Connector:
    """
    Connector for Sentinel-2 via Copernicus Data Space STAC API.

    Copernicus Data Space Ecosystem (CDSE) provides:
    - STAC API: https://stac.dataspace.copernicus.eu/v1/
    - S3 Access: https://eodata.dataspace.copernicus.eu (requires auth)
    - OpenID Connect: https://identity.dataspace.copernicus.eu/

    For production use, set in .env:
    - COPERNICUS_CLIENT_ID
    - COPERNICUS_CLIENT_SECRET
    - COPERNICUS_USERNAME
    - COPERNICUS_PASSWORD
    """

    # Known Sentinel-2 collections in CDSE
    KNOWN_COLLECTIONS = {
        "sentinel-2-l2a": "Sentinel-2 Level 2A Surface Reflectance (10m/20m/60m)",
        "sentinel-2-l1c": "Sentinel-2 Level 1C Top-of-Atmosphere Reflectance",
    }

    def __init__(self):
        self.settings = get_settings()
        self.stac_url = "https://stac.dataspace.copernicus.eu/v1"
        self.client_id = os.getenv("COPERNICUS_CLIENT_ID")
        self.client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")
        self.username = os.getenv("COPERNICUS_USERNAME")
        self.password = os.getenv("COPERNICUS_PASSWORD")
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        self._token_type: str = "Bearer"

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers if credentials available"""
        token = self._get_access_token()
        if token:
            return {"Authorization": f"{self._token_type} {token}"}
        return {}

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token for Copernicus Data Space.

        Uses client credentials flow or password grant.
        Token is cached until expiry.
        """
        if self._access_token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._access_token

        if self.client_id and self.client_secret:
            return self._fetch_client_credentials_token()
        elif self.username and self.password:
            return self._fetch_password_grant_token()

        return ""

    def _fetch_client_credentials_token(self) -> str:
        """Fetch token using client credentials flow"""
        try:
            token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            with httpx.Client(timeout=30) as client:
                response = client.post(token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data.get("access_token", "")
                self._token_type = token_data.get("token_type", "Bearer")
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 60)
                return self._access_token
        except Exception as e:
            print(f"Failed to get client credentials token: {e}")
            return ""

    def _fetch_password_grant_token(self) -> str:
        """Fetch token using password grant (for user credentials)"""
        try:
            token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
            data = {
                "grant_type": "password",
                "client_id": "cdse-public",
                "username": self.username,
                "password": self.password,
            }
            with httpx.Client(timeout=30) as client:
                response = client.post(token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data.get("access_token", "")
                self._token_type = token_data.get("token_type", "Bearer")
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 60)
                return self._access_token
        except Exception as e:
            print(f"Failed to get password grant token: {e}")
            return ""

    async def search(
        self,
        params: SentinelSearchParams
    ) -> SentinelSearchResult:
        """
        Search Sentinel-2 imagery via STAC API.

        Args:
            params: Search parameters including geometry, dates, cloud cover

        Returns:
            SentinelSearchResult with matching items
        """
        # Build STAC search request
        search_body = {
            "collections": params.collections,
            "datetime": f"{params.start_date.isoformat()}T00:00:00Z/{params.end_date.isoformat()}T23:59:59Z",
            "intersects": params.geometry,
            "query": {
                "eo:cloud_cover": {"lt": params.max_cloud_cover}
            },
            "limit": 100,
        }

        headers = {
            "Content-Type": "application/json",
            **self._get_auth_headers()
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.stac_url}/search",
                json=search_body,
                headers=headers
            )
            response.raise_for_status()
            results = response.json()

        items = []
        for feature in results.get("features", []):
            props = feature.get("properties", {})
            item = SentinelItem(
                id=feature.get("id", ""),
                datetime=props.get("datetime", ""),
                geometry=feature.get("geometry", {}),
                properties=props,
                assets=feature.get("assets", {}),
                cloud_cover=props.get("eo:cloud_cover", 100),
                tile_id=props.get("s2:mgrs_tile", props.get("mgrs:tile", None)),
                platform=props.get("platform", props.get("sat:platform", None)),
                orbit_state=props.get("sat:orbit_state", None),
            )
            items.append(item)

        return SentinelSearchResult(
            items=items,
            total_matched=results.get("context", {}).get("matched", len(items)),
            search_params=params
        )

    async def get_available_dates(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        max_cloud: float = 30.0
    ) -> List[Dict[str, Any]]:
        """Get list of available Sentinel-2 dates with cloud cover"""
        params = SentinelSearchParams(
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=max_cloud
        )
        result = await self.search(params)

        dates = []
        for item in result.items:
            dates.append({
                "date": item.datetime[:10] if item.datetime else "",
                "cloud_cover": item.cloud_cover,
                "tile_id": item.tile_id,
                "item_id": item.id,
                "platform": item.platform,
                "orbit_state": item.orbit_state,
                "assets": list(item.assets.keys()),
                "preview_url": self._get_preview_url(item.assets),
            })

        return dates

    def _get_preview_url(self, assets: Dict) -> Optional[str]:
        """Extract preview/thumbnail URL from assets"""
        for key in ["thumbnail", "rendered_preview", "visual", "true_color", "rgb"]:
            if key in assets:
                return assets[key].get("href")
        return None

    def get_band_assets(self, item: SentinelItem) -> Dict[str, str]:
        """Map Sentinel-2 band names to asset keys"""
        band_map = {
            "B01": "B01",  # Coastal aerosol (60m)
            "B02": "B02",  # Blue (10m)
            "B03": "B03",  # Green (10m)
            "B04": "B04",  # Red (10m)
            "B05": "B05",  # Red Edge 1 (20m)
            "B06": "B06",  # Red Edge 2 (20m)
            "B07": "B07",  # Red Edge 3 (20m)
            "B08": "B08",  # NIR (10m)
            "B8A": "B8A",  # Red Edge 4 / NIR narrow (20m)
            "B09": "B09",  # Water vapour (60m)
            "B10": "B10",  # Cirrus (60m) - L1C only
            "B11": "B11",  # SWIR 1 (20m)
            "B12": "B12",  # SWIR 2 (20m)
            "SCL": "SCL",  # Scene Classification (20m) - L2A only
            "WVP": "WVP",  # Water Vapor Pressure (10m) - L2A only
            "AOT": "AOT",  # Aerosol Optical Thickness (10m) - L2A only
            "TCI": "TCI",  # True Color Image (10m) - L2A only
        }

        assets = {}
        for name, key in band_map.items():
            if key in item.assets:
                assets[name] = item.assets[key].get("href")

        return assets

    async def download_bands(
        self,
        item: SentinelItem,
        bands: List[str],
        geometry: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Download specific bands for an item.

        Note: Requires authenticated access for actual downloads.
        For CDSE, authenticated S3 access is used.
        This method returns signed URLs or asset hrefs.
        """
        available_bands = self.get_band_assets(item)

        # Filter requested bands
        result_bands = {}
        for band in bands:
            if band in available_bands:
                result_bands[band] = available_bands[band]

        return {
            "item_id": item.id,
            "datetime": item.datetime,
            "tile_id": item.tile_id,
            "bands": result_bands,
            "note": "Authenticated S3 access required for actual data download. Use COPERNICUS_CLIENT_ID/SECRET for signed URLs."
        }

    @staticmethod
    def geometry_from_bounds(bounds: Tuple[float, float, float, float]) -> Dict:
        """Create GeoJSON polygon from bounds (min_lon, min_lat, max_lon, max_lat)"""
        min_lon, min_lat, max_lon, max_lat = bounds
        return {
            "type": "Polygon",
            "coordinates": [[
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ]]
        }

    @staticmethod
    def geometry_from_polygon(polygon: Polygon) -> Dict:
        """Convert Shapely polygon to GeoJSON"""
        return mapping(polygon)

    async def list_collections(self) -> List[Dict[str, Any]]:
        """List available Sentinel-2 collections in the STAC catalog"""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.stac_url}/collections")
            response.raise_for_status()
            results = response.json()

        sentinel_collections = []
        for coll in results.get("collections", []):
            coll_id = coll.get("id", "")
            if "sentinel-2" in coll_id.lower() or "s2" in coll_id.lower():
                sentinel_collections.append({
                    "id": coll_id,
                    "title": coll.get("title", ""),
                    "description": coll.get("description", ""),
                    "extent": coll.get("extent", {}),
                    "keywords": coll.get("keywords", []),
                })

        return sentinel_collections


# Need timedelta import
from datetime import timedelta


# Singleton
_sentinel2 = None

def get_sentinel2_connector() -> Sentinel2Connector:
    global _sentinel2
    if _sentinel2 is None:
        _sentinel2 = Sentinel2Connector()
    return _sentinel2