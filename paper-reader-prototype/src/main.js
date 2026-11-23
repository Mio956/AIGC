import { analyzeDemo, analyzeWithModel, demoPaper, institutes } from './paperAnalysis.js';
import { extractPdf } from './pdf.js';
import './style.css';

const $ = selector => document.querySelector(selector);
const state = { papers: [{ id: 'demo', data: demoPaper, text: `摘要：本文提出了一种基于图神经网络的论文引用关系建模方法，用于提升学术文献推荐的相关性。方法将论文表示为图节点，融合标题语义和引用关系，通过对比学习优化节点表示。在一个包含公开计算机科学论文的引文数据集上进行实验，并与基于内容和基于协同过滤的基线进行对比。实验结果显示，该方法在 Recall@20 和 NDCG@20 上取得提升。本文尚未验证跨学科场景下的泛化能力。关键词：图神经网络；论文推荐；对比学习；学术图谱。`, pages: [{ page: 1, text: `第 1 页 · 摘要：本文提出了一种基于图神经网络的论文引用关系建模方法，用于提升学术文献推荐的相关性。方法将论文表示为图节点，融合标题语义和引用关系，通过对比学习优化节点表示。在一个包含公开计算机科学论文的引文数据集上进行实验，并与基于内容和基于协同过滤的基线进行对比。实验结果显示，该方法在 Recall@20 和 NDCG@20 上取得提升。本文尚未验证跨学科场景下的泛化能力。关键词：图神经网络；论文推荐；对比学习；学术图谱。` }], demo: true }], activeId: 'demo', query: '', filter: '', busy: false, modelError: '' };
const active = () => state.papers.find(p => p.id === state.activeId) || null;
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
let toastTimer;
function toast(message) { const node = $('#toast'); node.textContent = message; node.classList.add('visible'); clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove('visible'), 3400); }
function setStatus(message, kind = '') { $('#statusText').textContent = message; $('#uploadStatus').classList.toggle('error', kind === 'error'); $('#uploadStatus').classList.toggle('success', kind === 'success'); }
function availableMatches(paper) { return Array.isArray(paper.institute_matches) ? paper.institute_matches.slice(0, 3) : []; }
function renderFilter() {
  const select = $('#instituteFilter'); const previous = state.filter;
  select.innerHTML = `<option value="">全部研究所</option>${institutes.map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('')}<option value="需人工确认">需人工确认</option><option value="其他方向">其他方向</option>`;
  if ([...select.options].some(o => o.value === previous)) select.value = previous;
}
function renderList() {
  const filtered = state.papers.filter(paper => {
    const text = `${paper.data.title} ${(paper.data.keywords || []).join(' ')}`.toLowerCase();
    return text.includes(state.query.toLowerCase()) && (!state.filter || availableMatches(paper).some(m => m.name === state.filter));
  });
  $('#paperCount').textContent = String(state.papers.length).padStart(2, '0');
  $('#paperList').innerHTML = filtered.length ? filtered.map(paper => {
    const d = paper.data; const tags = availableMatches(d);
    return `<button type="button" class="paper-card ${paper.id === state.activeId ? 'selected' : ''}" data-paper-id="${escapeHtml(paper.id)}" aria-pressed="${paper.id === state.activeId}">
      <span class="paper-card-top"><span class="paper-label">${paper.demo ? '演示样例' : '本地 PDF'}</span><span class="card-chevron" aria-hidden="true">↗</span></span>
      <span class="paper-title">${escapeHtml(d.title || '未识别标题')}</span>
      <span class="tag-list">${(d.keywords || []).slice(0, 4).map(k => `<span class="keyword">${escapeHtml(k)}</span>`).join('')}</span>
      ${tags[0] ? `<span class="card-institute">${escapeHtml(tags[0].name)}</span>` : ''}
      <span class="paper-summary">${escapeHtml(d.problem || '论文中未找到摘要信息。')}</span>
    </button>`;
  }).join('') : `<div class="list-empty"><span class="empty-icon">⌕</span><strong>${state.papers.length ? '没有找到匹配的论文' : '还没有论文'}</strong><span>试试其他关键词或筛选条件。</span></div>`;
  $('#paperList').querySelectorAll('[data-paper-id]').forEach(button => button.addEventListener('click', () => { state.activeId = button.dataset.paperId; state.modelError = ''; render(); }));
}
function field(label, value, fallback = '论文中未找到相关信息。') {
  const content = Array.isArray(value) ? (value.length ? `<ul class="detail-bullets">${value.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : `<p class="muted">${fallback}</p>`) : (value ? `<p>${escapeHtml(value)}</p>` : `<p class="muted">${fallback}</p>`);
  return `<div class="detail-field"><span class="field-label">${label}</span>${content}</div>`;
}
function renderDetails() {
  const paper = active(); const panel = $('#detailPanel');
  if (!paper) { panel.innerHTML = `<div class="detail-empty"><span class="empty-illustration">＋</span><h3>选一篇论文开始阅读</h3><p>上传 PDF，或从左侧选择一张阅读卡片。</p></div>`; return; }
  const d = paper.data; const matches = availableMatches(d); const primary = matches.find(m => m.type === '主标签') || matches[0]; const secondary = matches.filter(m => m !== primary).slice(0, 2);
  const uncertainties = d.uncertain_fields || [];
  panel.innerHTML = `<div class="detail-header"><div class="detail-heading"><span class="section-kicker">03 / PAPER BRIEF · ${paper.demo ? 'DEMO' : 'LOCAL PDF'}</span><h2>${escapeHtml(d.title || '未识别标题')}</h2><div class="byline">${(d.authors || []).length ? d.authors.map(escapeHtml).join('、') : '作者未识别'}${d.year ? ` <span>·</span> ${escapeHtml(d.year)}` : ''}</div></div><div class="match-card"><span class="field-label">主要方向建议</span>${primary ? `<span class="institute-pill">${escapeHtml(primary.name)}</span><p>${escapeHtml(primary.reason || '需结合全文人工核对。')}</p>` : `<span class="institute-pill">需人工确认</span>`}${secondary.map(m => `<span class="secondary-match">＋ ${escapeHtml(m.name)}</span>`).join('')}<small>研究方向匹配仅供初筛参考，请人工核对。</small></div></div>
    <div class="detail-columns">${field('研究问题', d.problem)}${field('核心方法', d.method)}${field('数据 / 实验环境', d.data_or_environment)}${field('主要发现', d.findings)}${field('论文局限', d.limitations)}${field('关键词', d.keywords?.length ? d.keywords.join(' · ') : null)}</div>
    <div class="evidence-strip"><span class="field-label">分类依据</span>${matches.length ? matches.map(m => `<p><b>${escapeHtml(m.name)}</b> · ${escapeHtml(m.evidence || m.reason)}</p>`).join('') : `<p>未找到明确的分类依据。</p>`}<div class="uncertainty"><span class="field-label">需要核对</span><span>${uncertainties.length ? uncertainties.map(escapeHtml).join('、') : '暂无明显缺失字段'}</span></div></div>
    ${paper.truncated ? `<p class="warning-note">已处理前 ${paper.pages.length} 页，文档较长部分已截断；分析结果可能不完整。</p>` : ''}
    ${state.modelError ? `<div class="model-error" role="alert"><strong>分析未能完成</strong><span>${escapeHtml(state.modelError)} 当前展示基于本地规则生成的演示分析。</span></div>` : ''}
    <section class="qa-section" aria-labelledby="qaHeading"><div class="qa-heading"><div><span class="section-kicker">04 / ASK THE PAPER</span><h3 id="qaHeading">问问这篇论文</h3></div><span class="qa-context">仅基于当前论文文本</span></div><div id="chatLog" class="chat-log" aria-live="polite"><div class="chat-message assistant-message"><span class="avatar">AI</span><p>你好，可以问我论文中的研究方法、实验设置或结论。找不到依据时，我会明确告诉你。</p></div></div><form id="questionForm" class="question-form"><label class="sr-only" for="questionInput">输入关于当前论文的问题</label><input id="questionInput" name="question" maxlength="300" placeholder="例如：论文用了什么数据集？" autocomplete="off" required /><button type="submit" aria-label="发送问题">发送 <span aria-hidden="true">↗</span></button></form><p class="qa-disclaimer">回答引用当前论文的原文片段与页码；演示模式下答案由本地文本检索生成。</p></section>`;
  $('#questionForm').addEventListener('submit', askQuestion);
}
function render() { renderFilter(); renderList(); renderDetails(); $('#clearButton').disabled = state.papers.length === 0 || state.busy; $('.demo-badge').hidden = state.papers.every(p => !p.demo); }

function findEvidence(text, pages, question) {
  const q = question.toLowerCase();
  const words = q.match(/[a-z\d]{2,}/g) || [];
  const cjk = [...q].filter(char => /[\u3400-\u9fff]/.test(char)).join('');
  for (let i = 0; i < cjk.length - 1; i++) words.push(cjk.slice(i, i + 2));
  const stop = new Set(['论文', '作者', '请问', '什么', '如何', '哪些', '是否', '这个', '一下', '研究', '方法', '结果', '使用', '通过', '进行', '主要', '用了', '实验', '情况', '介绍', '说明']);
  const terms = [...new Set(words.filter(w => !stop.has(w)))];
  if (/数据集|实验环境|基准|数据来源/.test(q)) terms.push('数据集', '基准', '公开');
  if (/方法|模型|算法|框架/.test(q)) terms.push('方法', '模型', '提出');
  if (/结果|发现|结论|效果|性能/.test(q)) terms.push('结果', '发现', '实验显示');
  if (/局限|不足|缺点|未来工作/.test(q)) terms.push('局限', '不足', '尚未');
  const sentences = [];
  for (const page of pages || []) {
    const chunks = page.text.split(/(?<=[。！？.!?])\s*|\n+/).map(s => s.trim()).filter(s => s.length >= 12);
    for (const sentence of chunks) {
      const hits = terms.filter(term => sentence.toLowerCase().includes(term)).length;
      if (hits) sentences.push({ sentence, page: page.page, hits });
    }
  }
  return sentences.sort((a, b) => b.hits - a.hits)[0] || null;
}
function addChat(role, text) {
  const log = $('#chatLog'); if (!log) return;
  const row = document.createElement('div'); row.className = `chat-message ${role === 'user' ? 'user-message' : 'assistant-message'}`;
  const avatar = document.createElement('span'); avatar.className = 'avatar'; avatar.textContent = role === 'user' ? '我' : 'AI';
  const p = document.createElement('p'); p.textContent = text; row.append(avatar, p); log.append(row); log.scrollTop = log.scrollHeight;
}
function askQuestion(event) {
  event.preventDefault(); const input = $('#questionInput'); const question = input.value.trim(); const paperAtSubmit = active();
  if (!question || !paperAtSubmit) return;
  const id = paperAtSubmit.id; addChat('user', question); input.value = '';
  const evidence = findEvidence(paperAtSubmit.text, paperAtSubmit.pages, question);
  const answer = evidence ? `在第 ${evidence.page} 页附近找到相关表述：“${evidence.sentence.slice(0, 280)}”` : '论文中未找到相关信息。';
  if (active()?.id === id) addChat('assistant', answer);
}

async function handleFile(file) {
  if (!file) return;
  if (!/\.pdf$/i.test(file.name) && file.type !== 'application/pdf') { setStatus('请选择 PDF 格式文件。', 'error'); toast('文件格式不支持，请选择 PDF。'); return; }
  state.busy = true; $('#clearButton').disabled = true; state.modelError = ''; $('#progressWrap').hidden = false; $('#progressBar').style.width = '0%'; setStatus(`准备读取：${file.name}`);
  try {
    const extracted = await extractPdf(file, progress => {
      const pct = Math.round(progress.page / progress.total * 100);
      $('#progressBar').style.width = `${pct}%`; $('#progressPercent').textContent = `${pct}%`;
      $('#progressLabel').textContent = `正在提取文字 · 第 ${progress.page} / ${progress.total} 页`;
      $('#fileMeta').textContent = `${progress.page} / ${progress.total} 页`;
      setStatus(`正在本地提取：${file.name}`);
    });
    $('#progressLabel').textContent = '正在生成阅读卡片…'; $('#progressBar').style.width = '100%';
    setStatus(`本地文本提取完成 · ${extracted.pages} 页 · ${extracted.characters.toLocaleString()} 字`, 'success');
    const data = await analyzeWithModel(extracted.text, null);
    const id = crypto.randomUUID ? crypto.randomUUID() : `paper-${Date.now()}`;
    const pages = extracted.text.split(/(?=\[第 \d+ 页\]\n)/).filter(Boolean).map(block => { const match = block.match(/^\[第 (\d+) 页\]\n/); return { page: match ? Number(match[1]) : 1, text: block.replace(/^\[第 \d+ 页\]\n/, '') }; });
    state.papers.unshift({ id, data, text: extracted.text, pages, demo: false, truncated: extracted.truncated, filename: file.name }); state.activeId = id; state.query = ''; state.filter = ''; $('#searchInput').value = ''; $('#instituteFilter').value = '';
    render(); $('#fileMeta').textContent = `${file.name} · ${extracted.pages} 页 · ${(file.size / 1024 / 1024).toFixed(1)} MB`;
    toast('论文已添加；当前使用演示分析，结果需人工核对。');
  } catch (error) {
    state.modelError = error.message || '未知错误'; setStatus(`解析失败：${state.modelError}`, 'error'); toast(state.modelError); render();
  } finally { state.busy = false; $('#progressWrap').hidden = true; $('#clearButton').disabled = state.papers.length === 0; $('#fileInput').value = ''; }
}

$('#fileInput').addEventListener('change', event => handleFile(event.target.files[0]));
const drop = $('#dropZone');
drop.addEventListener('dragover', event => { event.preventDefault(); drop.classList.add('drag-over'); });
drop.addEventListener('dragleave', () => drop.classList.remove('drag-over'));
drop.addEventListener('drop', event => { event.preventDefault(); drop.classList.remove('drag-over'); handleFile(event.dataTransfer.files[0]); });
drop.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); $('#fileInput').click(); } });
$('#searchInput').addEventListener('input', event => { state.query = event.target.value; renderList(); });
$('#instituteFilter').addEventListener('change', event => { state.filter = event.target.value; renderList(); });
$('#clearButton').addEventListener('click', () => { if (state.busy) return; state.papers = []; state.activeId = null; state.query = ''; state.filter = ''; $('#searchInput').value = ''; $('#fileMeta').textContent = ''; $('#progressWrap').hidden = true; setStatus('就绪 · 上传一篇 PDF 开始阅读'); render(); toast('已清空当前论文。'); });
document.addEventListener('keydown', event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); $('#searchInput').focus(); } });
render();

