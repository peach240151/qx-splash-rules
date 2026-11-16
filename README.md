# QX-Splash-AdBlock · 综合开屏广告拦截规则

面向 **Quantumult X（圈 X）** 的**开屏广告拦截**方案，聚合 **hwind2021 + 墨鱼去开屏 + 神机(DivineEngine)** 三家上游，含两份参考 Orz-3 小白配置结构改写的**懒人配置**（无节点版 / 海外国内分流版），以及三份一次性合并快照。

**懒人配置的分流与重写已全部改为上游每日更新链接**，导入一次即可自动跟进上游更新。

## 🔗 订阅地址（可直接复制）

### 🛋️ 方式一：一键导入懒人配置（推荐）

```
https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Lazy.conf
```

QX → 右下角「风车」→「配置文件」→ 右上角 `+` → 「从 URL 下载」→ 粘贴上面链接。配置内含 6 条上游订阅（hwind + 墨鱼 + 神机 三家）、470 个 MITM 主机名与国内 DNS 优化，一次配好。**不需要节点，装了就能去开屏。**

> ⚠️ **导入完整配置文件会替换你现有的全部配置**（节点订阅、策略组、分流等），导入前请先长按现有配置导出备份。若只想把规则合并进现有配置，把 `QX-Lazy.conf` 里的 `[filter_remote]`、`[rewrite_remote]`、`[mitm]` 三段复制到你自己的 `.conf` 即可。
>
> ⚠️ 想让「秒跳过」生效，还需：设置 → MITM → 开启 → 安装并信任证书。若不想解密流量，把 `[rewrite_remote]` 两条的 `enabled` 改成 `false`，只用分流即可。

### 🌐 方式一·分流版：海外走节点 / 国内直连（需要机场订阅）

```
https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Lazy-Global.conf
```

在方式一的基础上增加了 `[server_remote]` 订阅占位、4 条 RuleGo 国内外分流规则、`final, proxy`。**去广告部分与方式一完全一致**，只是多了节点分流能力。使用前必须把自己的机场订阅填进 `[server_remote]`，否则海外流量无节点可用。详见下方「🌐 海外 / 国内节点分流」章节。

> 只想纯净去开屏、没有节点 → 用 `QX-Lazy.conf`；想同时让海外网站走代理 → 用 `QX-Lazy-Global.conf`。两份互相独立，导入哪份都不会改动另一份。

### 方式二：本仓库合并快照（可选，一次性）

- **分流规则（无需 MITM）**
  `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Splash-AdBlock.list`
- **重写规则（需 MITM）**
  `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Splash-AdBlock.conf`

> 这两份是把上游规则下载后合并去重生成的**静态快照**，不会自动更新。想长期保持最新，请用方式一的懒人配置，或直接订阅下方上游链接。

## 🔄 上游链接清单（懒人配置实际订阅的内容）

| 类型 | 上游地址 | tag | 说明 |
|---|---|---|---|
| 分流 | `https://raw.githubusercontent.com/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/filter/Splash-Killer.list` | 开屏广告拦截 | ~470 条，20+ 广告 SDK 域名，每日更新 |
| 分流 | `https://raw.githubusercontent.com/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/filter/BlockHttpDNS.list` | HTTPDNS阻断 | ~62 条，防 App 用 HTTPDNS 绕过本地解析 |
| 重写 | `https://raw.githubusercontent.com/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/rewrite/AdBlock-Splash.conf` | hwind开屏重写 | ~112 条精准开屏接口 |
| 重写 | `https://ddgksf2013.top/rewrite/StartUpAds.conf` | 墨鱼去开屏2.0 | 400+ 逐 App 开屏接口，需 QX UA 才返回规则 |
| 分流 | `https://raw.githubusercontent.com/HengLiu2282/DivineEngine/master/Quantumult/Filter/Guard/Advertising.list` | 神机去广告 | 神机(DivineEngine) 通用广告/追踪域名 640 条，原仓库已下架，采用镜像 |
| 重写 | `https://raw.githubusercontent.com/HengLiu2282/DivineEngine/master/Quantumult/Rewrite/Block/Advertising.conf` | 神机去广告重写 | 神机通用去广告重写 248 条，范围广、较激进 |

六条均设 `update-interval=86400`（每日自动拉取）。墨鱼那条加 `opt-parser=true`（与 Orz-3 原版一致），QX 请求时会自带 `Quantumult-X` UA，因此能取到真规则而非站点网页。

分流版额外订阅 4 条 [ConnersHua/RuleGo](https://github.com/ConnersHua/RuleGo) 规则（见下表），`update-interval=172800`、`opt-parser=true`（RuleGo 为 Surge 格式，需解析器转换）。

| 顺序 | 规则 | force-policy | 作用 |
|---|---|---|---|
| ② | `Surge/Ruleset/Direct+.list` | `direct` | 强制直连修正（国内 CDN、统计域名等，优先于任何代理规则） |
| ② | `Surge/Ruleset/Direct.list` | `direct` | 国内网站域名直连 |
| ③ | `Surge/Ruleset/Proxy.list` | `proxy` | 海外网站域名走代理 |
| ③ | `Surge/Ruleset/Proxy+.list` | `proxy` | 代理修正（GEOIP,GOOGLE） |

> 国内网络若 `raw.githubusercontent.com` 不稳，可在前面加加速前缀 `https://gh.idayer.com/`，例如
> `https://gh.idayer.com/https://raw.githubusercontent.com/hwind2021/...`。

## 📦 文件说明

| 文件 | 类型 | 是否需 MITM | 说明 |
|---|---|---|---|
| `QX-Lazy.conf` | 完整配置 | 重写部分需要 | **懒人配置（无节点版）**。参考 Orz-3 骨架改写，去掉依赖机场节点的策略组，不装节点也能用；7 条上游订阅（含 MITM 主机名订阅，MITM 不再内联）+ 国内 DNS 优化，`final, direct`。 |
| `QX-Lazy-Global.conf` | 完整配置 | 重写部分需要 | **懒人配置（海外/国内分流版）**。在上面基础上加 `[server_remote]` 占位 + 4 条 RuleGo 分流规则，`final, proxy`；需自备机场订阅。 |
| `QX-Splash-AdBlock.list` | 分流规则 | ❌ 不需要 | 一次性快照。1141 条去重规则：295 HOST + 769 HOST-SUFFIX + 31 HOST-KEYWORD + 41 IP-CIDR + 4 IP6-CIDR + 1 USER-AGENT，含墨鱼补充分流行与神机通用去广告域名，并阻断 HTTPDNS 绕过。 |
| `QX-Splash-AdBlock.conf` | 重写规则 | ✅ 需要 | 一次性快照。835 条去重重写（hwind 112 + 墨鱼 475 + 神机 248）+ 470 个 MITM 主机。 |
| `QX-MITM-Hosts.conf` | 重写资源 | — | **MITM 主机名订阅（免重导）**。本身是一条重写资源，只托管 470 个 MITM 主机名；在 QX「设置 → 重写 → 添加资源」加一次后，QX 会自动合并其中的 hostname 并随订阅每日更新，以后更新主机名无需重导整份配置。 |

## 🚀 使用方法（单独订阅快照时）

> 低风险优化（2026-11-16）：[mitm] 已从 704 精简到 470 —— 剔除「已被分流 REJECT」（本就不会进入 MITM）与「无任何重写命中」的冗余主机名，并去掉 hwind 原生 .list 上多余的 opt-parser（Splash-Killer / BlockHttpDNS 为 QX 原生格式，无需解析器；神机 Surge 格式广告列表保留 opt-parser）。现存全部重写的目标主机仍被完整覆盖，功能不变。

### 一、订阅分流规则（必装，无需 MITM）

1. 打开 Quantumult X → 右下角「风车」→「配置文件」→ 右上角 `+` → 选择「**远程资源**」
2. 类型选「**分流规则**」，URL 填：
   ```
   https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Splash-AdBlock.list
   ```
3. 策略保持默认 `REJECT`，保存 → 回首页「风车」→ 长按该资源 → 更新。

### 二、（可选）叠加开屏重写规则（需 MITM）

1. 同样在「远程资源」新增一条，类型选「**重写规则**」：
   ```
   https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Splash-AdBlock.conf
   ```
2. 「设置」→「MITM」→ 开启，并把 `.conf` 里 `[mitm]` 段的 `hostname` 全部加入，然后安装并信任证书。

> ⚠️ MITM 主机清单较长（470 条），开启后 QX 会解密这些域名的流量。若只想去开屏、担心性能或隐私，可只用分流规则，或按需裁剪 hostname。
>
> ⚠️ 部分重写规则为 `script-response-body`，依赖 [ddgksf2013/Scripts](https://github.com/ddgksf2013/Scripts) 仓库中的 JS 脚本，请确保 QX 能访问 GitHub raw。

## 🛋️ 懒人配置说明

`QX-Lazy.conf` 参考 [Orz-3/QuantumultX · Orz-3.conf](https://github.com/Orz-3/QuantumultX/blob/master/Orz-3.conf) 的「小白配置」结构，保留其 `[general]` 国内 DNS 优化、`dns_exclusion_list`、`[filter_local]` 本地直连兜底等写法，做了以下改动：

1. **去掉 `[policy]` 策略组与 RuleGo 海外分流**——原版依赖机场节点，本配置聚焦去开屏，无节点也能正常工作；
2. **`final` 由「黑白名单」改为 `direct`**，避免没有节点时无法联网；
3. **只保留开屏相关项，分流 / 重写全部改为上游每日更新链接**（见上方清单），不再引用本仓库的一次性合并快照；
4. **`[server_remote]` 留空**，已有机场订阅可自行按注释格式添加；
5. **`[mitm]` 内联 470 个 hostname**（取自 hwind MITM.list + 墨鱼 StartUpAds.conf + 神机 Advertising.conf）。这段是静态文本，上游新增域名时可重新导入本配置或手动补充。

## 🌐 海外 / 国内节点分流

`QX-Lazy-Global.conf` 是分流版。QX 的分流本质是「**规则命中 → 指定策略 → 未命中走 final**」，四块拼起来：

| 部件 | 段 | 作用 |
|---|---|---|
| 节点来源 | `[server_remote]` | 机场订阅，提供可用的代理节点 |
| 策略 | `[policy]` 或内置 `proxy` / `direct` / `reject` | `proxy` = 走当前选中节点，`direct` = 直连，`reject` = 丢弃 |
| 路由规则 | `[filter_remote]` 的 `force-policy=`、`[filter_local]` | 命中即停，按配置顺序自上而下匹配 |
| 兜底 | `final, proxy` | 所有规则都没匹配到时的默认出口 |

本配置采用的「极简二分」：

```
① 开屏广告 / HTTPDNS        → REJECT   （排最前，广告无论国内海外都拦）
② Direct+.list / Direct.list → DIRECT   （直连修正 + 国内域名）
③ Proxy.list / Proxy+.list   → PROXY    （海外域名 + 代理修正）
④ geoip, cn                  → DIRECT   （国内 IP 兜底，[filter_local]）
⑤ final                      → PROXY    （其余全部走节点）
```

关键点：

- **核心不是域名表，而是 `geoip, cn, direct` + `final, proxy`**：解析到国内 IP 的直连，其余一律走节点。RuleGo 的 `Direct.list` / `Proxy.list` 只是补例外（国内域名强制直连、海外域名强制代理），表本身很小（分别 24 / 513 条），别指望它覆盖全网。
- **REJECT 必须排最前**：QX 规则命中即停，广告规则若被直连/代理规则抢先命中就拦不住了，所以两条开屏 reject 放在 `[filter_remote]` 第一行。
- **`[policy]` 可以完全不用**：内置 `proxy` 就够做二分了，QX 首页选中哪个节点，`proxy` 就用哪个。配置里 `[policy]` 段留了一组注释掉的 Orz-3 按地区自动分组写法（`available` + `server-tag-regex` 按节点名里的 港/台/日/坡/美 关键字分组），需要「AI 走美国节点、番剧走港台节点」这类精细控制时再启用，并把 `force-policy=proxy` 改成对应策略组名。
- **必须有节点**：`[server_remote]` 是占位注释，导入后请取消注释换成自己的订阅链接（`https://你的订阅链接, tag=机场, update-interval=172800, enabled=true`）。没填节点时 `proxy` 无服务器可用，海外网站会连不上；若临时只想国内直连，把 `final, proxy` 改成 `final, direct` 即可退回无节点版行为。
- **顺序敏感性**：`Direct+.list`（强制直连修正）要放在 `Proxy.list` 之前，否则国内 CDN/统计域名会被误送进代理；`final` 永远最后。
- **DNS**：`[dns]` 用国内 DNS（119.29.29.29 / 180.184.1.1 / 223.5.5.5）并配了 `circumvent-ipv4-answer` 污染 IP 黑名单；走 `proxy` 的连接由节点远端解析，本地 DNS 结果不影响海外域名。

> ⚠️ 分流版同样会**替换你现有的全部配置**（节点、策略组、分流都会没），导入前务必先导出备份。若已有自己的分流配置，只需把这份的 `[filter_remote]`（7 条）、`[rewrite_remote]`（3 条）、`[mitm]` 三段复制过去，别整份导入。

## 📊 规则组成

- **HOST / HOST-SUFFIX / HOST-KEYWORD**：广告 SDK 域名直连层拦截（穿山甲 pangolin、广点通 gdt、百青藤 mobads、快手、阿里妈妈 alimama、taobao adashx 埋点、Google/Facebook/AppLovin/Unity/Vungle/ironSource/Mintegral 等）。
- **IP-CIDR / IP6-CIDR**：兜底拦截已知广告服务器 IP。
- **HTTPDNS 阻断**：防止头条/阿里/腾讯系 App 用 HTTPDNS 绕过本地 DNS 解析广告域名（不拦这一层，前面效果会打折）。
- **神机通用去广告**：DivineEngine Advertising.list 的 640 条域名（追踪、广告 SDK、埋点等），补充开屏之外的常规广告，较激进，遇误杀可关闭该订阅。
- **重写 A（hwind2021）**：对 `/splash/*`、`startup ad`、各 App 具体开屏接口（美团/京东/淘宝/携程/小红书/知乎/微博/高德 等）返回空响应。
- **重写 B（墨鱼去开屏 2.0）**：逐 App 整理的开屏接口，400+ 应用按 `0~9 / A~Z` 分组并保留 `# > App名` 注释，便于排查与加白名单。
- **重写 C（神机 / DivineEngine）**：通用去广告重写 248 条（各 App 广告接口、`mp.weixin.qq.com` 广告字段等），范围比开屏更广、较激进。

## 🙏 数据来源与致谢

- [hwind2021/QuantumultX-AdBlock-CN](https://github.com/hwind2021/QuantumultX-AdBlock-CN)（Splash-Killer、BlockHttpDNS、AdBlock-Splash、MITM，每日 04:00 UTC+8 自动更新）
- [ddgksf2013/ddgksf2013](https://github.com/ddgksf2013/ddgksf2013) · [墨鱼去开屏 2.0 / StartUpAds.conf](https://ddgksf2013.top/rewrite/StartUpAds.conf)（已抓包 400 余应用去开屏）
- DivineEngine 神机规则（原仓库已下架，采用镜像 [HengLiu2282/DivineEngine](https://github.com/HengLiu2282/DivineEngine) 的 `Quantumult/*/Guard/Advertising` 系列）
- 懒人配置结构参考：[Orz-3/QuantumultX · Orz-3.conf](https://github.com/Orz-3/QuantumultX/blob/master/Orz-3.conf)
- 国内外分流规则：[ConnersHua/RuleGo](https://github.com/ConnersHua/RuleGo)（Surge/Ruleset）
- 上游：[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)、[privacy-protection-tools/anti-AD](https://github.com/privacy-protection-tools/anti-AD)

> 墨鱼原项目声明：**本库内容禁止公众号、自媒体进行任何形式的转载或发布**，此处仅作个人使用规则的合并引用，如需引用请遵守原作者要求并注明出处。

## ⚠️ 免责声明

- 本项目仅供学习交流，规则数据均来自公开开源项目。
- 请在遵守当地法律法规的前提下使用，请勿用于商业或违法用途。
- 广告是许多免费服务的主要收入来源，如认可某 App，建议加入白名单或购买会员支持开发者。
- 使用本规则可能导致部分 App 功能异常，请自行判断风险。

## 🔧 免重导更新 MITM 主机名（推荐）

QX 的 `[mitm]` 主机名默认写在配置里，改了它就要重新导入整份配置。官方支持**重写资源自带 `hostname` 行并自动合并**（见 QX `sample-import-rewrite.snippet`），所以可以把主机名单独做成一条订阅：

1. 本仓库的 `QX-MITM-Hosts.conf` 就是一条重写资源，只托管 470 个 MITM 主机名。
2. **新版懒人配置（`QX-Lazy.conf` / `QX-Lazy-Global.conf`）已内置这条订阅**，导入即生效，无需任何手动操作。
3. 如果你**沿用的是旧配置、又不想重导**：在 QX「设置 → 重写 → 右上角 ＋ → 添加资源」手动加一次：
   `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-MITM-Hosts.conf`，tag 随意（如 `MITM主机名`）。
4. 之后它随订阅每日自动更新；以后增删 MITM 主机名只改这个文件，**不用再重导整份配置**。

> 新版懒人配置已**不再内联** MITM 主机名，完全由该订阅托管；只有沿用旧配置、又不想重导时，才需要手动加一次。

## 📅 更新

- `QX-Lazy.conf` / `QX-Lazy-Global.conf` 订阅的是上游每日更新源，导入后无需重新导入配置。
- MITM 主机名：加一次 `QX-MITM-Hosts.conf` 订阅即可随订阅自动更新，无需重导整份配置（详见上节）。
- `QX-Splash-AdBlock.list` / `.conf` 为一次性快照，如需更新需重新生成推送。
