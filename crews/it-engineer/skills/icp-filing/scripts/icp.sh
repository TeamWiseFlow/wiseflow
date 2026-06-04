#!/usr/bin/env bash
# icp-filing — ICP备案助手
set -euo pipefail
CMD="${1:-help}"; shift 2>/dev/null || true; INPUT="$*"

export ICP_CMD="$CMD"
export ICP_INPUT="$INPUT"

python3 << 'PYEOF'
import os
from datetime import datetime
from html import escape as html_escape

cmd = os.environ.get("ICP_CMD", "help")
inp = os.environ.get("ICP_INPUT", "")

PROVINCES = {"北京":"京ICP备","上海":"沪ICP备","广东":"粤ICP备","浙江":"浙ICP备","江苏":"苏ICP备","四川":"川ICP备","湖北":"鄂ICP备","山东":"鲁ICP备","福建":"闽ICP备","湖南":"湘ICP备","河南":"豫ICP备","河北":"冀ICP备","安徽":"皖ICP备","重庆":"渝ICP备","天津":"津ICP备","陕西":"陕ICP备","辽宁":"辽ICP备","吉林":"吉ICP备","黑龙江":"黑ICP备","广西":"桂ICP备","云南":"滇ICP备","贵州":"黔ICP备","甘肃":"甘ICP备","海南":"琼ICP备","宁夏":"宁ICP备","青海":"青ICP备","西藏":"藏ICP备","新疆":"新ICP备","内蒙古":"蒙ICP备","山西":"晋ICP备","江西":"赣ICP备"}

SITE_TYPES = {
    "personal": {"name": "个人网站", "docs": ["身份证正反面","域名证书","网站备案信息真实性核验单","手持身份证照片"], "rules": ["不得涉及企业/商业内容","标题不能含公司/企业等字眼","不能有评论/论坛功能(部分省)"]},
    "company": {"name": "企业网站", "docs": ["营业执照","法人身份证","网站负责人身份证","域名证书","核验单(盖公章)","授权书(非法人备案)"], "rules": ["域名所有者须与备案主体一致","网站内容须与经营范围一致","前置审批(新闻/出版/医疗等)"]},
}

def cmd_checklist():
    stype = inp.strip().lower() if inp else "company"
    if stype not in SITE_TYPES:
        stype = "company"
    st = SITE_TYPES[stype]
    print("=" * 55)
    print("  ICP备案材料清单 — {}".format(st["name"]))
    print("=" * 55)
    print("")
    print("  一、必备材料:")
    for i, d in enumerate(st["docs"], 1):
        print("    [ ] {}. {}".format(i, d))
    print("")
    print("  二、注意事项:")
    for r in st["rules"]:
        print("    - {}".format(r))
    print("")
    print("  三、通用要求:")
    general = ["域名已实名认证(3个工作日以上)","域名在有效期内","备案期间网站不能访问","手机号须为备案省份号码","一个主体最多备案多个网站"]
    for g in general:
        print("    - {}".format(g))

def cmd_flow():
    print("=" * 55)
    print("  ICP备案流程 (2024版)")
    print("=" * 55)
    print("")
    steps = [
        ("1. 注册账号", "在接入商(阿里云/腾讯云等)注册并实名", "1天"),
        ("2. 填写信息", "主体信息+网站信息+负责人信息", "1天"),
        ("3. 上传材料", "身份证/营业执照/核验单等", "1天"),
        ("4. 初审", "接入商审核材料", "1-2个工作日"),
        ("5. 短信验证", "工信部发送验证短信，24h内验证", "1天"),
        ("6. 管局审核", "省通信管理局审核", "5-20个工作日"),
        ("7. 备案成功", "收到备案号，添加到网站底部", "即时"),
    ]
    for step, desc, time in steps:
        print("  {} ({})".format(step, time))
        print("    {}".format(desc))
        print("")
    print("  总耗时: 约10-25个工作日")
    print("  加急: 部分省份支持，联系接入商")

def cmd_query():
    if not inp:
        print("Usage: query <domain>")
        print("Example: query example.com")
        return
    domain = inp.strip()
    print("=" * 50)
    print("  域名备案查询指引")
    print("=" * 50)
    print("")
    print("  域名: {}".format(domain))
    print("")
    print("  查询方式:")
    print("  1. 工信部官网: https://beian.miit.gov.cn/")
    print("     > 公共查询 > ICP备案查询")
    print("     > 输入域名或备案号")
    print("")
    print("  2. 站长工具: https://icp.chinaz.com/")
    print("")
    print("  备案号格式: {}XXXXXXXX号-X".format(PROVINCES.get("北京", "X ICP备")))

def cmd_province():
    if inp:
        prov = inp.strip()
        if prov in PROVINCES:
            print("  {} → {}".format(prov, PROVINCES[prov]))
            return
    print("=" * 45)
    print("  各省ICP备案号前缀")
    print("=" * 45)
    print("")
    for prov, prefix in sorted(PROVINCES.items()):
        print("  {:6s} → {}".format(prov, prefix))

def cmd_footer():
    if not inp:
        print("Usage: footer <备案号>")
        print("Example: footer 京ICP备2024001234号-1")
        return
    icp = html_escape(inp.strip())
    print("<!-- ICP Footer Code -->")
    print('<div style="text-align:center;padding:20px;color:#999;font-size:12px;">')
    print('  <a href="https://beian.miit.gov.cn/" target="_blank"')
    print('     style="color:#999;text-decoration:none;">')
    print("    {}".format(icp))
    print("  </a>")
    print("</div>")

commands = {"checklist": cmd_checklist, "flow": cmd_flow, "query": cmd_query, "province": cmd_province, "footer": cmd_footer}
if cmd == "help":
    print("ICP Filing Assistant")
    print("")
    print("Commands:")
    print("  checklist [personal|company] — Required documents")
    print("  flow                        — Filing process steps")
    print("  query <domain>              — How to check filing status")
    print("  province [name]             — Provincial ICP prefixes")
    print("  footer <icp_number>         — Generate HTML footer code")
elif cmd in commands:
    commands[cmd]()
else:
    print("Unknown: {}".format(cmd))
PYEOF
