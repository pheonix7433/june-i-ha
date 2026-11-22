"""June.Ⅰ 户型中枢：托管户型编辑器、存储 house.json 与预渲染资产，供微信小程序拉取。

数据流：
    编辑器（HA 侧边栏 iframe）--PUT--> 本集成（.storage/june_i.data.json）
    小程序 --GET house/render/media--> 本集成
用户全程不碰文件。

安装：把 custom_components/june_i 整个目录拷到 HA 的 config/custom_components/ 下，
configuration.yaml 加一行 `june_i:`，重启 HA。侧边栏出现「户型编辑器」。
"""
import logging

from homeassistant.core import HomeAssistant

from .http import setup_http

DOMAIN = "june_i"
LOGGER = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: dict):
    """yaml 方式启用：configuration.yaml 里加 `june_i:`。"""
    from homeassistant.helpers.storage import Store

    store = Store(hass, 1, "june_i.data.json")
    loaded = await store.async_load() or {}
    data = {
        "house": loaded.get("house") or {},
        "manifest": loaded.get("manifest") or {},
        "media": loaded.get("media") or {},
    }
    hub = {"store": store, "data": data}
    hass.data[DOMAIN] = hub

    # 托管编辑器（单文件 3d_JX.html → editor/index.html）
    editor_dir = str(__import__("pathlib").Path(__file__).parent / "editor")
    try:
        hass.http.register_static_path("/june_i/editor", editor_dir, cache_headers=False)
    except Exception:  # noqa: BLE001
        LOGGER.exception("编辑器静态路径注册失败")

    # API 视图（/api/june_i/house、/api/june_i/render、/api/june_i/media/{name}）
    setup_http(hass, hub)

    # 侧边栏面板（iframe 指向编辑器）
    editor_url = "/june_i/editor/index.html"
    registered = False
    try:
        hass.components.frontend.async_register_panel(
            "iframe",
            {"url": editor_url},
            DOMAIN,
            sidebar_title="户型编辑器",
            sidebar_icon="mdi:floor-plan",
        )
        registered = True
    except Exception:  # noqa: BLE001
        LOGGER.warning("旧版面板注册失败，尝试新版 API", exc_info=True)
    if not registered:
        try:
            from homeassistant.components import frontend

            frontend.async_register_panel(
                hass,
                component_name="custom",
                config={
                    "component": "iframe",
                    "panel_name": DOMAIN,
                    "url": editor_url,
                },
                frontend_url_path=DOMAIN,
                sidebar_title="户型编辑器",
                sidebar_icon="mdi:floor-plan",
            )
            registered = True
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "侧边栏面板注册失败；编辑器仍可手动访问 %s", editor_url
            )

    LOGGER.info("June.Ⅰ 户型中枢已启动（编辑器: %s）", editor_url)
    return True
