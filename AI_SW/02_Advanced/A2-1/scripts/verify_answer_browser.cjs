/** Open the actual local HTML artifacts in Chrome and verify visual and source-link behavior. */
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const playwrightPath = process.env.PLAYWRIGHT_MODULE || '/Users/oliverjoo/.npm/_npx/616f69621f722dde/node_modules/playwright';
const { chromium } = require(playwrightPath);
const root = path.resolve(__dirname, '..');
process.env.TMPDIR = path.join(root, '.cache/tmp');

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--disable-crash-reporter', '--disable-breakpad'],
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const remoteRequests = [], pageErrors = [], report = [], clickedLinks = [];
  await context.route(/^https?:/, route => { remoteRequests.push(route.request().url()); return route.abort(); });
  const page = await context.newPage();
  page.on('pageerror', error => pageErrors.push(String(error)));
  const documents = ['docs/code_walkthrough.html'];
  for (const relative of documents) {
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto(pathToFileURL(path.join(root, relative)).href, { waitUntil: 'load' });
      await page.evaluate(async () => {
        const images = [...document.querySelectorAll('img')];
        images.forEach(image => image.loading = 'eager');
        await Promise.all(images.map(image => image.decode()));
        if (images.some(image => !image.naturalWidth)) throw new Error('PNG decode failed');
        await document.fonts.ready;
      });
      const stats = await page.evaluate(() => ({
        title: document.title,
        sections: document.querySelectorAll('.answer-section').length,
        svg: document.querySelectorAll('svg').length,
        images: document.querySelectorAll('img').length,
        documentWidth: document.documentElement.scrollWidth,
        viewport: innerWidth,
        font: getComputedStyle(document.body).fontFamily,
        actualHangulFont: getComputedStyle(document.querySelector('svg text') || document.body).fontFamily,
        missingToc: [...document.querySelectorAll('aside a')].filter(a => !document.getElementById(decodeURIComponent(a.hash.slice(1)))).map(a => a.hash),
        svgTextOverflow: [...document.querySelectorAll('svg text')].filter(text => {
          const box = text.getBBox(), frame = text.ownerSVGElement.viewBox.baseVal;
          return box.x < -1 || box.y < -1 || box.x + box.width > frame.width + 1 || box.y + box.height > frame.height + 1;
        }).map(text => text.textContent),
        overflowElements: [...document.querySelectorAll('body *')].filter(element => {
          if (element.closest('svg')) return false;
          let ancestor = element.parentElement;
          while (ancestor && ancestor !== document.body) {
            if (getComputedStyle(ancestor).overflowX !== 'visible') return false;
            ancestor = ancestor.parentElement;
          }
          return element.getBoundingClientRect().right > innerWidth + 1;
        }).slice(0, 12).map(element => ({ tag: element.tagName, cls: element.className,
          right: element.getBoundingClientRect().right, text: element.textContent.slice(0, 100) })),
        overflowingBlocks: [...document.querySelectorAll('body *')].filter(element =>
          !element.closest('svg') && element.clientWidth > 0 && element.scrollWidth > element.clientWidth + 1 &&
          getComputedStyle(element).overflowX === 'visible').slice(-12).map(element => ({
            tag: element.tagName, cls: element.className, width: element.clientWidth, scroll: element.scrollWidth,
            text: element.textContent.slice(0, 160),
          })),
      }));
      if (stats.documentWidth > width || stats.missingToc.length || stats.svgTextOverflow.length) throw new Error(JSON.stringify(stats));
      if (stats.sections !== 15 || stats.svg !== 15 || stats.images !== 30) throw new Error('Integrated item coverage failed');
      const label = relative.replace(/[/.]/g, '-');
      await page.screenshot({ path: path.join(root, `.cache/${label}-${width}.png`) });
      if (width === 1440) {
        const diagrams = page.locator('.diagram');
        for (let i = 0; i < await diagrams.count(); i++) {
          await diagrams.nth(i).screenshot({ path: path.join(root, `.cache/answer-diagram-${i + 1}.png`) });
        }
        await page.locator('#criterion-15 .formula').first().screenshot({ path: path.join(root, '.cache/answer-mle-formula.png') });
      }
      report.push({ file: relative, width, ...stats });
    }
  }
  // Exercise actual user clicks from selected sections, including the failed assessment items.
  await page.setViewportSize({ width: 1440, height: 1000 });
  for (const number of [1, 3, 8, 10, 15]) {
    await page.goto(pathToFileURL(path.join(root, 'docs/code_walkthrough.html')).href);
    const link = page.locator(`#criterion-${number} .code-links a[href^="#"]`).first();
    await link.click();
    await page.waitForURL(/code_walkthrough\.html#(?:src-|scripts-)/);
    await page.waitForLoadState('load');
    await page.waitForFunction(() => {
      const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (!target) return false;
      const rect = target.getBoundingClientRect();
      return rect.top >= 0 && rect.top < innerHeight;
    });
    const result = await page.evaluate(() => {
      const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      const rect = target.getBoundingClientRect();
      return { hash: location.hash, highlighted: target.matches(':target'),
        visible: rect.top >= 0 && rect.top < innerHeight, text: target.textContent.slice(0, 160) };
    });
    if (!result.highlighted || !result.visible) throw new Error(JSON.stringify(result));
    clickedLinks.push({ criterion: number, ...result });
  }
  if (pageErrors.length || remoteRequests.length) throw new Error(JSON.stringify({ pageErrors, remoteRequests }));
  fs.writeFileSync(path.join(root, 'reports/browser_verification.json'), JSON.stringify({
    documents: documents.length, viewports: report.length, report, clickedLinks, pageErrors, remoteRequests, offline: true,
    browser: 'Google Chrome via existing local Playwright',
  }, null, 2) + '\n');
  await browser.close();
  process.stdout.write(JSON.stringify({ documents: documents.length, viewports: report.length, clickedLinks: clickedLinks.length, pageErrors, remoteRequests, offline: true }));
})().catch(error => { console.error(error); process.exit(1); });
