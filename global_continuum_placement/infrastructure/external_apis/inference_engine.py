import logging
from dataclasses import dataclass

import aiohttp

from global_continuum_placement.application.platform_service import IPlatformService
from global_continuum_placement.domain.platform.platform import Platform

logger = logging.getLogger(__name__)


@dataclass
class InferenceEngineAPIPlatformService(IPlatformService):
    inference_engine_base_api: str
    authorization_token: str

    """
    In memory representation of the platform. Might be updated directly (POST) or using the updated-platform (GET)
    """
    _platform: Platform = None

    async def set_platform(self, platform: Platform) -> None:
        self._platform = platform

    async def get_platform(self) -> Platform:
        if self._platform is None:
            return await self.update_platform()
        return self._platform

    async def update_platform(self) -> Platform:
        url = self.inference_engine_base_api.rstrip("/") + "/cluster"
        logger.info("Get platform update from %s", url)
        async with aiohttp.client.ClientSession() as session:
            async with session.get(
                url,
                headers={"X-API-KEY": self.authorization_token},
                ssl=False,
            ) as response:
                response_json = await response.json()
                logger.info("response for platform request %s", response_json)
                self._platform = Platform.create_from_dict(response_json["platform"])
        return self._platform
