# June.Ⅰ 户型中枢 (Home Assistant 集成)

为微信小程序「June.Ⅰ」与 3D 户型编辑器提供数据总线的 Home Assistant 自定义集成。

## 功能

- **侧边栏编辑器**：安装后在 HA 侧边栏出现「户型编辑器」入口（iframe 静态托管，无需另起服务）
- **数据总线**：
  - `GET/PUT /api/june_i/house` — house.json 户型数据存取
  - `GET/PUT /api/june_i/render` — 预渲染户型图（PNG + 热区 manifest，base64 传输）
  - `GET /api/june_i/media/{name}` — 静态资源
- 编辑器内「存到 HA / 上传到 HA」一键保存，小程序端自动拉取，无需手动拷贝文件

## 安装（HACS 自定义仓库）

1. 确保已安装 [HACS](https://hacs.xyz)
2. HACS → 右上角 ⋮ → **自定义存储库** (Custom repositories)
3. 仓库地址填本仓库 URL，类别选 **集成 (Integration)**
4. 在 HACS 集成列表中找到「June.Ⅰ 户型中枢」→ 下载
5. **重启 Home Assistant**
6. `configuration.yaml` 添加：

```yaml
june_i:
```

7. 再次重启，侧边栏出现「户型编辑器」

## 手动安装

把 `custom_components/june_i/` 整个目录复制到 HA 配置目录下的 `custom_components/june_i/`，重启 HA，`configuration.yaml` 添加 `june_i:` 后再重启。

## 配套

- 小程序端（June.Ⅰ）通过 `http://<HA地址>:8123/api/june_i/...` 自动同步
- 编辑器机位设置（方向/俯仰/缩放/留白）导出的预渲染图会一并上传
