import * as pdfjsLib from 'pdfjs-dist';
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

const MAX_BYTES = 50 * 1024 * 1024;
const MAX_PAGES = 300;
const MAX_CHARS = 250_000;

export async function extractPdf(file, onProgress = () => {}) {
  if (file.size > MAX_BYTES) throw new Error('文件超过 50 MB。请先压缩 PDF 或选择较小的文件。');
  if (file.size === 0) throw new Error('文件为空，无法读取。');
  const buffer = await file.arrayBuffer();
  const task = pdfjsLib.getDocument({ data: new Uint8Array(buffer), isEvalSupported: false });
  let pdf;
  try {
    pdf = await task.promise;
    if (pdf.numPages > MAX_PAGES) throw new Error(`该 PDF 共 ${pdf.numPages} 页，当前原型最多处理 ${MAX_PAGES} 页。`);
    const pages = [];
    let charCount = 0;
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      const text = content.items.filter(item => typeof item.str === 'string').map(item => item.str).join(' ').replace(/\s+/g, ' ').trim();
      pages.push({ page: i, text });
      charCount += text.length;
      onProgress({ page: i, total: pdf.numPages, chars: charCount });
      if (charCount >= MAX_CHARS) break;
      if (i % 6 === 0) await new Promise(resolve => setTimeout(resolve, 0));
    }
    const text = pages.filter(p => p.text).map(p => `[第 ${p.page} 页]\n${p.text}`).join('\n\n').slice(0, MAX_CHARS);
    if (text.replace(/\[第 \d+ 页\]/g, '').replace(/\s/g, '').length < 80) throw new Error('该 PDF 可能是扫描件，当前原型暂不支持 OCR，请使用可复制文字的 PDF。');
    await task.destroy();
    return { text, pages: pages.length, characters: charCount, truncated: charCount >= MAX_CHARS };
  } catch (error) {
    await task.destroy().catch(() => {});
    if (error?.name === 'PasswordException') throw new Error('该 PDF 受密码保护，请先解锁后再试。');
    if (error?.name === 'InvalidPDFException') throw new Error('文件似乎不是有效的 PDF，请检查后重试。');
    if (error?.name === 'MissingPDFException') throw new Error('无法读取该 PDF 文件，请重新选择后重试。');
    throw error;
  }
}

