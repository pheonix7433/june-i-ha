"""UI 配置流程：无任何必填项，点「添加」即完成（数据存 .storage，无需 yaml）。"""
from homeassistant import config_entries

from .const import DOMAIN  # noqa: F401  （保持包结构一致）


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """一步式配置：确认即添加。"""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """用户点「添加集成」进入；直接创建条目，不需要填表单。"""
        if user_input is None:
            return self.async_show_form(step_id="user")
        # 同一集成只允许一条配置
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")
        return self.async_create_entry(
            title="June.Ⅰ 户型中枢",
            data={},
        )
