# -*- coding: utf-8 -*-
"""
Consolidated generator for the QX / Shadowrocket ad-block ruleset.

Pulls every upstream subscription (hwind2021, 墨鱼, 神机/DivineEngine, 番茄小说/zqzess),
merges + de-duplicates, applies the security/regex fixes, and rewrites:
  QX-Splash-AdBlock.list / QX-Splash-AdBlock.conf / QX-MITM-Hosts.conf
  shadowrocket/Shadowrocket-AdBlock.conf / .list / -Rewrite.conf
  README.md numeric aggregates  (best-effort regex)
No third-party deps (stdlib only) so it runs in GitHub Actions.

Env:
  QX_ROOT        repo root (default: parent of this script)
  QX_LOCAL_DIR   if set, read sources from this local dir instead of downloading
"""
import io, os, re, sys, time, datetime, urllib.request

ROOT = os.environ.get('QX_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL = os.environ.get('QX_LOCAL_DIR', '').strip()
UA_QX = 'Quantumult-X/1.0'

GH = 'https://raw.githubusercontent.com'
CDN = 'https://cdn.jsdelivr.net/gh'

# 本仓库地址：用于把重写里引用的第三方 JS 指向仓库内镜像（scripts/js/）
SELF_REPO = os.environ.get('GITHUB_REPOSITORY') or 'peach240151/qx-splash-rules'
SELF_RAW = GH + '/' + SELF_REPO + '/main'
JS_DIR = os.path.join(ROOT, 'scripts', 'js')

SOURCES = {
    'splash':      (GH + '/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/filter/Splash-Killer.list',
                    CDN + '/hwind2021/QuantumultX-AdBlock-CN@main/quantumultx/filter/Splash-Killer.list'),
    'httpdns':     (GH + '/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/filter/BlockHttpDNS.list',
                    CDN + '/hwind2021/QuantumultX-AdBlock-CN@main/quantumultx/filter/BlockHttpDNS.list'),
    'splash_rw':   (GH + '/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/rewrite/AdBlock-Splash.conf',
                    CDN + '/hwind2021/QuantumultX-AdBlock-CN@main/quantumultx/rewrite/AdBlock-Splash.conf'),
    'mitm':        (GH + '/hwind2021/QuantumultX-AdBlock-CN/main/quantumultx/mitm/MITM.list',
                    CDN + '/hwind2021/QuantumultX-AdBlock-CN@main/quantumultx/mitm/MITM.list'),
    'moyu':        ('https://ddgksf2013.top/rewrite/StartUpAds.conf', None),
    'shenji_list': (GH + '/HengLiu2282/DivineEngine/master/Quantumult/Filter/Guard/Advertising.list',
                    CDN + '/HengLiu2282/DivineEngine@master/Quantumult/Filter/Guard/Advertising.list'),
    'shenji_rw':   (GH + '/HengLiu2282/DivineEngine/master/Quantumult/Rewrite/Block/Advertising.conf',
                    CDN + '/HengLiu2282/DivineEngine@master/Quantumult/Rewrite/Block/Advertising.conf'),
    'fanqie_snip': (GH + '/zqzess/rule_for_quantumultX/master/QuantumultX/snippet/FanQieNovel.snippet',
                    CDN + '/zqzess/rule_for_quantumultX@master/QuantumultX/snippet/FanQieNovel.snippet'),
    'fanqie_rw':   (GH + '/zqzess/rule_for_quantumultX/master/QuantumultX/rewrite/FanQieNovel.qxrewrite',
                    CDN + '/zqzess/rule_for_quantumultX@master/QuantumultX/rewrite/FanQieNovel.qxrewrite'),
}
LOCAL_MAP = {
    'splash': 'Splash-Killer.list', 'httpdns': 'BlockHttpDNS.list',
    'splash_rw': 'AdBlock-Splash.conf', 'mitm': 'MITM.list',
    'moyu': 'StartUpAds-QX-UA.txt', 'shenji_list': 'shenji-advertising.list',
    'shenji_rw': 'shenji-advertising.conf',
    'fanqie_snip': os.path.join('zqzess', 'FanQieNovel.snippet'),
    'fanqie_rw': os.path.join('zqzess', 'FanQieNovel.qxrewrite'),
}

# ---------- hostname safety filter (same policy as review fix) ----------
BANK = ['ccb.com','bankcomm','spdb','ecitic','pingan.com','boc.cn','icbc.com','abchina','cmbchina',
        '95559','95588','95533','cebbank','psbc','bankofchina','citicbank','hxb.com','cgbchina',
        '95555','95595','95599','95566','95528','95580','95568']
GOV = ['gov.cn','.gov','nhsa','122.gov']
MED = ['91160','hospital','patientgate','.health','haodf','xywy.com','dxy.cn','guahao']
PAY = ['unionpay','95516']

def bad_host(h):
    x = h.strip().lower()
    if not x: return 'empty'
    if x.startswith('-'): return 'leading-dash'
    if '..' in x: return 'double-dot'
    if 'ailbaba' in x: return 'typo'
    if re.fullmatch(r'[0-9]{1,3}(\.[0-9]{1,3}){3}', x): return 'ip-literal'
    for b in BANK:
        if b in x: return 'bank'
    for g in GOV:
        if g in x: return 'gov'
    for m in MED:
        if m in x: return 'medical'
    for p in PAY:
        if p in x: return 'payment'
    if not re.fullmatch(r'[a-z0-9.*?_-]+', x): return 'invalid-char'
    if ('.' not in x) and (not x.startswith('*')): return 'no-dot'
    return None

def filter_hosts(hosts):
    keep, dropped, seen = [], {}, set()
    for h in hosts:
        hh = h.strip()
        if not hh: continue
        r = bad_host(hh)
        if r:
            dropped[r] = dropped.get(r, 0) + 1; continue
        k = hh.lower()
        if k in seen:
            dropped['dup'] = dropped.get('dup', 0) + 1; continue
        seen.add(k); keep.append(hh)
    return keep, dropped

def _tok(pat):
    p = re.sub(r'^\^', '', pat.strip())
    p = re.sub(r'^https?\??:', '', p)
    p = p.replace('\\/', '/')
    p = re.sub(r'^/+', '', p)
    m = re.match(r'^([^/?]*)', p)
    h = m.group(1).replace('\\', '').lower().strip() if m else ''
    if h == '' or h in ('https', 'http'):
        return None
    if re.fullmatch(r'\d+\.\d+\.\d+\.\d+', h):
        return ('exact', h)
    if re.fullmatch(r'[a-z0-9.\-]+', h) and '.' in h:
        return ('exact', h)
    dm = re.search(r'([a-z0-9\-]+\.)+[a-z0-9\-]+$', h)
    if dm and '.' in dm.group(0):
        return ('wild', dm.group(0))
    return None

def _covers(e, tok):
    ee = e.lower(); kind, val = tok
    if kind == 'exact':
        if '*' in ee:
            s = ee.lstrip('*').lstrip('.')
            return val == s or val.endswith('.' + s)
        return ee == val
    else:
        if '*' in ee:
            s = ee.lstrip('*').lstrip('.')
            return val == s or val.endswith('.' + s) or s.endswith('.' + val)
        return ee == val or ee.endswith('.' + val)

def prune_hosts(entries, buckets, rw_blocks):
    exact = {v.lower() for v in buckets['HOST']}
    suf = [v.lower() for v in buckets['HOST-SUFFIX']]
    kws = [v.lower() for v in buckets['HOST-KEYWORD']]
    def isrej(h):
        h = h.lower()
        if h in exact: return True
        for s in suf:
            if h == s or h.endswith('.' + s): return True
        for k in kws:
            if k in h: return True
        return False
    tokens = []
    for _, lines in rw_blocks:
        for s in lines:
            pat = re.split(r'\s+url\s+', s)[0].strip()
            tk = _tok(pat)
            if tk: tokens.append(tk)
    ntok = [tk for tk in tokens if not isrej(tk[1])]
    uniq = []
    seenE = set()
    for e in entries:
        ee = e.strip()
        if not ee: continue
        if ee.lower() in seenE: continue
        seenE.add(ee.lower()); uniq.append(ee)
    keep = [e for e in uniq if any(_covers(e, tk) for tk in ntok)]
    # ---- 零风险：被本列表内通配条目（*.x.com）覆盖的普通主机重复，删除 ----
    wilds = [e.lower().lstrip('*').lstrip('.') for e in keep if '*' in e]
    if wilds:
        keep = [e for e in keep
                if ('*' in e) or not any(e.lower().endswith('.' + w) for w in wilds)]
    risk = []
    for tk in ntok:
        if any(_covers(e, tk) for e in uniq) and not any(_covers(e, tk) for e in keep):
            risk.append(tk)
    return keep, len(uniq), len(tokens), len(ntok), risk

# ---------- zero-risk de-dup: rules already covered by a broader rule ----------
def dedupe_filter(buckets):
    """删掉被更宽规则完全覆盖的分流条目（行为不变）。

    HOST-SUFFIX x 同时匹配 x 本身，所以 HOST,x 与 HOST-SUFFIX,x 并存时 HOST 多余；
    HOST-KEYWORD k 命中集合 ⊇ 同名/更长后缀，故 k 是 suffix 的后缀时也多余。
    """
    suf = [v.lower() for v in buckets['HOST-SUFFIX']]
    def covered(h):
        hl = h.lower()
        for s in suf:
            if hl == s or hl.endswith('.' + s):
                return s
        return None
    dropped = {}
    for kind in ('HOST', 'HOST-KEYWORD'):
        keep, gone = [], []
        for v in buckets[kind]:
            s = covered(v)
            if s:
                gone.append((v, s))
            else:
                keep.append(v)
        buckets[kind] = keep
        dropped[kind] = gone
    return dropped

SENS_HOST = ('alipay.com', 'alipay.cn', 'tenpay.com', 'wechatpay', 'helipay',
             'yeepay', 'paypal', 'unionpay', '95516', '99bill', 'cgbchina')

def is_sensitive(h):
    hl = h.strip().lower().lstrip('*').lstrip('.')
    return any(s in hl for s in SENS_HOST)

def filter_covered_hosts(hosts, buckets):
    """删掉已被分流层 REJECT 的 MITM 主机（连接在握手前就被丢弃，MITM 永不触发）。"""
    exact = {v.lower() for v in buckets['HOST']}
    suf = [v.lower() for v in buckets['HOST-SUFFIX']]
    kws = [v.lower() for v in buckets['HOST-KEYWORD']]
    keep, dropped = [], []
    for h in hosts:
        hl = h.lower()
        if '*' in hl:                      # 通配主机可能覆盖未拦截子域，保守保留
            keep.append(h); continue
        hit = hl in exact
        if not hit:
            for s in suf:
                if hl == s or hl.endswith('.' + s):
                    hit = True; break
        if not hit:
            for k in kws:
                if k in hl:
                    hit = True; break
        if hit:
            dropped.append(h)
        else:
            keep.append(h)
    return keep, dropped

# ---------- JS mirror: 把重写引用的第三方脚本收进本仓库 ----------
SCRIPT_RE = re.compile(r'(url\s+(?:script[\w-]*|jsonjq-response-body)\s+)(https?://\S+)')
DEAD_SCRIPTS = {
    # 这些 script 规则永远不会触发，脚本与规则一并移除（详见 NOTICE.md「已停用脚本」）：
    'abchina.js',          # 主机 mobilepaas.abchina.com.cn 按「银行域」剔出 MITM -> 无法解密
    'quark.js',            # 主机 open-cms-api.(uc|quark).cn 带交替，MITM 主机名无法精确覆盖
    '12306.js',            # 主机 ad.12306.cn 已被分流 REJECT，连接在握手前即断
    '555Ad.js',            # 上游模式 [a-zA-Z0-9_-]+(\.[...]){1,4} 为泛主机通配，无具体 hostname 可 MITM
    'amdc.js',             # 同上（泛主机通配）
    'ahfs.js',             # 上游模式 .*(xbwpys|ahhhhfs)\.com 为通配主机
    'fly.js',              # 上游模式 .*flyert.* 为通配主机
    'hanglvzongheng.js',   # 上游模式 .*umetrip\.com\.cn 为通配主机
}

def script_name(s):
    m = SCRIPT_RE.search(s)
    if not m:
        return None
    return m.group(2).rstrip('/').split('/')[-1].split('?')[0]


def _cdn_of(url):
    if url.startswith(GH + '/') and '/refs/heads/' in url:
        return url.replace(GH + '/', CDN + '/', 1).replace('/refs/heads/', '@', 1)
    return None

def mirror_scripts(rw_blocks):
    """把 rw 行里引用外部 JS 的 URL 指向本仓库 scripts/js/<name>，并把文件同步进来。

    下载失败但仓库已有镜像时继续用镜像；两边都没有才保留原始上游地址。
    """
    os.makedirs(JS_DIR, exist_ok=True)
    offline = os.environ.get('QX_NO_DOWNLOAD', '').strip().lower() in ('1', 'true', 'yes')
    stats = dict(new=[], same=[], failed=[], rewritten=0, external=0)
    out = []
    for label, lines in rw_blocks:
        new_lines = []
        for s in lines:
            m = SCRIPT_RE.search(s)
            if not m:
                new_lines.append(s); continue
            url = m.group(2)
            if url.startswith(SELF_RAW):
                new_lines.append(s); continue
            stats['external'] += 1
            name = url.split('/')[-1].split('?')[0]
            if not name.endswith('.js'):
                stats['failed'].append(name)
                new_lines.append(s); continue
            path = os.path.join(JS_DIR, name)
            data = None
            for u in (() if offline else (url, _cdn_of(url))):
                if not u:
                    continue
                try:
                    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (ruleset-builder)'})
                    with urllib.request.urlopen(req, timeout=45) as resp:
                        data = resp.read()
                    # 拒绝错误页/空响应，避免把 HTML 或 404 文本当脚本镜像
                    if not data or len(data) < 8 or data.startswith(b'404:') \
                            or data.lstrip()[:1] == b'<':
                        data = None
                    else:
                        break
                except Exception:
                    data = None
            if data is not None:
                old = None
                if os.path.exists(path):
                    with io.open(path, 'rb') as f:
                        old = f.read()
                if old != data:
                    with io.open(path, 'wb') as f:
                        f.write(data)
                    if name not in stats['new']:
                        stats['new'].append(name)
                elif name not in stats['same']:
                    stats['same'].append(name)
            elif os.path.exists(path):
                if name not in stats['same']:
                    stats['same'].append(name)
            else:
                stats['failed'].append(name)
                new_lines.append(s); continue
            new_lines.append(s[:m.start(2)] + SELF_RAW + '/scripts/js/' + name + s[m.end(2):])
            stats['rewritten'] += 1
        out.append((label, new_lines))
    return out, stats

# ---------- fetch ----------
def fetch(key):
    if LOCAL:
        p = os.path.join(LOCAL, LOCAL_MAP[key])
        with io.open(p, 'r', encoding='utf-8-sig', errors='replace') as f:
            return f.read()
    raw, cdn = SOURCES[key]
    urls = [u for u in (raw, cdn) if u]
    ua = UA_QX if key == 'moyu' else 'Mozilla/5.0 (ruleset-builder)'
    last = None
    for u in urls:
        for _ in range(3):
            try:
                r = urllib.request.Request(u, headers={'User-Agent': ua})
                with urllib.request.urlopen(r, timeout=60) as resp:
                    return resp.read().decode('utf-8', errors='replace')
            except Exception as e:
                last = e; time.sleep(2)
    raise RuntimeError('fetch failed %s: %s' % (key, last))

# ---------- parsers ----------
TYPE_MAP = {'HOST':'HOST','HOST-SUFFIX':'HOST-SUFFIX','HOST-KEYWORD':'HOST-KEYWORD',
            'DOMAIN':'HOST','DOMAIN-SUFFIX':'HOST-SUFFIX','DOMAIN-KEYWORD':'HOST-KEYWORD',
            'IP-CIDR':'IP-CIDR','IP6-CIDR':'IP6-CIDR','IP-CIDR6':'IP6-CIDR','USER-AGENT':'USER-AGENT'}

def parse_filter(text, kinds=('qx','surge','snippet')):
    rules = []
    for line in text.split('\n'):
        s = line.strip()
        if not s or s.startswith('#') or s.startswith(';') or s.startswith('//'):
            continue
        if s.lower().startswith('hostname'):
            continue
        parts = [p.strip() for p in s.split(',')]
        if len(parts) < 2:
            continue
        t = parts[0].upper()
        v = parts[1]
        action = parts[2].lower() if len(parts) >= 3 else 'reject'
        if t not in TYPE_MAP:
            continue
        if action != 'reject':
            continue
        tt = TYPE_MAP[t]
        if v.startswith('*') and tt == 'HOST':
            tt, v = 'HOST-SUFFIX', v.lstrip('*')
        if not v:
            continue
        rules.append((tt, v))
    return rules

def parse_rewrites(text):
    out = []
    for line in text.split('\n'):
        s = line.strip()
        if not s or s.startswith('#') or s.startswith(';') or s.startswith('//'):
            continue
        if s.lower().startswith('hostname'):
            continue
        if ' url ' not in s and not s.endswith(' url reject'):
            continue
        out.append(s)
    return out

def parse_userscript(text):
    rewrites, filters, hosts = [], [], []
    for line in text.split('\n'):
        s = line.strip()
        if not s or s.startswith('#') or s.startswith(';') or s.startswith('//'):
            continue
        if s.lower().startswith('hostname'):
            rhs = s.split('=', 1)[1] if '=' in s else ''
            hosts += [h.strip() for h in rhs.split(',') if h.strip()]
            continue
        if ' url ' in s:
            rewrites.append(s); continue
        parts = [p.strip() for p in s.split(',')]
        if len(parts) >= 3 and parts[0].lower() in ('host', 'host-suffix', 'ip-cidr', 'host-keyword'):
            if parts[2].lower() == 'reject':
                t = {'host': 'HOST', 'host-suffix': 'HOST-SUFFIX', 'host-keyword': 'HOST-KEYWORD', 'ip-cidr': 'IP-CIDR'}[parts[0].lower()]
                v = parts[1]
                if v.startswith('*') and t == 'HOST':
                    t, v = 'HOST-SUFFIX', v.lstrip('*')
                filters.append((t, v))
    return rewrites, filters, hosts

def parse_mitm_list(text):
    hosts = []
    for line in text.split('\n'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        if s.lower().startswith('hostname'):
            rhs = s.split('=', 1)[1] if '=' in s else ''
            hosts += [h.strip() for h in rhs.split(',') if h.strip()]
            continue
        for h in s.split(','):
            h = h.strip()
            if h:
                hosts.append(h)
    return hosts

def parse_hostname_conf(text):
    hosts = []
    for line in text.split('\n'):
        s = line.strip()
        if s.lower().startswith('hostname'):
            rhs = s.split('=', 1)[1] if '=' in s else ''
            hosts += [h.strip() for h in rhs.split(',') if h.strip()]
    return hosts

# ---------- build merge ----------
def build():
    splash = fetch('splash'); httpdns = fetch('httpdns'); splash_rw = fetch('splash_rw'); mitm = fetch('mitm')
    moyu_txt = fetch('moyu'); shenji_list = fetch('shenji_list'); shenji_rw = fetch('shenji_rw')
    fq_snip = fetch('fanqie_snip'); fq_rw = fetch('fanqie_rw')

    moyu_rw, moyu_filters, moyu_hosts = parse_userscript(moyu_txt)

    # ---- filter rules ----
    rule_sources = [
        ('hwind2021 Splash-Killer.list', parse_filter(splash)),
        ('hwind2021 BlockHttpDNS.list', parse_filter(httpdns)),
        ('DivineEngine Advertising.list', parse_filter(shenji_list)),
        ('zqzess FanQieNovel.snippet', parse_filter(fq_snip)),
    ]
    # self-hosted carrier list (optional, from repo)
    carrier_p = os.path.join(ROOT, 'QX-Carrier-Ads.list')
    if os.path.exists(carrier_p):
        with io.open(carrier_p, 'r', encoding='utf-8-sig') as f:
            rule_sources.append(('qx-splash-rules QX-Carrier-Ads.list', parse_filter(f.read())))
    if moyu_filters:
        rule_sources.append(('ddgksf2013 StartUpAds.conf', moyu_filters))

    order = ['HOST', 'HOST-SUFFIX', 'HOST-KEYWORD', 'IP-CIDR', 'IP6-CIDR', 'USER-AGENT']
    buckets = {t: [] for t in order}
    seen = set()
    for name, rules in rule_sources:
        for t, v in rules:
            if t not in buckets:
                continue
            k = (t, v.lower())
            if k in seen:
                continue
            seen.add(k); buckets[t].append(v)

    # ---- 零风险去重：删掉已被更宽 HOST-SUFFIX 覆盖的 HOST / HOST-KEYWORD ----
    dropped_rules = dedupe_filter(buckets)
    counts = {t: len(buckets[t]) for t in order}
    total = sum(counts.values())

    # ---- rewrite rules ----
    rw_sources = [
        ('hwind2021 AdBlock-Splash.conf', parse_rewrites(splash_rw)),
        ('ddgksf2013 StartUpAds.conf (墨鱼去开屏2.0)', moyu_rw),
        ('DivineEngine Advertising.conf (神机)', parse_rewrites(shenji_rw)),
        ('zqzess FanQieNovel.qxrewrite', parse_rewrites(fq_rw)),
    ]
    rw_blocks = []
    seen_pat = set()
    rw_count = 0
    for label, lines in rw_sources:
        kept = []
        for s in lines:
            if ('2026.08.29' in s) or ('/d+' in s) or ('BbsImg' in s):
                continue
            if s.startswith('^https?://'):
                s = '^https?:\\/\\/' + s[len('^https?://'):]
            if '  url ' in s:
                s = s.replace('  url ', ' url ')
            pat = re.split(r'\s+url\s+', s)[0].strip()
            if not pat or pat in seen_pat:
                continue
            seen_pat.add(pat); kept.append(s); rw_count += 1
        if kept:
            rw_blocks.append((label, kept))

    # ---- B1：移除永不触发的 script 规则（主机不在 MITM / 已被分流 REJECT / 上游为通配主机）----
    dead_rw = []
    nb = []
    for label, lines in rw_blocks:
        kept = []
        for s in lines:
            nm = script_name(s)
            if nm in DEAD_SCRIPTS:
                dead_rw.append(nm)
                continue
            kept.append(s)
        if kept:
            nb.append((label, kept))
    rw_blocks = nb
    rw_count = sum(len(x[1]) for x in rw_blocks)

    # ---- 第三方 JS 收进本仓库镜像（防上游删库/改内容），重写 URL 改指向镜像 ----
    rw_blocks, mir = mirror_scripts(rw_blocks)

    # ---- hostnames: union upstream -> prune (only cover non-rejected rewrite) -> safety filter ----
    all_hosts = []
    all_hosts += parse_mitm_list(mitm)
    all_hosts += parse_hostname_conf(shenji_rw)
    all_hosts += moyu_hosts
    all_hosts += parse_hostname_conf(fq_rw)
    pruned, n_entries, n_tokens, n_ntok, risk = prune_hosts(all_hosts, buckets, rw_blocks)
    keep_hosts, host_drop = filter_hosts(pruned)
    # ---- 零风险：域已被分流 REJECT 的主机，MITM 永不触发，删除 ----
    keep_hosts, covered_hosts = filter_covered_hosts(keep_hosts, buckets)
    # ---- 安全：支付/金融域不做 MITM；其对应重写行同时移除（无 MITM 也是死规则）----
    sens_hosts = [h for h in keep_hosts if is_sensitive(h)]
    if sens_hosts:
        keep_hosts = [h for h in keep_hosts if not is_sensitive(h)]
        nb = []
        for label, lines in rw_blocks:
            kept = []
            for s in lines:
                tk = _tok(re.split(r'\s+url\s+', s)[0].strip())
                if tk and is_sensitive(tk[1]):
                    continue
                kept.append(s)
            if kept:
                nb.append((label, kept))
        rw_blocks = nb
        rw_count = sum(len(x[1]) for x in rw_blocks)
    host_drop['rejected_by_filter'] = len(covered_hosts)
    host_drop['sensitive'] = len(sens_hosts)
    MH = len(keep_hosts)
    host_drop['prune_removed'] = n_entries - len(pruned)
    host_drop['risk'] = len(risk)
    if risk:
        raise RuntimeError('MITM prune risk nonzero (%d): %s' % (len(risk), risk[:10]))

    today = datetime.date.today().isoformat()
    return dict(counts=counts, total=total, buckets=buckets, rw_blocks=rw_blocks, rw_count=rw_count,
                keep_hosts=keep_hosts, MH=MH, host_drop=host_drop, today=today,
                mir=mir, dropped_rules=dropped_rules, covered_hosts=covered_hosts, dead_rw=dead_rw)

def write_if_changed(path, text):
    def norm(s):
        return [l for l in s.split('\n') if not re.match(r'(?i)\s*#?\s*.*UPDATED:', l) and 'UPDATED:' not in l]
    old = None
    if os.path.exists(path):
        with io.open(path, 'r', encoding='utf-8-sig') as f:
            old = f.read()
    if old is not None and norm(old) == norm(text):
        return False
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return True

def emit(r):
    c = r['counts']; total = r['total']; today = r['today']
    changed = []

    # ---------- QX-Splash-AdBlock.list ----------
    hdr = [
        '# NAME: QX-Splash-AdBlock',
        '# AUTHOR: qx-splash-rules (aggregated; see NOTICE.md)',
        '# SOURCES:',
        '#   - hwind2021/QuantumultX-AdBlock-CN  Splash-Killer.list (开屏 SDK 域名)',
        '#   - hwind2021/QuantumultX-AdBlock-CN  BlockHttpDNS.list  (阻断 HTTPDNS 绕过)',
        '#   - ddgksf2013/ddgksf2013  StartUpAds.conf  墨鱼去开屏2.0',
        '#   - DivineEngine 神机规则  Advertising.list  (经 HengLiu2282/DivineEngine 镜像)',
        '#   - privacy-protection-tools/anti-AD  → 运营商广告/统计域名（QX-Carrier-Ads.list）',
        '#   - zqzess/rule_for_quantumultX  FanQieNovel.snippet  番茄小说去广告',
        '# UPDATED: %s (auto-sync)' % today,
        '# POLICY: REJECT',
        '# HOST : %d' % c['HOST'],
        '# HOST-SUFFIX : %d' % c['HOST-SUFFIX'],
        '# HOST-KEYWORD : %d' % c['HOST-KEYWORD'],
        '# IP-CIDR : %d' % c['IP-CIDR'],
        '# IP6-CIDR : %d' % c['IP6-CIDR'],
        '# USER-AGENT : %d' % c['USER-AGENT'],
        '# TOTAL: %d' % total,
        '# DESC: 综合去广告规则：开屏广告 SDK + 墨鱼补充 + 阻断 HTTPDNS + 神机通用 + 运营商广告 + 番茄小说。仅需分流规则，无需 MITM。',
        '',
    ]
    body = []
    # need buckets order + values; rebuild from r? store in r
    for t in ['HOST', 'HOST-SUFFIX', 'HOST-KEYWORD', 'IP-CIDR', 'IP6-CIDR', 'USER-AGENT']:
        vals = r['buckets'][t]
        if not vals:
            continue
        body.append('# ---------- %s ----------' % t)
        for v in vals:
            body.append('%s,%s,REJECT' % (t, v))
        body.append('')
    list_txt = '\n'.join(hdr + body).rstrip('\n') + '\n'
    if write_if_changed(os.path.join(ROOT, 'QX-Splash-AdBlock.list'), list_txt): changed.append('QX-Splash-AdBlock.list')

    # ---------- 已停止生成：QX-Splash-AdBlock.conf ----------
    # 与 QX-Splash-Rewrite.conf 内容完全相同（只多 [rewrite_local]/[mitm] 段头），
    # 而作为远程重写资源时 QX 不认段头，故这份整份导入格式不再生成；历史文件一并删除。
    _stale = os.path.join(ROOT, 'QX-Splash-AdBlock.conf')
    if os.path.exists(_stale):
        os.remove(_stale)
        changed.append('QX-Splash-AdBlock.conf (removed)')


    # ---------- QX-MITM-Hosts.conf ----------
    mitm_txt = ('# NAME: QX 综合去开屏 MITM 主机名\n'
                '# DESC: 综合去开屏规则所需的 MITM 主机名清单（hwind + 墨鱼 + 神机 + 番茄 合并后按仅广告相关收敛，共 %d 个）\n' % r['MH'] +
                '# USAGE: 在 Quantumult X「设置 → 重写 → 添加资源」把本文件加为一条重写订阅即可；QX 会自动合并其中的 hostname 行，以后更新主机名无需重新导入整份配置\n' +
                '# UPDATED: %s (auto-sync)\n' % today +
                '# 占位重写（永不命中，仅用于确保本资源被识别为重写资源）\n' +
                '^https?://qx-mitm-hosts\\.invalid/ url reject\n' +
                'hostname = ' + ', '.join(r['keep_hosts']) + '\n')
    if write_if_changed(os.path.join(ROOT, 'QX-MITM-Hosts.conf'), mitm_txt): changed.append('QX-MITM-Hosts.conf')

    # ---------- QX-Splash-Rewrite.conf（远程重写资源格式：无段头，纯重写行 + hostname） ----------
    rw_hdr = [
        '# NAME: QX-Splash-Rewrite',
        '# AUTHOR: qx-splash-rules (aggregated; see NOTICE.md)',
        '# DESC: 开屏广告重写规则（可直接作为 Quantumult X 远程重写资源订阅；末尾 hostname 行会被自动合并）',
        '# UPDATED: %s (auto-sync)' % today,
    ]
    rw_body = []
    for label, lines in r['rw_blocks']:
        rw_body.append('')
        rw_body.append('# ---------- %s ----------' % label)
        rw_body.extend(lines)
    rwconf_txt = ('\n'.join(rw_hdr + rw_body).rstrip('\n') + '\n'
                  'hostname = ' + ', '.join(r['keep_hosts']) + '\n')
    if write_if_changed(os.path.join(ROOT, 'QX-Splash-Rewrite.conf'), rwconf_txt):
        changed.append('QX-Splash-Rewrite.conf')

    # ---------- 清理已停用的死脚本镜像 ----------
    jsd = os.path.join(ROOT, 'scripts', 'js')
    for _nm in sorted(DEAD_SCRIPTS):
        _p = os.path.join(jsd, _nm)
        if os.path.exists(_p):
            os.remove(_p)
            changed.append('scripts/js/%s (removed)' % _nm)

    # ---------- Shadowrocket ----------
    conv = {'HOST': 'DOMAIN', 'HOST-SUFFIX': 'DOMAIN-SUFFIX', 'HOST-KEYWORD': 'DOMAIN-KEYWORD', 'USER-AGENT': 'USER-AGENT'}
    sr_rules = []
    for t in ['HOST', 'HOST-SUFFIX', 'HOST-KEYWORD', 'USER-AGENT', 'IP-CIDR', 'IP6-CIDR']:
        for v in r['buckets'][t]:
            if t in conv:
                sr_rules.append('%s,%s,REJECT' % (conv[t], v))
            else:
                sr_rules.append('%s,%s,REJECT,no-resolve' % (t, v))
    # rewrite: reuse conf rewrite lines
    rw_lines = []
    script = 0
    for label, lines in r['rw_blocks']:
        for s in lines:
            if ' url script' in s:
                script += 1; continue
            rw_lines.append(s)
    hosts_csv = ', '.join(r['keep_hosts'])
    sob = os.path.join(ROOT, 'shadowrocket')
    os.makedirs(sob, exist_ok=True)

    list_txt = ('# QX-Splash-AdBlock · Shadowrocket 版\n'
                '# 由 QX 综合去开屏规则转换\n'
                '# 规则 %d 条（全 REJECT）｜URL 重写 %d 条｜MITM 主机 %d 个\n'
                '# UPDATED: %s · 详见 NOTICE.md / LICENSE\n\n' % (len(sr_rules), len(rw_lines), r['MH'], today) +
                '\n'.join(sr_rules) + '\n')
    if write_if_changed(os.path.join(sob, 'Shadowrocket-AdBlock.list'), list_txt): changed.append('shadowrocket/Shadowrocket-AdBlock.list')

    # ---------- 已停止生成：shadowrocket/Shadowrocket-Rewrite.conf ----------
    # 内容 100% 已包含在 Shadowrocket-AdBlock.conf 里，保留只会造成重复维护。
    _stale2 = os.path.join(sob, 'Shadowrocket-Rewrite.conf')
    if os.path.exists(_stale2):
        os.remove(_stale2)
        changed.append('shadowrocket/Shadowrocket-Rewrite.conf (removed)')


    conf = ('# QX-Splash-AdBlock · Shadowrocket 完整配置\n'
            '# 导入：Shadowrocket → 配置文件 → 添加 → 从文件/URL 导入\n'
            '# 规则 %d 条 + URL 重写 %d 条 + MITM %d 个主机\n' % (len(sr_rules), len(rw_lines), r['MH']) +
            '# 默认 FINAL,DIRECT（纯去广告、不接管代理）。\n'
            '# UPDATED: %s\n\n' % today +
            '[General]\nbypass-system = true\n'
            'skip-proxy = 127.0.0.1, 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 172.20.0.0/14, localhost, *.local\n'
            'dns-server = system, 223.5.5.5, 119.29.29.29, 114.114.114.114\n\n'
            '[Rule]\n' + '\n'.join(sr_rules) + '\nFINAL,DIRECT\n\n'
            '[URL Rewrite]\n' + '\n'.join(rw_lines) + '\n\n[MITM]\nhostname = ' + hosts_csv + '\n')
    if write_if_changed(os.path.join(sob, 'Shadowrocket-AdBlock.conf'), conf): changed.append('shadowrocket/Shadowrocket-AdBlock.conf')

    update_readme(r, changed)
    return dict(changed=changed, total=total, counts=c, rw=r['rw_count'], MH=r['MH'])

def update_readme(r, changed):
    rp = os.path.join(ROOT, 'README.md')
    if not os.path.exists(rp):
        return
    with io.open(rp, 'r', encoding='utf-8-sig') as f:
        t = f.read()
    orig = t
    c = r['counts']
    def sub(pat, repl, flags=0):
        nonlocal t
        t2, n = re.subn(pat, repl, t, count=0, flags=flags)
        if n:
            t = t2
        return n
    sub(r'一次性快照。\d+ 条去重规则：\d+ HOST \+ \d+ HOST-SUFFIX \+ \d+ HOST-KEYWORD \+ \d+ IP-CIDR \+ \d+ IP6-CIDR \+ \d+ USER-AGENT',
        '一次性快照。%d 条去重规则：%d HOST + %d HOST-SUFFIX + %d HOST-KEYWORD + %d IP-CIDR + %d IP6-CIDR + %d USER-AGENT'
        % (r['total'], c['HOST'], c['HOST-SUFFIX'], c['HOST-KEYWORD'], c['IP-CIDR'], c['IP6-CIDR'], c['USER-AGENT']))
    sub(r'\d+ 条重写（原始 \d+ 条，按 URL pattern 去重并修正瑕疵后；来源 (.*?)）\+ \d+ 个 MITM 主机',
        lambda m: '%d 条重写（原始 835 条，按 URL pattern 去重并修正瑕疵后；来源 %s）+ %d 个 MITM 主机' % (r['rw_count'], m.group(1), r['MH']))
    sub(r'只托管 \d+ 个 MITM 主机名', '只托管 %d 个 MITM 主机名' % r['MH'])
    sub(r'MITM 主机清单仍有 \d+ 条', 'MITM 主机清单仍有 %d 条' % r['MH'])
    sub(r'共 \d+ 个）', '共 %d 个）' % r['MH'])
    sub(r'（\d+ 条，Surge/Shadowrocket 格式）', '（%d 条，Surge/Shadowrocket 格式）' % r['total'])
    sub(r'其余 \d+ 条 URL 重写生效', '其余 %d 条 URL 重写生效' % r['rw_count'])
    if t != orig:
        with io.open(rp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(t)
        changed.append('README.md')

if __name__ == '__main__':
    r = build()
    # attach buckets for emit
    dead_list = sorted(set(r.get('dead_rw') or []))
    dead_n = len(r.get('dead_rw') or [])
    out = emit(r)
    print('BUILD total=%d  rw=%d  MH=%d' % (out['total'], out['rw'], out['MH']))
    print('counts:', out['counts'])
    print('dead_scripts_removed_rules:', dead_n, dead_list)
    print('changed:', out['changed'] if out['changed'] else '(none)')
