import httpx

from services.tvheadend_config_service import TVHeadendConfig


class TVHeadendConnectionTestService:

    async def test(
        self,
        config: TVHeadendConfig,
    ) -> dict:

        url = config.url.rstrip("/")

        result = {
            "success": False,
            "server": False,
            "channels": False,
            "epg": False,
            "dvr": False,
            "stream": False,   
        }

        try:
            async with httpx.AsyncClient(
                auth=config.auth,
                timeout=5.0,
            ) as client:

                # Server
                response = await client.get(
                    f"{url}/api/serverinfo"
                )
                response.raise_for_status()

                data = response.json()

                result["server"] = True
                result["server_name"] = data.get(
                    "name",
                    "TVHeadend",
                )
                result["version"] = data.get(
                    "sw_version",
                    "unknown",
                )

                # Channels
                response = await client.get(
                    f"{url}/api/channel/grid",
                    params={"limit": 1},
                )
                response.raise_for_status()

                channel_data = response.json()

                result["channels"] = True
                result["channel_count"] = channel_data.get(
                    "total",
                    0,
                )

                # EPG
                response = await client.get(
                    f"{url}/api/epg/events/grid",
                    params={"limit": 1},
                )
                response.raise_for_status()

                epg_data = response.json()

                result["epg"] = True
                result["epg_count"] = epg_data.get(
                    "total",
                    0,
                )

                # DVR
                try:
                    response = await client.get(
                        f"{url}/api/dvr/entry/grid",
                        params={"limit": 1},
                    )

                    if response.status_code == 401:
                        result["dvr"] = None
                        result["dvr_message"] = "Nicht verfügbar / keine Berechtigung"
                    else:
                        response.raise_for_status()

                        dvr_data = response.json()

                        result["dvr"] = True
                        result["dvr_count"] = dvr_data.get("total", 0)

                except httpx.RequestError as error:
                    result["dvr"] = False
                    result["dvr_message"] = str(error)

                response = await client.get(
                    f"{url}/api/channel/grid",
                    params={"limit": 1},
                )
                response.raise_for_status()

                channel_data = response.json()

                result["channels"] = True
                result["channel_count"] = channel_data.get("total", 0)
                entries = channel_data.get("entries", [])

                test_channel = entries[0] if entries else None

                # Stream
                if test_channel:
                    channel_uuid = test_channel.get("uuid")

                    try:
                        async with client.stream(
                            "GET",
                            f"{url}/stream/channel/{channel_uuid}",
                        ) as response:

                            response.raise_for_status()

                            async for chunk in response.aiter_bytes():
                                if chunk:
                                    result["stream"] = True
                                    break

                        if not result["stream"]:
                            result["stream_message"] = (
                                "Stream liefert keine Daten"
                            )

                    except httpx.HTTPStatusError as error:
                        result["stream"] = False
                        result["stream_message"] = (
                            f"HTTP {error.response.status_code}"
                        )

                    except httpx.RequestError as error:
                        result["stream"] = False
                        result["stream_message"] = str(error)

                else:
                    result["stream"] = False
                    result["stream_message"] = (
                        "Kein Channel für Stream-Test vorhanden"
                    )

                result["success"] = True

        except httpx.HTTPStatusError as error:
            result["message"] = (
                f"HTTP {error.response.status_code}"
            )

        except httpx.RequestError as error:
            result["message"] = str(error)

        except ValueError:
            result["message"] = (
                "Ungültige Antwort von TVHeadend"
            )

        return result