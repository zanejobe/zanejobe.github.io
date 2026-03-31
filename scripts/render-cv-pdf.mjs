import { chromium } from "playwright";

const [url, outputPath] = process.argv.slice(2);

if (!url || !outputPath) {
  console.error("Usage: node scripts/render-cv-pdf.mjs <url> <output-path>");
  process.exit(1);
}

const browser = await chromium.launch({
  headless: true,
});

try {
  const page = await browser.newPage({
    viewport: { width: 1400, height: 2000 },
  });

  await page.goto(url, { waitUntil: "networkidle" });

  // Generate a clean, printable CV PDF from the rendered Jekyll page.
  await page.addStyleTag({
    content: `
      @page {
        size: letter;
        margin: 0.5in;
      }

      html, body {
        background: #ffffff !important;
        color: #000000 !important;
      }

      .masthead,
      .greedy-nav,
      .sidebar,
      .author__avatar,
      .author__content,
      .author__urls-wrapper,
      .page__footer,
      .pagination,
      .toc,
      .breadcrumbs,
      .home-portrait,
      script {
        display: none !important;
      }

      .initial-content,
      .page,
      .page__inner-wrap,
      .layout--single,
      .archive,
      .page__content {
        background: #ffffff !important;
        color: #000000 !important;
      }

      .page {
        width: 100% !important;
        float: none !important;
        margin: 0 !important;
        padding: 0 !important;
      }

      .page__inner-wrap,
      .page__content {
        max-width: none !important;
        padding: 0 !important;
        margin: 0 !important;
      }

      a,
      a:visited {
        color: #000000 !important;
        text-decoration: none !important;
      }

      table,
      th,
      td {
        color: #000000 !important;
        background: #ffffff !important;
      }

      th,
      td {
        border-color: #999999 !important;
      }
    `,
  });

  await page.pdf({
    path: outputPath,
    format: "Letter",
    printBackground: true,
    margin: {
      top: "0.5in",
      right: "0.5in",
      bottom: "0.5in",
      left: "0.5in",
    },
  });
} finally {
  await browser.close();
}
