# NOTICE · 数据来源与许可说明

本仓库聚合了多家上游的广告拦截规则，规则数据版权归各上游作者，**本仓库不对规则数据主张版权**。

## 上游与许可

1. **hwind2021/QuantumultX-AdBlock-CN**
   - 采用其 Splash-Killer.list / BlockHttpDNS.list / AdBlock-Splash.conf / MITM.list。
   - LICENSE 正文为 MIT，但**仅覆盖 `tools/` 目录代码**；「规则数据并非原创，各上游保留自身许可，二次分发请保留上游来源声明」。
   - 其规则数据追溯上游：blackmatrix7/ios_rule_script、privacy-protection-tools/anti-AD 等。

2. **ddgksf2013/ddgksf2013（墨鱼去开屏 2.0 / StartUpAds.conf）**
   - 原项目 README 声明「本库内容禁止公众号、自媒体进行任何形式的转载或发布」。
   - 本仓库仅作**个人使用**的规则合并引用，未用于公众号/自媒体发布；如需再分发请取得作者许可并注明出处。

3. **DivineEngine（神机规则）**
   - 原仓库已下架，采用第三方镜像 HengLiu2282/DivineEngine 的 `Quantumult/*/Guard/Advertising` 系列。
   - 镜像来源未经原作者背书，使用需自行评估可信度。

4. **ConnersHua/RuleGo**（分流版额外使用）
   - 采用 Surge/Ruleset 下的 Direct+/Direct/Proxy/Proxy+ 列表。

5. **KOP-XIAO/QuantumultX**（resource-parser.js）
   - 已固定到 commit `cce2996b0064361829b16c2866b5cfc98a1b13b9`。

## 远程可执行脚本

`.conf` 快照中的 `script-response-body` / `script-response-header` / `script-analyze-echo-response`
规则依赖以下仓库的 JS，已固定到 commit SHA：
- ddgksf2013/Scripts @ `203e38b7b8dd1082ececbd17de3aeb587ac2826c`
- app2smile/rules @ `df6366a7024e0b3f0aa3510c5b791eea6f3cba89`

这些脚本在 Quantumult X 本地执行，可读取解密后的请求/响应报文。请仅在信任上述来源时启用。

## 本仓库自身

本仓库的脚本、配置骨架与文档编排代码采用 MIT 许可（见 LICENSE）。规则数据不在 MIT 覆盖范围内。

## scripts/js/ — 第三方脚本镜像

`scripts/js/` 下的脚本镜像自以下上游，仅用于确保本规则引用的脚本在上游删改后仍可用；
脚本版权归原作者，遵循其仓库原有许可：

- `ddgksf2013/Scripts`（多为 `master` 分支下的 js，如 coolapk.js、startup.js、zhihu_openads.js 等）
- `app2smile/rules`（`js/baidumap.js`）

`scripts/build.py` 每次构建会自动同步这些文件：下载失败时沿用仓库已有镜像，网络仍失败才回退指向上游地址。

## 已停用脚本（永不触发的规则）

以下 8 条 `script-*` 规则及其脚本已从构建产物中移除。原因是**它们本来就一条都不会触发**，
删除前后实际拦截行为完全一致，只是去掉了死代码：

| 脚本 | 原因 |
|---|---|
| `abchina.js` | 主机 `mobilepaas.abchina.com.cn` 按「银行域」策略剔出 MITM，解不了密 |
| `quark.js` | 主机 `open-cms-api.(uc\|quark).cn` 带交替、且上游名与 MITM 精确主机名对不上 |
| `12306.js` | 主机 `ad.12306.cn` 已被分流 `REJECT`，连接在 TLS 握手前就断了 |
| `555Ad.js` / `amdc.js` | 上游模式 `[a-zA-Z0-9_-]+(\.[...]){1,4}` 是泛主机通配，没有具体 hostname 可 MITM |
| `ahfs.js` / `fly.js` / `hanglvzongheng.js` | 上游模式 `.*(xbwpys\|ahhhhfs)\.com`、`.*flyert.*`、`.*umetrip\.com\.cn` 同为通配主机 |

如需恢复其中某条，向 `scripts/build.py` 的 `DEAD_SCRIPTS` 移除对应文件名，
并确保该规则的主机能出现在 MITM 清单里，否则规则依旧不会生效。
