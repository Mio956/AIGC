# -*- coding: utf-8 -*-
"""把杭电计算机学院官网 9 个研究所信息写入腾讯文档在线表格。
数据来源（2026-11-18 采集）：
  清单  https://computer.hdu.edu.cn/12276/list.htm  （学院概况→机构设置）
  介绍  https://computer.hdu.edu.cn/12277/list.htm  （学院概况→研究所介绍）
"""
import base64
import importlib.util
import json
import sys

SKILL = r"C:\Users\20986\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docs-plugin\5.11.3-wb.43806934.gecace0f7.ha395516167d4\skills\tencent-docs\tencentdocs.py"
FILE_ID = "ZqdPPxcrflfK"
MAIN_SHEET_ID = "BB08J2"

spec = importlib.util.spec_from_file_location("td", SKILL)
td = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td)


def call(tool, args, service="sheet-mcp"):
    res, err = td.call_tool(service, tool, args)
    if err:
        raise RuntimeError(f"{tool}: {err}")
    payload = (res or {}).get("result", {})
    sc = payload.get("structuredContent")
    if sc is None:
        try:
            sc = json.loads(payload["content"][0]["text"])
        except Exception:
            sc = payload
    if isinstance(sc, dict) and sc.get("error"):
        raise RuntimeError(f"{tool}: {sc['error']}")
    print(f"[OK] {tool}: {json.dumps(sc, ensure_ascii=False)[:260]}")
    return sc


def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


HEADER = [
    "研究所编号", "研究所全称", "中文研究方向（官网原文摘抄）",
    "强匹配中文关键词", "强匹配英文关键词", "代表导师",
]

ROWS = [
    [
        "R1", "计算机应用技术研究所",
        "形成了以下科研优势与特色：（1）智能感知与计算方向：聚焦“感—算—智”一体化的软硬件协同系统设计，致力于突破多模态智能感知的核心理论与关键技术。在智能感知系统架构、七维动态光场采集、脑-机接口与脑电分析、边缘智能计算等方面取得系列创新成果。（2）智能物联网方向：突出多场景感知融合能力，聚焦复杂环境（山区、跨介质）与行业场景（工业、电力、医疗），深耕无人系统感知、物联融合定位，拓展技术应用边界。（3）海量数据计算方向的：深耕多源数据真值发现、众包与数据清洗融合两大方向，提出多款创新算法与系统。（4）物理信息系统方向：聚焦 CPS 核心，跨界融合重实用，以 CPS 为核心，深耕传感网、复杂网络控制等方向，攻克设备协同、能耗控制等痛点。",
        "智能感知与计算、软硬件协同系统、多模态智能感知、智能感知系统架构、七维动态光场采集、脑-机接口、脑电分析、边缘智能计算、智能物联网、多场景感知融合、无人系统感知、物联融合定位、低成本室内定位、定位算法、物联网通信协议、海量数据计算、多源数据真值发现、众包、数据清洗、物理信息系统（CPS）、传感网、复杂网络控制、可穿戴设备、制造业大数据分析",
        "intelligent perception, hardware-software co-design, multimodal perception, perception system architecture, light field capture, brain-computer interface (BCI), EEG analysis, edge intelligent computing, AIoT, multi-scene perception fusion, unmanned system perception, IoT-fused localization, indoor localization, localization algorithm, IoT communication protocol, massive data computing, truth discovery, crowdsourcing, data cleaning, cyber-physical systems (CPS), sensor networks, complex network control, wearable devices, manufacturing big data analytics",
        "所长：申兴发；副所长：周文晖、吴以凡、叶晨",
    ],
    [
        "R2", "认知计算与智能交互研究所",
        "面向新一代人工智能与脑科学深度交叉的发展趋势，聚焦认知计算与智能交互的基础理论、关键方法及应用技术研究，重点围绕类脑认知建模、脑机协同智能、智能感知与多模态计算、复杂系统智能决策等核心方向开展系统性研究。研究所以“认知机理驱动的智能交互”为特色研究主线，强调从人类认知过程与脑信息处理机制中汲取启发，突破传统数据驱动人工智能在泛化能力、可解释性和持续学习能力方面的局限。在技术特色方面，研究所长期围绕脑机协同计算、认知驱动的多模态信息处理与智能学习方法开展研究，形成了从脑信号获取、认知特征建模到智能算法与系统实现的完整研究链条。",
        "认知计算、智能交互、类脑认知建模、脑机协同智能、智能感知、多模态计算、复杂系统智能决策、脑科学、认知机理、泛化能力、可解释性、持续学习、人机协同、智能健康、脑机协同计算、脑信号获取、认知特征建模、多模态信息处理、智能学习方法",
        "cognitive computing, intelligent interaction, brain-inspired cognitive modeling, brain-machine collaborative intelligence, multimodal computing, complex system intelligent decision-making, cognitive mechanism, generalization, interpretability, continual learning, human-machine collaboration, intelligent health, brain signal acquisition, cognitive feature modeling, multimodal information processing, machine learning methods",
        "所长：孔万增；副所长：彭勇、朱莉、明煜航",
    ],
    [
        "R3", "智能与软件技术研究所",
        "着力于对标世界巨头公司抱团创立的“OPAF”组织提出的新型工业控制系统方案，围绕其中最为关键的三大科学问题：面向高可靠高实时应用的开放统一架构系统高复杂高延时的优化、基于海量异构工业数据的孪生空间构建、虚实空间的转换和优化理论和方法，开展理论研究。相关理论突破将支撑实现控制系统软硬件解耦，打破工业控制软件与控制器硬件“深度绑定”的平台模式；建立系统级组态平台技术，实现跨设备、跨网络的设备控制协同组态能力，支持分布式异构系统级协同部署；形成开放式的系统软件架构，实现 ICT 技术与 OT 工业控制技术深度融合，“网控算”一体化和云边端协同控制闭环。",
        "新型工业控制系统、开放统一架构、高可靠高实时、海量异构工业数据、孪生空间构建、虚实空间转换、控制系统软硬件解耦、系统级组态平台、设备控制协同组态、分布式异构系统、系统软件架构、ICT 与 OT 融合、网控算一体化、云边端协同控制",
        "industrial control systems, open unified architecture, high reliability, real-time systems, massive heterogeneous industrial data, digital twin space, virtual-physical space transformation, hardware-software decoupling, system-level configuration, distributed heterogeneous systems, system software architecture, ICT-OT convergence, network-computing-control integration, cloud-edge-device collaborative control",
        "所长：邬惠峰；副所长：徐海涛、李平、孙丹枫",
    ],
    [
        "R4", "先进计算与系统研究所",
        "具体聚焦于：（1）大模型计算与优化技术。聚焦大模型训练集群架构优化、低精度量化推理、模型压缩与分布式部署，攻克千亿级参数模型的高效算力调度难题，适配通用大模型与行业垂类大模型的落地需求。（2）复杂系统计算与优化技术。研究复杂系统内在规律的建模、分析与优化方法，涉及全域数据获取与治理、网络社会刻画与态势感知、传播系统建模与认知干预策略以及人机混合环境中集体智能的协同模式。强调数据与模型双驱动、因果推断与跨平台验证的结合，为智慧城市、社会计算等复杂场景，提供系统解决方案。（3）面向特定领域的智能计算与优化技术。致力于在多智能体动态对抗的复杂环境下，研究自主决策、策略演化与协同优化的核心理论与方法。通过强化学习、大模型与博弈算法相结合的技术路径，重点攻克不完美信息博弈、动态策略生成与人机混合决策等关键问题。",
        "先进计算、大模型计算与优化、训练集群架构、低精度量化推理、模型压缩、分布式部署、算力调度、复杂系统建模、全域数据治理、网络社会、态势感知、传播系统建模、认知干预、集体智能、因果推断、社会计算、智慧城市、多智能体、动态对抗、自主决策、策略演化、协同优化、强化学习、博弈算法、不完美信息博弈、人机混合决策",
        "advanced computing, LLM computing and optimization, training cluster architecture, low-precision quantization, model compression, distributed deployment, compute scheduling, complex system modeling, data governance, situation awareness, propagation modeling, causal inference, collective intelligence, social computing, smart city, multi-agent systems, dynamic adversarial environments, autonomous decision-making, strategy evolution, collaborative optimization, reinforcement learning, game-theoretic algorithms, imperfect-information games, human-machine hybrid decision-making",
        "所长：殷昱煜；副所长：蒋从锋、周仁杰、李尤慧子",
    ],
    [
        "R5", "数智可视建模与仿真研究所",
        "聚焦“数智可信建模与仿真”这一计算机科学与技术交叉前沿领域，围绕可视计算、三维几何建模、智能仿真与数字孪生等核心方向开展系统研究。研究特色在于以几何建模与物理仿真为基础，引入数据驱动与人工智能方法，探索多模态信息融合条件下复杂系统的高保真建模、可视化表达与智能推演机制。研究团队在 B样条/NURBS 几何建模、等几何分析、三维网格处理、可视化算法及工程仿真一体化方面具有扎实积累，强调“模型—算法—系统”协同创新，注重理论深度与工程可落地性并重，形成了面向工程设计、智能制造与复杂系统分析的研究优势。",
        "数智可信建模与仿真、可视计算、三维几何建模、智能仿真、数字孪生、几何建模、物理仿真、数据驱动、多模态信息融合、高保真建模、可视化表达、智能推演、B样条、NURBS、等几何分析、三维网格处理、可视化算法、工程仿真一体化、智能制造、工程设计",
        "trustworthy digital-intelligent modeling and simulation, visual computing, 3D geometric modeling, intelligent simulation, digital twin, geometric modeling, physical simulation, data-driven methods, multimodal information fusion, high-fidelity modeling, visualization, intelligent reasoning, B-spline, NURBS, isogeometric analysis, 3D mesh processing, visualization algorithms, integrated engineering simulation, intelligent manufacturing, engineering design",
        "所长：徐岗；副所长：夏莹杰、陈小雕、许金兰",
    ],
    [
        "R6", "媒体智能计算研究所",
        "聚焦“智能媒体”核心领域，形成了特色鲜明、优势突出的四大研究方向：（1）跨模态融合与智能推理：专注于文本、图像、视频等多模态信息的深度融合与语义理解，研究面向大规模场景的知识化视觉问答（VQA）、视频描述生成等关键技术。（2）图像视频理解、生成与安全：涵盖图像/视频的细粒度识别、内容生成（如可控人像生成、虚拟试穿）、以及视觉隐私保护（如人脸匿名化）、物理机制成像（电磁成像、脑信号成像）等研究。研究所在生成模型、对抗学习、联邦学习等前沿技术上深度布局。（3）三维视觉与元宇宙应用：致力于三维图形理解、点云处理、以及基于稀疏视图的三维内容生成技术研究。（4）医学影像智能分析：积极探索人工智能在医疗健康领域的应用，重点研究多模态医学影像（如胸片）的智能报告生成、跨模态对齐与语义理解。",
        "智能媒体、跨模态融合、智能推理、多模态语义理解、视觉问答（VQA）、视频描述生成、图像视频理解、细粒度识别、内容生成、可控人像生成、虚拟试穿、视觉隐私保护、人脸匿名化、物理机制成像、电磁成像、脑信号成像、生成模型、对抗学习、联邦学习、数据安全、三维视觉、三维图形理解、点云处理、稀疏视图三维生成、元宇宙、自动驾驶、数字孪生、医学影像智能分析、多模态医学影像、智能报告生成、跨模态对齐、辅助诊断",
        "intelligent media, cross-modal fusion, intelligent reasoning, multimodal semantic understanding, visual question answering (VQA), video captioning, fine-grained recognition, content generation, controllable portrait synthesis, virtual try-on, visual privacy protection, face anonymization, physics-based imaging, electromagnetic imaging, generative models, adversarial learning, federated learning, data security, 3D vision, 3D shape understanding, point cloud processing, sparse-view 3D generation, metaverse, autonomous driving, digital twin, medical image analysis, multimodal medical imaging, radiology report generation, cross-modal alignment, computer-aided diagnosis",
        "所长：余宙；副所长：丁佳骏、顾晓玲、朱素果",
    ],
    [
        "R7", "具身机器人研究所",
        "团队成员聚焦于人工智能（具身智能）、大数据安全与隐私保护、智慧物联网、智慧医疗等领域的前沿研究与产品研发，并将具身智能拓展至智慧城市感知与低空经济相关领域的研究与研发。与阿里巴巴、华为、海康威视等知名公司保持长期合作关系。",
        "具身智能、具身机器人、人工智能、大数据安全、隐私保护、智慧物联网、智慧医疗、智慧城市感知、低空经济",
        "embodied AI, embodied robotics, artificial intelligence, big data security, privacy preservation, intelligent IoT (AIoT), smart healthcare, smart city perception, low-altitude economy",
        "所长：李攀；副所长：张建辉、管昉立",
    ],
    [
        "R8", "计算机软件研究所",
        "面向国家信息技术发展和数字经济建设的重大需求，聚焦计算机软件关键理论、核心技术及其工程化应用。研究所围绕软件工程与程序分析、行业大数据挖掘与分析、工业生产过程优化、知识图谱增强、大模型应用等方向，逐步形成具有稳定特色的研究布局。一方面，面向软件复杂性、可靠性和智能化等前沿问题，持续开展原创性理论与方法研究；另一方面，结合行业和区域发展需求，推动软件技术在实际场景中的落地应用。",
        "计算机软件、软件工程、程序分析、行业大数据挖掘与分析、工业生产过程优化、知识图谱增强、大模型应用、软件复杂性、软件可靠性、智能化、数字经济、工程化应用、成果转化",
        "computer software, software engineering, program analysis, industrial big data mining, industrial process optimization, knowledge graph enhancement, LLM applications, software complexity, software reliability, intelligentization, digital economy, engineering application, technology transfer",
        "所长：俞东进；副所长：徐小良、胡海洋、陈信",
    ],
    [
        "R9", "数字诊疗研究所",
        "面向人工智能与医学深度融合的发展需求，聚焦数字诊疗关键技术与智慧医疗应用体系，围绕医学影像、数字病理和智能诊疗系统等方向开展系统研究与技术创新。在数字诊疗领域，研究所重点面向医学影像和结构性眼病等典型临床场景，开展疾病数字化表征、智能分析模型和辅助诊疗方法研究，推动人工智能技术与诊疗流程和医疗器械的深度融合。通过软硬件协同设计与系统集成，研究所具备将人工智能算法嵌入医疗设备和数字诊疗系统中的工程实现能力。在支撑能力方面，研究所围绕数字诊疗与智慧医疗应用对计算资源和系统稳定性的需求，开展人工智能模型在异构计算环境中的应用研究，注重算法部署效率、系统可靠性与安全性。",
        "数字诊疗、智慧医疗、医学影像、数字病理、智能诊疗系统、医工交叉、结构性眼病、疾病数字化表征、智能分析模型、辅助诊疗、医疗器械、软硬件协同、系统集成、异构计算、算法部署效率、系统可靠性、安全性、临床辅助诊疗、医疗管理",
        "digital diagnosis and treatment, smart healthcare, medical imaging, digital pathology, intelligent diagnosis and treatment systems, medical-engineering interdiscipline, structural eye diseases, disease digital representation, intelligent analysis models, computer-aided diagnosis, medical devices, hardware-software co-design, system integration, heterogeneous computing, model deployment efficiency, system reliability, security, clinical decision support, healthcare management",
        "所长：安林；副所长：黄孝喜、陈德潮、徐翀",
    ],
]

NOTES = [
    ["项目", "内容"],
    ["分类规则", "一篇论文优先分配 1 个主研究所标签，最多 2 个副标签"],
    ["无法匹配", "无法匹配的论文统一标记：【其他方向】"],
    ["数据来源", "全部来自杭电计算机学院官网科研机构页面"],
    ["官网清单页", "https://computer.hdu.edu.cn/12276/list.htm （学院概况 → 机构设置 → 教学科研机构）"],
    ["官网介绍页", "https://computer.hdu.edu.cn/12277/list.htm （学院概况 → 研究所介绍，9 个所介绍集中在同一页）"],
    ["研究所数量口径", "官网“教学科研机构”共列出 9 个研究所，另有“计算机基础教学部”“实验教学中心”两个教学机构，非研究所，未纳入本表"],
    ["名称核对（重点）", "官网全称为“具身机器人研究所”，官网无“具身智能研究所”这一机构名称；“具身智能”出现在该所介绍原文中，作为研究方向表述。给提示词同学使用时请以官网全称作为标签值"],
    ["关键词口径", "强匹配中文关键词均从 C 列官网原文中的名词提取，英文列为学术常用译法。示例词“行人导航、场景感知、定位、SLAM、激光雷达”未出现在官网具身机器人研究所介绍原文中，如需加入请先核实来源，避免答辩被挑错"],
    ["原文口径", "C 列为官网原文节选，仅规整网页排版产生的多余空格，未改写字词；引用完整段落请以上方“官网介绍页”为准"],
    ["代表导师口径", "官网介绍页未使用“代表导师”表述，本表 F 列填写官网公布的所长与副所长姓名（官网原文）"],
    ["使用建议", "提示词匹配时以“研究所全称”为唯一标签值，按强匹配关键词命中情况确定 1 个主标签与最多 2 个副标签；无命中则记为【其他方向】"],
    ["采集日期", "2026-11-18"],
]


def grid_values(rows, start_row=0):
    vals = []
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            vals.append({"row": start_row + r, "col": c,
                         "value_type": "STRING", "string_value": v})
    return vals


def write_grid(sheet_id, rows):
    args = {"file_id": FILE_ID, "sheet_id": sheet_id,
            "values": grid_values(rows)}
    try:
        return call("set_range_value", args)
    except RuntimeError as e:
        if "501" not in str(e):
            raise
        vals = []
        for cell in args["values"]:
            vals.append({"row": cell["row"], "col": cell["col"],
                         "value_type": "STRING",
                         "value_base64": base64.b64encode(
                             cell["string_value"].encode("utf-8")).decode("ascii")})
        print("[retry] value_base64")
        return call("set_range_value", {"file_id": FILE_ID, "sheet_id": sheet_id,
                                        "values": vals})


def main():
    # 1. 主表
    call("rename_sheet", {"file_id": FILE_ID, "sheet_id": MAIN_SHEET_ID,
                          "name": "研究所关键词表"})
    write_grid(MAIN_SHEET_ID, [HEADER] + ROWS)
    call("set_cell_style", {"file_id": FILE_ID, "sheet_id": MAIN_SHEET_ID,
                            "start_row": 0, "end_row": 0, "start_col": 0, "end_col": 5,
                            "bold": True, "font_color": "FFFFFFFF",
                            "bg_color": "FF1F4E79", "horizontal_align": "center",
                            "vertical_align": "center", "wrap_text": True})
    call("set_cell_style", {"file_id": FILE_ID, "sheet_id": MAIN_SHEET_ID,
                            "start_row": 1, "end_row": 9, "start_col": 0, "end_col": 5,
                            "vertical_align": "top", "wrap_text": True})
    call("set_dimension_size", {"file_id": FILE_ID, "sheet_id": MAIN_SHEET_ID,
                                "dimensions": [
                                    {"dimension_type": "col", "index": 0, "size": 78},
                                    {"dimension_type": "col", "index": 1, "size": 210},
                                    {"dimension_type": "col", "index": 2, "size": 560},
                                    {"dimension_type": "col", "index": 3, "size": 360},
                                    {"dimension_type": "col", "index": 4, "size": 420},
                                    {"dimension_type": "col", "index": 5, "size": 230},
                                    {"dimension_type": "row", "start_index": 0, "end_index": 0, "size": 34},
                                    {"dimension_type": "row", "start_index": 1, "end_index": 9, "size": 130},
                                ]})
    call("set_freeze", {"file_id": FILE_ID, "sheet_id": MAIN_SHEET_ID,
                        "row_count": 1, "col_count": 2})

    # 2. 备注 sheet
    info = call("add_sheet", {"file_id": FILE_ID, "name": "备注与规则",
                              "append_index": True})
    note_id = find_key(info, "sheet_id")
    if not note_id:
        all_sheets = call("get_sheet_info", {"file_id": FILE_ID})
        for s in (all_sheets.get("sheets") or []):
            if s.get("sheet_name") == "备注与规则":
                note_id = s.get("sheet_id")
    if not note_id:
        raise RuntimeError("无法获取备注 sheet_id")
    print("[OK] 备注 sheet_id =", note_id)
    write_grid(note_id, NOTES)
    call("set_cell_style", {"file_id": FILE_ID, "sheet_id": note_id,
                            "start_row": 0, "end_row": 0, "start_col": 0, "end_col": 1,
                            "bold": True, "font_color": "FFFFFFFF",
                            "bg_color": "FF1F4E79", "horizontal_align": "center"})
    call("set_cell_style", {"file_id": FILE_ID, "sheet_id": note_id,
                            "start_row": 1, "end_row": len(NOTES) - 1,
                            "start_col": 0, "end_col": 1,
                            "vertical_align": "top", "wrap_text": True})
    call("set_dimension_size", {"file_id": FILE_ID, "sheet_id": note_id,
                                "dimensions": [
                                    {"dimension_type": "col", "index": 0, "size": 190},
                                    {"dimension_type": "col", "index": 1, "size": 760},
                                    {"dimension_type": "row", "start_index": 1,
                                     "end_index": len(NOTES) - 1, "size": 42},
                                ]})
    # 3. 回读校验
    check = call("get_cell_data", {"file_id": FILE_ID, "sheet_id": MAIN_SHEET_ID,
                                   "start_row": 0, "end_row": 9,
                                   "start_col": 0, "end_col": 1,
                                   "return_csv": True})
    print("[CHECK] A1:B10 =", json.dumps(check, ensure_ascii=False)[:900])
    print("[DONE] https://docs.qq.com/sheet/DWnFkUFB4Y3JmbGZL?_fid=" + FILE_ID)


if __name__ == "__main__":
    main()
