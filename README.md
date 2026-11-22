# QX-Splash-AdBlock · 配置方法

一份**大肥鱼**写的、面向 **Quantumult X** 的开屏广告拦截规则集（聚合 hwind / 墨鱼 / 神机 / 运营商广告 / 番茄小说）。

## 一、Quantumult X

### 订阅地址

| 用途 | 地址 |
|---|---|
| 懒人配置（无节点，装了就能用） | `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Lazy.conf` |
| 懒人配置·海外分流版（需机场订阅） | `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Lazy-Global.conf` |
| 分流规则快照（无需 MITM） | `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Splash-AdBlock.list` |
| 重写规则快照（需 MITM） | `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/QX-Splash-AdBlock.conf` |

### 配置步骤

**方式 A · 一键导入懒人配置（推荐）**

1. QX → 右下角「风车」→「配置文件」→ 右上角 `+` →「从 URL 下载」→ 粘贴上面的 `QX-Lazy.conf`（想海外走节点就用 `QX-Lazy-Global.conf`）。
2. 想让「秒跳过」生效：设置 → MITM → 开启 → 安装并信任证书。

**方式 B · 只订阅快照**

1. 风车 →「配置文件」→ 右上角 `+` →「远程资源」→ 类型选「分流规则」→ 填 `QX-Splash-AdBlock.list` → 策略保持 `REJECT` → 保存后长按该资源更新（无需 MITM）。
2. 需要重写再添一条「重写规则」→ 填 `QX-Splash-AdBlock.conf` → 设置 → MITM → 开启 → 导入其中 `hostname` 并安装信任证书。

### 注意

- ⚠️ 导入「整份配置」会**替换你现有的全部配置**（节点、策略组、分流等），导入前先长按现有配置导出备份。只想合并规则：把 `[filter_remote]`、`[rewrite_remote]`、`[mitm]` 三段复制进你自己的 `.conf`。
- 分流版导入后，请把 `[server_remote]` 里的占位注释换成自己的机场订阅链接，否则海外无节点可用。
- 只想国内纯净去开屏、没有节点 → 用 `QX-Lazy.conf`；要海外走代理 → 用 `QX-Lazy-Global.conf`，两份互相独立。
- 不想解密流量可只用分流（方式 B 第 1 步），或把 `[rewrite_remote]` 各条 `enabled` 改为 `false`。

## 二、Shadowrocket（小火箭）

| 文件 | 用途 |
|---|---|
| `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/shadowrocket/Shadowrocket-AdBlock.conf` | 完整配置，直接导入（含 `[General]`/`[Rule]`/`[URL Rewrite]`/`[MITM]`，`FINAL,DIRECT` 纯去广告） |
| `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/shadowrocket/Shadowrocket-AdBlock.list` | 规则集，用于 `RULE-SET` 远程订阅 |
| `https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/shadowrocket/Shadowrocket-Rewrite.conf` | 重写补充片段，已有配置时合并用 |

导入步骤与注意事项见 [shadowrocket/README.md](shadowrocket/README.md)。

## 三、更新

懒人配置里的远程资源（1 条分流 + 1 条重写，MITM 主机名内联在重写源末尾）全部指向本仓库快照，由 GitHub Actions 每天 04:00（UTC+8）跟随上游重建，导入后无需重新导入。

重写规则里引用的第三方 JS 已全部镜像到本仓库 `scripts/js/`，上游删库或改内容都不影响使用（见 [NOTICE.md](NOTICE.md)）。

---

## 数据来源与致谢

- [hwind2021/QuantumultX-AdBlock-CN](https://github.com/hwind2021/QuantumultX-AdBlock-CN)（Splash-Killer / BlockHttpDNS / AdBlock-Splash / MITM，每日更新）
- [ddgksf2013/ddgksf2013](https://github.com/ddgksf2013/ddgksf2013) · [墨鱼去开屏 2.0 / StartUpAds.conf](https://ddgksf2013.top/rewrite/StartUpAds.conf)（已抓包 400 余应用去开屏）
- 神机 DivineEngine（原仓库已下架，采用镜像 [HengLiu2282/DivineEngine](https://github.com/HengLiu2282/DivineEngine) 的 `Quantumult/*/Guard/Advertising` 系列）
- [Orz-3/QuantumultX · Orz-3.conf](https://github.com/Orz-3/QuantumultX/blob/master/Orz-3.conf)（懒人配置结构参考）
- [ConnersHua/RuleGo](https://github.com/ConnersHua/RuleGo)（国内外分流规则）
- [zqzess/rule_for_quantumultX](https://github.com/zqzess/rule_for_quantumultX)（番茄小说去广告 FanQieNovel.snippet / qxrewrite）
- 运营商广告/统计域名：从 [privacy-protection-tools/anti-AD](https://github.com/privacy-protection-tools/anti-AD) 的 anti-ad-domains.txt 筛出，另含常见 DNS 劫持域名 `wscdns.com/.net`
- 上游：[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)、[privacy-protection-tools/anti-AD](https://github.com/privacy-protection-tools/anti-AD)

> 墨鱼原项目声明：**本库内容禁止公众号、自媒体进行任何形式的转载或发布**，此处仅作个人使用规则的合并引用。规则数据版权归各上游作者，详见 [NOTICE.md](NOTICE.md) 与 [LICENSE](LICENSE)。

## 免责声明

- 本项目仅供学习交流，规则数据均来自公开开源项目。
- 请在遵守当地法律法规的前提下使用，请勿用于商业或违法用途。
- 广告是许多免费服务的主要收入来源，如认可某 App，建议加入白名单或购买会员支持开发者。
- 使用本规则可能导致部分 App 功能异常，请自行判断风险。
