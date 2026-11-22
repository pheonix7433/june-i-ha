"""June.Ⅰ 户型中枢：托管户型编辑器、存储 house.json 与预渲染资产，供微信小程序拉取。

数据流：
    编辑器（HA 侧边栏 iframe）--PUT--> 本集成（.storage/june_i.data.json）
    小程序 --GET house/render/media--> 本集成
用户全程不碰文件。

两种启用方式（二选一）：
    ① 界面配置（推荐，零代码）：设置 → 设备与服务 → 添加集成 → 搜「June.Ⅰ」→ 点添加
    ② yaml：configuration.yaml 加一行 `june_i:`，重启
"""
import inspect
import logging

from homeassistant.core import HomeAssistant

from .http import setup_http

DOMAIN = "june_i"
LOGGER = logging.getLogger(__package__)


async def _setup_hub(hass: HomeAssistant) -> None:
    """初始化存储 / 编辑器托管 / API / 侧边栏（幂等，yaml 与 UI 两种方式共用）。"""
    if hass.data.get(DOMAIN):
        return  # 已初始化过（比如 yaml 和 UI 同时配置了）

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
    await _register_panel(hass, editor_url)

    LOGGER.info("June.Ⅰ 户型中枢已启动（编辑器: %s）", editor_url)


async def _register_panel(hass: HomeAssistant, editor_url: str) -> bool:
    """注册侧边栏 iframe 面板。兼容新旧 HA：

    ① frontend.async_register_built_in_panel —— 2023.x 起的现役 API（hassio 同款）
    ② hass.components.frontend.async_register_panel —— 老版本（2025.x 已移除）
    全部失败时发一条持久通知，避免“装了但没入口”无从排查。
    """
    title = "户型编辑器"
    icon = "mdi:floor-plan"
    errors = []

    from homeassistant.components import frontend

    reg_builtin = getattr(frontend, "async_register_built_in_panel", None)
    if callable(reg_builtin):
        try:
            result = reg_builtin(
                hass,
                component_name="iframe",
                sidebar_title=title,
                sidebar_icon=icon,
                frontend_url_path=DOMAIN,
                config={"url": editor_url},
                require_admin=False,
            )
            if inspect.isawaitable(result):
                await result
            LOGGER.info("侧边栏面板已注册（built_in API）: %s", editor_url)
            return True
        except Exception as err:  # noqa: BLE001
            errors.append("built_in: %r" % (err,))

    # 旧版兜底
    legacy = getattr(getattr(hass, "components", None), "frontend", None) if hasattr(
        hass, "components"
    ) else None
    reg_legacy = getattr(legacy, "async_register_panel", None) if legacy else None
    if callable(reg_legacy):
        try:
            result = reg_legacy(
                "iframe",
                {"url": editor_url},
                DOMAIN,
                sidebar_title=title,
                sidebar_icon=icon,
            )
            if inspect.isawaitable(result):
                await result
            LOGGER.info("侧边栏面板已注册（legacy API）: %s", editor_url)
            return True
        except Exception as err:  # noqa: BLE001
            errors.append("legacy: %r" % (err,))

    LOGGER.error("侧边栏面板注册失败：%s；可直接访问 %s", "; ".join(errors), editor_url)
    try:
        from homeassistant.components import persistent_notification

        persistent_notification.async_create(
            hass,
            "「户型编辑器」侧边栏注册失败（%s）。"
            "编辑器仍可直接访问：%s"
            % ("; ".join(errors), editor_url),
            title="June.Ⅰ 户型中枢",
            notification_id="june_i_panel_failed",
        )
    except Exception:  # noqa: BLE001
        LOGGER.exception("持久通知创建失败")
    return False


async def async_setup(hass: HomeAssistant, config: dict):
    """yaml 方式启用：configuration.yaml 里加 `june_i:`。"""
    if config.get(DOMAIN) is not None:
        await _setup_hub(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    """UI 配置方式启用：设置 → 设备与服务 → 添加集成。"""
    await _setup_hub(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """UI 里「删除」集成时：不做破坏性清理（户型数据保留在 .storage，重装不丢）。"""
    return True
