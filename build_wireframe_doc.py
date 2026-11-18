# -*- coding: utf-8 -*-
"""任务3：把线框图 PNG 放进可协作的腾讯文档在线文档，拿到在线链接。"""
import base64
import importlib.util
import json
import os

SKILL = r"C:\Users\20986\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docs-plugin\5.11.3-wb.43806934.gecace0f7.ha395516167d4\skills\tencent-docs\tencentdocs.py"
OUT = r"C:\Users\20986\WorkBuddy\2026-11-18-14-23-14"

# 每次都插在正文末尾同一位置，新图会排在旧图之前；因此按期望显示顺序倒序插入，
# 最终文档呈现为 视图1 → 视图2 → 视图3 → 备注。
IMAGES = [
    ("备注_给前端.png", 620, 151),
    ("视图3_详情面板.png", 620, 278),
    ("视图2_论文卡片列表.png", 600, 474),
    ("视图1_首页上传.png", 600, 474),
]

MD = """# 论文阅读助手 - 低保真原型草图

**任务 3 交付｜给前端 C 的页面布局与点击交互依据｜2026-11-18**

本页为低保真线框图，仅用矩形、文字、色块表达「有什么模块、点了会发生什么」，不做美化。3 个视图如下：

1. **视图 1 首页上传视图**：导航栏 → 虚线框【拖拽 PDF 上传区 / 点击上传按钮】→ 摘要文本粘贴框（备选输入方式）→ 底部提示。
2. **视图 2 论文卡片列表视图**：标题「论文列表」→ 多张等尺寸卡片（彩色研究所标签 / 论文标题 / 一句话摘要 / 关键词）→ 点击卡片后右侧滑出详情面板。
3. **视图 3 详情面板视图**：左右分栏；左栏结构化摘要（论文标题、研究目标、核心方法、传感器 / 数据集、实验结论、匹配研究所、关键词），右栏问答对话区（对话气泡 + 输入框 + 发送按钮），右上角关闭按钮收起面板回到卡片列表。

**交互流程**：默认只显示首页 → 上传解析完成渲染卡片列表 → 点击卡片右侧滑出详情面板 → 点关闭回到卡片列表。

**分区对照 summarizepaper**：搜索区＝上传区 / 论文卡片＝卡片列表 / 摘要面板＝详情左栏 / 问答区＝详情右栏。仅借鉴分区结构，不使用其代码与后端。

**原型不做**：分页、收藏、用户登录。

**相关链接**

- PRD 产品需求说明书：https://docs.qq.com/doc/DWm52UkdEYnZvZHFD?_fid=ZnvRGDbvodqC
- 研究所关键词标签库：https://docs.qq.com/sheet/DWnFkUFB4Y3JmbGZL?_fid=ZqdPPxcrflfK
- 参考项目 summarizepaper：https://github.com/summarizepaper/summarizepaper

以下为 3 个视图与备注的线框图。
"""

spec = importlib.util.spec_from_file_location("td", SKILL)
td = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td)


def call(tool, args, service="tencent-docs"):
    res, err = td.call_tool(service, tool, args)
    if err:
        raise RuntimeError(f"{tool}: {err}")
    p = (res or {}).get("result", {})
    sc = p.get("structuredContent")
    if sc is None:
        try:
            sc = json.loads(p["content"][0]["text"])
        except Exception:
            sc = p
    if isinstance(sc, dict) and sc.get("error"):
        raise RuntimeError(f"{tool}: {sc['error']}")
    print(f"[OK] {tool}: {json.dumps(sc, ensure_ascii=False)[:220]}")
    return sc


def find(obj, *keys):
    for k in keys:
        v = None
        if isinstance(obj, dict):
            v = obj.get(k)
        if v in (None, ""):
            def rec(o):
                if isinstance(o, dict):
                    if k in o and o[k] not in (None, ""):
                        return o[k]
                    for x in o.values():
                        r = rec(x)
                        if r is not None:
                            return r
                elif isinstance(o, list):
                    for x in o:
                        r = rec(x)
                        if r is not None:
                            return r
                return None
            v = rec(obj)
        if v not in (None, ""):
            return v
    return None


def main():
    created = call("manage.create_file", {
        "title": "论文阅读助手 - 低保真原型草图", "file_type": "doc"})
    file_id = find(created, "file_id")
    raw_url = find(created, "url", "file_url")
    url = ("https:" + raw_url) if raw_url and raw_url.startswith("//") else raw_url
    if not file_id:
        raise RuntimeError("创建文档失败")
    print("[OK] DOC file_id =", file_id, "url =", url)

    # 正文说明
    call("insert_markdown", {
        "file_id": file_id, "idx": 0,
        "base64_markdown": base64.b64encode(MD.encode("utf-8")).decode("ascii"),
    }, service="doc-mcp")

    # 逐张插图
    for fn, w, h in IMAGES:
        path = os.path.join(OUT, fn)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        up = call("upload_image", {"file_name": fn, "image_base64": b64})
        image_id = find(up, "image_id", "imageID", "imageId", "id")
        if not image_id:
            raise RuntimeError(f"{fn} 上传未返回 image_id")
        pos = call("get_last_operable_pos", {"file_id": file_id},
                   service="doc-mcp")
        idx = find(pos, "pos", "index", "idx", "last_operable_pos")
        if idx is None:
            idx = 0
        call("insert_image", {"file_id": file_id, "idx": int(idx),
                              "image_id": image_id, "width": w, "height": h},
             service="doc-mcp")

    # 共享权限（接口能力有限，尽力设置并回报实际结果）
    try:
        call("manage.set_privilege", {"file_id": file_id, "policy": 3})
    except Exception as e:
        print("[WARN] set_privilege:", e)
    priv = call("manage.get_privilege", {"file_id": file_id})
    print("[OK] 权限 policy =", priv.get("policy"))
    doc_url = (url or "https://docs.qq.com/doc/") + "?_fid=" + file_id
    print("[DONE] doc_url =", doc_url)


if __name__ == "__main__":
    main()
