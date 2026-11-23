/** Local demo analyzer and model adapter. Never put a secret API key in this browser app. */
export const institutes = [
  '计算机应用技术研究所', '认知计算与智能交互研究所', '智能与软件技术研究所', '先进计算与系统研究所',
  '数智可视建模与仿真研究所', '媒体智能计算研究所', '具身机器人研究所', '计算机软件研究所', '数字诊疗研究所'
];

const rules = [
  { name: '认知计算与智能交互研究所', words: ['用户', '交互', '认知', '对话', '意图', '推荐'] },
  { name: '具身机器人研究所', words: ['具身智能', '机器人', '机械臂', '导航', '动作规划'] },
  { name: '数字诊疗研究所', words: ['诊疗', '医学', '临床', '医疗', '病理'] },
  { name: '媒体智能计算研究所', words: ['图像', '视频', '媒体', '视觉', '多模态'] },
  { name: '先进计算与系统研究所', words: ['系统', '并行', '计算', '芯片', '云计算'] },
  { name: '数智可视建模与仿真研究所', words: ['仿真', '可视化', '建模', '数字孪生'] },
  { name: '智能与软件技术研究所', words: ['软件工程', '智能', '机器学习', '深度学习', '大模型', '算法'] },
  { name: '计算机软件研究所', words: ['程序分析', '编程语言', '软件', '代码', '编译'] },
  { name: '计算机应用技术研究所', words: ['应用', '信息检索', '数据挖掘', '推荐系统', '分类'] }
];
const demoText = `摘要：本文提出了一种基于图神经网络的论文引用关系建模方法，用于提升学术文献推荐的相关性。方法将论文表示为图节点，融合标题语义和引用关系，通过对比学习优化节点表示。在一个包含公开计算机科学论文的引文数据集上进行实验，并与基于内容和基于协同过滤的基线进行对比。实验结果显示，该方法在 Recall@20 和 NDCG@20 上取得提升。本文尚未验证跨学科场景下的泛化能力。关键词：图神经网络；论文推荐；对比学习；学术图谱。`;

const emptyPaper = (overrides = {}) => ({ title: '', authors: [], year: null, problem: '', method: '', data_or_environment: '', findings: [], limitations: [], keywords: [], institute_matches: [], uncertain_fields: [], ...overrides });

export function analyzeDemo(text, filename) {
  const source = String(text || '').slice(0, 250_000);
  const normalized = source.replace(/\s+/g, ' ');
  const abstract = normalized.match(/(?:摘要|abstract)\s*[:：.]?\s*([\s\S]{80,1600}?)(?=关键词|key\s*words|introduction|\b1\s*[.、]|\n|$)/i)?.[1] || normalized.slice(0, 900);
  const keywordText = source.match(/(?:关键词|关键字|key\s*words?)\s*[:：]?\s*([^\n。；;]{2,180})/i)?.[1] || '';
  const keywords = [...new Set([...keywordText.split(/[、,，;；|]/).map(s => s.trim()).filter(s => s.length > 1), ...rules.flatMap(r => r.words).filter(w => source.includes(w))])].slice(0, 8);
  const scored = rules.map(rule => ({ ...rule, hits: rule.words.filter(word => source.includes(word)) })).filter(r => r.hits.length).sort((a, b) => b.hits.length - a.hits.length);
  const matches = scored.slice(0, 3).map((rule, i) => ({ name: rule.name, type: i === 0 ? '主标签' : '副标签', reason: `文本中出现“${rule.hits.slice(0, 3).join('、')}”等方向关键词。`, evidence: rule.hits.join('、') }));
  if (!matches.length) matches.push({ name: '需人工确认', type: '主标签', reason: '演示规则未能从论文文本中找到足够明确的方向依据。', evidence: '' });
  const sentences = (normalized.match(/[^。！？.!?]{16,240}[。！？.!?]?/g) || []).map(s => s.trim());
  const findings = sentences.filter(s => /结果|表明|提升|优于|验证|发现|性能|实验显示|improv|outperform/i.test(s)).slice(0, 3);
  const limitations = sentences.filter(s => /局限|不足|未来工作|未能|尚未|限制|limitation|future work/i.test(s)).slice(0, 3);
  const titleFromText = normalized.match(/^(?:title\s*[:：]\s*)?(.{8,160}?)(?=\s+(?:作者|author|摘要|abstract)\b|[。\n])/i)?.[1];
  const title = titleFromText && !/^(摘要|abstract|关键词)/i.test(titleFromText) ? titleFromText.trim() : (filename || '未识别标题').replace(/\.pdf$/i, '').replace(/[_-]+/g, ' ');
  const hasEnoughText = source.trim().length >= 80;
  return emptyPaper({
    title, problem: hasEnoughText ? (abstract.slice(0, 360) || null) : null,
    method: hasEnoughText ? (sentences.find(s => /方法|提出|模型|框架|method|approach/i.test(s))?.slice(0, 420) || null) : null,
    data_or_environment: hasEnoughText ? (sentences.find(s => /数据集|实验环境|基准|dataset|corpus/i.test(s))?.slice(0, 320) || null) : null,
    findings, limitations, keywords,
    institute_matches: matches,
    uncertain_fields: ['作者', '发表年份', ...(!findings.length ? ['主要发现'] : []), ...(!limitations.length ? ['论文局限'] : []), ...(!hasEnoughText ? ['论文摘要', '研究方法'] : [])]
  });
}

export const demoPaper = emptyPaper({ title: '面向学术文献推荐的图神经网络与对比学习方法', authors: ['演示作者'], year: 2024, problem: '如何同时利用学术文献的语义内容和引文关系，提升学术论文推荐的相关性？', method: '将论文表示为图节点，融合标题语义与引用关系，再用对比学习优化节点表示。', data_or_environment: '公开计算机科学论文引文数据集；与基于内容和基于协同过滤的基线进行比较。', findings: ['实验结果显示，该方法在 Recall@20 和 NDCG@20 上取得提升。'], limitations: ['尚未验证该方法在跨学科场景中的泛化能力。'], keywords: ['图神经网络', '论文推荐', '对比学习', '学术图谱'], institute_matches: [{ name: '智能与软件技术研究所', type: '主标签', reason: '核心方法结合图神经网络与对比学习开展智能推荐。', evidence: '图神经网络、对比学习、论文推荐' }, { name: '计算机应用技术研究所', type: '副标签', reason: '研究问题聚焦学术文献检索与推荐应用。', evidence: '论文推荐' }], uncertain_fields: ['真实作者与发表信息'] });

/** Model API boundary. Use a same-origin backend proxy; keys never belong in client source. */
export async function analyzeWithModel(text, config) {
  if (!config?.endpoint) return analyzeDemo(text, '未命名论文');
  const response = await fetch(config.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', ...(config.headers || {}) }, body: JSON.stringify({ text: String(text).slice(0, 250_000), schema: 'structured-paper-card-v1' }) });
  if (!response.ok) throw new Error(`模型服务暂不可用（${response.status}）。`);
  const data = await response.json();
  if (!data || typeof data !== 'object' || !('title' in data) || !Array.isArray(data.institute_matches)) throw new Error('模型返回格式不符合论文卡片数据结构。');
  return emptyPaper(data);
}

