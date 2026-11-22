"""June.Ⅰ 户型中枢的 HTTP API。

三个鉴权视图（Bearer 长期访问令牌，编辑器与小程序同一把）：
    GET / PUT  /api/june_i/house          户型 JSON
    GET / PUT  /api/june_i/render         预渲染清单（manifest + 文件 base64）
    GET        /api/june_i/media/{name}   渲染图片（PNG bytes）
"""
import base64
import binascii
import json
import re

from aiohttp import web
from homeassistant.components.http import HomeAssistantView

SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
MAX_FILE_BYTES = 3 * 1024 * 1024  # 单个媒体文件上限（渲染图几十 KB，远够）


class JuneHouseView(HomeAssistantView):
    """户型 JSON 存取。"""

    url = "/api/june_i/house"
    name = "api:june_i:house"
    requires_auth = True

    async def get(self, request):
        hub = request.app["hass"].data["june_i"]
        return self.json(hub["data"].get("house") or {})

    async def put(self, request):
        try:
            body = await request.json()
        except (ValueError, TypeError):
            return self.json({"error": "bad json"}, status=400)
        if not isinstance(body, dict) or not body.get("rooms"):
            return self.json({"error": "house 缺少 rooms"}, status=400)
        hub = request.app["hass"].data["june_i"]
        hub["data"]["house"] = body
        await hub["store"].async_save(hub["data"])
        return self.json({"ok": True, "rooms": len(body.get("rooms") or [])})


class JuneRenderView(HomeAssistantView):
    """预渲染清单存取（PUT 同时接收媒体文件 base64）。"""

    url = "/api/june_i/render"
    name = "api:june_i:render"
    requires_auth = True

    async def get(self, request):
        hub = request.app["hass"].data["june_i"]
        manifest = hub["data"].get("manifest") or {}
        if not manifest:
            return self.json({"empty": True})
        return self.json(manifest)

    async def put(self, request):
        try:
            body = await request.json()
        except (ValueError, TypeError):
            return self.json({"error": "bad json"}, status=400)
        manifest = body.get("manifest")
        files = body.get("files") or {}
        if not isinstance(manifest, dict) or not manifest.get("overview"):
            return self.json({"error": "manifest 缺少 overview"}, status=400)
        if len(files) > 32:
            return self.json({"error": "文件太多"}, status=400)

        media = {}
        for name, data_url in files.items():
            if not SAFE_NAME.match(str(name)):
                return self.json({"error": "非法文件名: " + str(name)}, status=400)
            if not isinstance(data_url, str) or "," not in data_url:
                return self.json({"error": "文件不是 dataURL: " + str(name)}, status=400)
            b64 = data_url.split(",", 1)[1]
            try:
                raw = base64.b64decode(b64, validate=True)
            except (binascii.Error, ValueError):
                return self.json({"error": "base64 解码失败: " + str(name)}, status=400)
            if len(raw) > MAX_FILE_BYTES:
                return self.json({"error": "文件过大: " + str(name)}, status=400)
            media[name] = b64

        hub = request.app["hass"].data["june_i"]
        # 只增改不删：旧文件保留（小程序可能还在缓存旧 manifest 引用它们）
        hub["data"]["media"].update(media)
        hub["data"]["manifest"] = manifest
        await hub["store"].async_save(hub["data"])
        return self.json({"ok": True, "updatedAt": manifest.get("updatedAt")})


class JuneMediaView(HomeAssistantView):
    """渲染图片下载。"""

    url = "/api/june_i/media/{name}"
    name = "api:june_i:media"
    requires_auth = True

    async def get(self, request, name: str):
        if not SAFE_NAME.match(name or ""):
            return web.Response(status=400, text="bad name")
        hub = request.app["hass"].data["june_i"]
        b64 = (hub["data"].get("media") or {}).get(name)
        if not b64:
            return web.Response(status=404, text="not found")
        try:
            raw = base64.b64decode(b64)
        except (binascii.Error, ValueError):
            return web.Response(status=500, text="corrupt")
        content_type = "image/png" if name.endswith(".png") else (
            "image/webp" if name.endswith(".webp") else "application/octet-stream"
        )
        return web.Response(body=raw, content_type=content_type)


def setup_http(hass, hub) -> None:
    """注册 API 视图（视图内部经 request.app["hass"].data["june_i"] 取数据）。"""
    for view in (JuneHouseView(), JuneRenderView(), JuneMediaView()):
        hass.http.register_view(view)
