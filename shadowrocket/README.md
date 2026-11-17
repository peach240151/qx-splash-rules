# QX-Splash-AdBlock · Shadowrocket（小火箭）版

由本仓库的 QX 综合去开屏规则（hwind2021 + 墨鱼去开屏2.0 + 神机/DivineEngine）转换而来的 **Shadowrocket 原生格式**。

## 文件说明

| 文件 | 用途 |
|---|---|
| `Shadowrocket-AdBlock.conf` | **完整配置**。含 `[General]` / `[Rule]` / `[URL Rewrite]` / `[MITM]`，默认 `FINAL,DIRECT`（纯去广告，不接管代理）。适合直接导入、开箱即用。 |
| `Shadowrocket-AdBlock.list` | **纯规则集**（1183 条，Surge/Shadowrocket 规则格式，全部 `REJECT`）。用于远程 `RULE-SET` 订阅，或并入你自己已有的配置。 |
| `Shadowrocket-Rewrite.conf` | **重写补充片段**（仅 `[URL Rewrite]` + `[MITM]` 两段）。你已有自己的配置时，把这两段合并进去即可。 |

## 导入方式

### 方式 A：直接导入完整配置（最省事）
1. Shadowrocket → 底部「配置」→ 右上角 `+` → 「从 URL 下载」或「从文件导入」。
2. 填：`https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/shadowrocket/Shadowrocket-AdBlock.conf`
3. 选中该配置 → 设为活动配置。
4. 想「秒跳过」广告：首页 → 设置 → **MITM** → 开启 → 生成/安装证书 → 到 iOS「设置 → 通用 → 关于本机 → 证书信任设置」里信任该证书。

### 方式 B：只加规则订阅（保留你自己的代理）
在你当前配置的 `[Rule]` 段加入一行（Shadowrocket 支持远程规则集）：
```
RULE-SET,https://raw.githubusercontent.com/peach240151/qx-splash-rules/main/shadowrocket/Shadowrocket-AdBlock.list,REJECT
```
或把 `Shadowrocket-AdBlock.list` 里的规则行直接粘贴进 `[Rule]`。

### 方式 C：只加重写（已有配置不动）
把 `Shadowrocket-Rewrite.conf` 的 `[URL Rewrite]` 与 `[MITM]` 两段内容，合并进你现有配置的同名段落后保存、重载。

## 重要注意事项

1. **776 条 URL 重写需要 MITM**：不开启 MITM 并信任证书，重写（`url reject*`）不会生效；此时只有分流规则（1183 条 `REJECT`）起作用。
2. **脚本规则已省略**：QX 的 **27 条 `script-response-body`** 依赖 QX 脚本 API，Shadowrocket 不兼容，已从本版本剔除。这部分 App 的开屏拦截会缺失（通常仍被分流 `REJECT` 兜底），其余 **776 条** 重写正常。
3. **动作沿用 Surge 语法**：`reject` / `reject-200` / `reject-img` / `reject-dict` 等为 Surge/Shadowrocket 通用写法；若极个别旧版 Shadowrocket 报错，可统一替换为 `reject`。
4. **`FINAL,DIRECT` 表示不接管代理**：想要科学上网，请把 `FINAL,DIRECT` 改成你的策略组/节点，或改用你自己的主配置 + 方式 B/C 叠加去广告。
5. **安全性**：MITM 会解密这些域名的流量；已剔除银行/政务/医疗/支付类域名（见 `NOTICE.md`）。
6. **静态快照**：这三个文件不会自动更新，需要时重新生成。
7. **授权**：规则数据版权归各上游作者，详见仓库根目录 `NOTICE.md` 与 `LICENSE`。墨鱼原项目禁止公众号/自媒体转载。

## 与 QX 版的字段映射

| QX 写法 | Shadowrocket 写法 |
|---|---|
| `HOST,example.com,REJECT` | `DOMAIN,example.com,REJECT` |
| `HOST-SUFFIX,example.com,REJECT` | `DOMAIN-SUFFIX,example.com,REJECT` |
| `HOST-KEYWORD,ads,REJECT` | `DOMAIN-KEYWORD,ads,REJECT` |
| `IP-CIDR,1.2.3.0/24,REJECT` | `IP-CIDR,1.2.3.0/24,REJECT,no-resolve` |
| `IP6-CIDR,...,REJECT` | `IP6-CIDR,...,REJECT,no-resolve` |
| `[rewrite_local]` + `pattern url reject` | `[URL Rewrite]` + `pattern url reject`（同语法） |
| `[mitm] hostname = ...` | `[MITM] hostname = ...` |
