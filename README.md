# June.Ⅰ 户型中枢 (Home Assistant 集成)

为微信小程序「June.Ⅰ」与 3D 户型编辑器提供数据总线的 Home Assistant 自定义集成。

> **当前版本：v1.3.4** · 版本号跟随小程序 June.Ⅰ 一起走
> 校验接口：`GET /api/june_i/house` 返回 JSON 即表示链路正常

## 功能

- **侧边栏编辑器**：启用后在 HA 侧边栏出现「户型编辑器」入口（iframe 静态托管，无需另起服务）
- **数据总线**：
  - `GET/PUT /api/june_i/house` — house.json 户型数据存取
  - `GET/PUT /api/june_i/render` — 预渲染户型图（PNG + 热区 manifest，base64 传输）
  - `GET /api/june_i/media/{name}` — 静态资源
- 编辑器内「存到 HA / 上传到 HA」一键保存，小程序端自动拉取，无需手动拷贝文件

## 安装（HACS 自定义仓库）

1. 确保已安装 [HACS](https://hacs.xyz)
2. HACS → 右上角 ⋮ → **自定义存储库** (Custom repositories)
3. 仓库地址填本仓库 URL，类别选 **集成 (Integration)**，添加
4. 在 HACS 集成列表中找到「June.Ⅰ 户型中枢」→ **下载**
5. **重启 Home Assistant**
6. 启用集成（二选一，推荐第一种）：
   - **界面方式（零代码）**：设置 → 设备与服务 → 右下角「+ 添加集成」→ 搜「June」→ 选择「June.Ⅰ 户型中枢」→ 直接点**提交**（无需填写）
   - **yaml 方式**：`configuration.yaml` 添加一行 `june_i:`，再重启
7. 侧边栏出现「**户型编辑器**」，点进去即可使用

## 手动安装

把 `custom_components/june_i/` 整个目录复制到 HA 配置目录下的 `custom_components/june_i/`，重启 HA，按上面的第 6 步启用。

## 更新

HACS → 「June.Ⅰ 户型中枢」→ **更新** → 重启 HA。户型数据存在 `.storage/june_i.data.json`，更新/重装都不会丢。

## 配套

- 小程序端（June.Ⅰ）通过 `http://<HA地址>:8123/api/june_i/...` 自动同步，URL 与 token 在 `june-i/utils/config.js`
- 编辑器机位设置（方向/俯仰/缩放/留白）导出的预渲染图会一并上传，小程序端零改动

## 更新日志

<!-- CHANGELOG -->
- **v1.3.4**（2026-11-22）修复侧边栏面板注册（适配新版 HA API，失败时发通知）；图标改为「June.Ⅰ」文字版（真字体渲染 + 户型底纹）
- **v1.3.3**（2026-11-22）支持「界面添加集成」（config_flow），不再必须改 configuration.yaml
- **v1.3.2**（2026-11-22）编辑器导出改为线条生成版渲染；娃娃屋隐墙；预渲染图重烘
- **v1.3.1**（2026-11-21）小程序瘦身：移除全部 WebGL 试验功能，只保留预渲染图链路
- **v1.3.0**（2026-11-21）预渲染方案 + HA 数据总线首版
