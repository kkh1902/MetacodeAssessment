module.exports = {
  stylesheet: ['style.css'],
  pdf_options: {
    format: 'A4',
    margin: { top: '20mm', bottom: '22mm', left: '18mm', right: '18mm' },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font-size:9pt;color:#666;text-align:center;font-family:Malgun Gothic, Noto Sans KR, sans-serif;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
  },
};
