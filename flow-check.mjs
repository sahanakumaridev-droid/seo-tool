import { chromium } from 'playwright-core';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
for (const path of ['/website-designing', '/mobile-apps', '/blog', '/contact']) {
  await page.goto('http://localhost:5180' + path + '?v=' + Date.now(), { waitUntil: 'networkidle' });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'flow' + path.replace(/\//g,'_') + '.png' });
}
await browser.close();
