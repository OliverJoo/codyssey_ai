/** Verify both local HTML artifacts in the existing Chrome/Playwright runtime. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { pathToFileURL } = require('url');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/Users/oliverjoo/.npm/_npx/616f69621f722dde/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const cache = path.join(root, '.cache');
fs.mkdirSync(cache, { recursive: true });
process.env.TMPDIR = cache;

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true, args: ['--disable-crash-reporter', '--disable-breakpad'],
  });
  const context = await browser.newContext();
  const requests = [], errors = [], viewports = [], clicks = [];
  await context.route(/^https?:/, route => { requests.push(route.request().url()); return route.abort(); });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(String(error)));
  const build = JSON.parse(fs.readFileSync(path.join(root, 'reports/document_build.json')));
  for (const file of ['README.html', 'docs/code_walkthrough.html']) {
    const expectedDiagrams = file === 'README.html' ? build.readme_diagrams : build.guide_diagrams;
    const expectedMath = file === 'README.html' ? build.readme_mathml : build.guide_mathml;
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto(pathToFileURL(path.join(root, file)).href);
      await page.evaluate(async () => {
        await Promise.all([...document.images].map(image => image.decode()));
        await document.fonts.ready;
      });
      const stats = await page.evaluate(() => ({
        width: innerWidth, documentWidth: document.documentElement.scrollWidth,
        diagrams: document.querySelectorAll('svg').length,
        mathml: document.querySelectorAll('math').length,
        images: document.images.length,
        missingLinks: [...document.querySelectorAll('a[href^="#"]')].filter(a => !document.getElementById(a.hash.slice(1))).map(a => a.hash),
        svgOverflow: [...document.querySelectorAll('svg text')].filter(text => {
          const box = text.getBBox(), frame = text.ownerSVGElement.viewBox.baseVal;
          return box.x < 0 || box.y < 0 || box.x + box.width > frame.width || box.y + box.height > frame.height;
        }).map(text => text.textContent),
      }));
      if (stats.documentWidth > width || stats.diagrams !== expectedDiagrams || stats.mathml !== expectedMath || stats.images !== 5 || stats.missingLinks.length || stats.svgOverflow.length) throw Error(JSON.stringify({ file, stats }));
      await page.screenshot({ path: path.join(cache, `${path.basename(file)}-${width}.png`) });
      const links = await page.locator('a').evaluateAll(items => items.map(a => a.getAttribute('href')));
      for (const link of links.filter(link => !link.startsWith('#'))) {
        const [relative, fragment] = link.split('#');
        const target = path.resolve(path.dirname(path.join(root, file)), relative);
        if (!fs.existsSync(target)) throw Error('Missing local file: ' + link);
        if (fragment && !fs.readFileSync(target, 'utf8').includes(`id="${fragment}"`)) throw Error('Missing code anchor: ' + link);
      }
      viewports.push({ file, ...stats });
    }
  }
  await page.setViewportSize({ width: 1440, height: 1000 });
  const questionClicks = [];
  await page.goto(pathToFileURL(path.join(root,'docs/code_walkthrough.html')).href);
  const questions = await page.locator('#evaluator-questions .qa-item').evaluateAll(items => items.map(item => ({
    id:item.id, question:item.querySelector('h3').textContent.replace(/^질문\s+\d+\.\s+/,''),
    answerFirst:item.children[1].textContent === '답변',
    examples:item.querySelectorAll('ol li').length,
    diagrams:item.querySelectorAll('svg').length,
    codeLinks:item.querySelectorAll('.qa-code-link').length,
  })));
  if (JSON.stringify(questions.map(q=>q.question)) !== JSON.stringify(build.assessment_question_texts) || questions.length!==16 || questions.some(q=>!q.answerFirst||q.examples!==3||q.diagrams!==1||q.codeLinks<1)) throw Error('Question appendix content/order mismatch');
  if (!await page.evaluate(()=>document.querySelector('main').lastElementChild.id === 'evaluator-questions')) throw Error('Question appendix must follow all existing content');
  for (const question of questions) {
    const link=page.locator('#'+question.id+' .qa-code-link').first();
    await link.click();
    const check=await page.evaluate(()=>{
      const target=document.getElementById(location.hash.slice(1));const box=target.getBoundingClientRect();
      return {hash:location.hash,visible:box.top>=0&&box.top<innerHeight};
    });
    if (!check.visible) throw Error('Question source navigation failed: '+question.id);
    questionClicks.push({question:question.id,...check});
  }
  for (const width of [1440,390]) {
    await page.setViewportSize({width,height:1000});
    await page.goto(pathToFileURL(path.join(root,'docs/code_walkthrough.html')).href+'#evaluator-questions');
    await page.screenshot({path:path.join(cache,'questions-'+width+'.png')});
    await page.locator('#qa-01').screenshot({path:path.join(cache,'question-answer-'+width+'.png')});
  }
  await page.setViewportSize({width:1440,height:1000});
  for (const ref of build.code_references.filter(ref=>['supervised','split','regularization','classification','ensemble','custom','tdd'].includes(ref.section))) {
    await page.goto(pathToFileURL(path.join(root,'docs/code_walkthrough.html')).href+'#'+ref.section);
    const codeId='code-'+ref.file.replaceAll('/','-').replaceAll('.','-')+'-L'+ref.line;
    await page.locator(`a[href="#${codeId}"]`).filter({hasText:'실제 코드:'}).first().click();
    const result=await page.evaluate(()=>{
      const node=document.getElementById(location.hash.slice(1));const box=node.getBoundingClientRect();
      return {hash:location.hash,visible:box.top>=0&&box.top<innerHeight,text:node.textContent};
    });
    if(!result.visible)throw Error(JSON.stringify(result));clicks.push(result);
  }
  for (const entry of build.sources) {
    const bytes = fs.readFileSync(path.join(root,entry.file));
    if (crypto.createHash('sha256').update(bytes).digest('hex') !== entry.sha256) throw Error('stale source: '+entry.file);
    const prefix = 'code-'+entry.file.replaceAll('/','-').replaceAll('.','-')+'-L';
    const actual = await page.locator(`.source-line[id^="${prefix}"]`).evaluateAll(lines => lines.map(line => {
      const copy = line.cloneNode(true); copy.querySelector('.ln').remove(); return copy.textContent;
    }));
    if (JSON.stringify(actual) !== JSON.stringify(bytes.toString('utf8').trimEnd().split('\n'))) throw Error('source mismatch: '+entry.file);
  }
  await page.goto(pathToFileURL(path.join(root,'README.html')).href);
  const rendered = await page.locator('pre code').allTextContents();
  const markdown = fs.readFileSync(path.join(root,'README.md'),'utf8');
  const original = [...markdown.matchAll(/```[^\n]*\n([\s\S]*?)```/g)].map(match => match[1].trimEnd());
  if (JSON.stringify(rendered)!==JSON.stringify(original)) throw Error('README commands changed');
  await page.locator('a').filter({hasText:'data_gen.py'}).first().click();
  if (!page.url().includes('code_walkthrough.html#code-data_gen-py-L1')) throw Error('README source navigation failed');
  await page.goto(pathToFileURL(path.join(root,'docs/code_walkthrough.html')).href);
  await page.locator('.diagram').nth(1).screenshot({path:path.join(cache,'training-diagram.png')});
  await page.locator('.formula').nth(1).screenshot({path:path.join(cache,'metric-formula.png')});
  const contrast=[];
  for(const scheme of ['light','dark']) {
    await page.emulateMedia({colorScheme:scheme});
    await page.goto(pathToFileURL(path.join(root,'docs/code_walkthrough.html')).href);
    const measured=await page.evaluate(()=>{
      const code=document.querySelector('pre code'),line=document.querySelector('.source-line'),ln=line.querySelector('.ln');
      function bg(el){while(el){const c=getComputedStyle(el).backgroundColor;if(c!=='transparent'&&c!=='rgba(0, 0, 0, 0)')return c;el=el.parentElement;}return 'rgb(255, 255, 255)';}
      const sample=el=>({foreground:getComputedStyle(el).color,background:bg(el)});
      const normal={code:sample(code),line:sample(line),number:sample(ln)};
      location.hash=line.id;
      return {...normal,target:sample(line),padding:getComputedStyle(code).padding,codeBackground:getComputedStyle(code).backgroundColor};
    });
    function luminance(c){const rgb=c.match(/[\d.]+/g).slice(0,3).map(Number).map(x=>x/255).map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];}
    for(const key of ['code','line','number','target']){
      const a=luminance(measured[key].foreground),b=luminance(measured[key].background);
      measured[key].contrast=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
      if(measured[key].contrast<4.5)throw Error('Low code contrast '+key);
    }
    if(measured.code.foreground!=='rgb(20, 33, 61)'||measured.code.background!=='rgb(231, 235, 240)'||measured.padding!=='0px'||measured.codeBackground!=='rgba(0, 0, 0, 0)'||measured.target.background!=='rgb(244, 237, 223)')throw Error('A2 reference code palette mismatch');
    contrast.push({scheme,...measured});
    await page.locator('.source-section pre').first().screenshot({path:path.join(cache,'code-'+scheme+'.png')});
  }
  fs.writeFileSync(path.join(root,'reports/code_contrast_verification.json'),JSON.stringify({reference:'A2-1 code palette',minimumContrast:4.5,samples:contrast,passed:true},null,2)+'\n');
  if (requests.length || errors.length) throw Error(JSON.stringify({requests,errors}));
  fs.writeFileSync(path.join(root,'reports/browser_verification.json'), JSON.stringify({
    documents:2, viewports, clicks, questions, questionClicks, sources:build.sources.length, readmeCodeBlocksMatch:true, requests,errors,offline:true,
  },null,2)+'\n');
  await browser.close();
  process.stdout.write(JSON.stringify({documents:2,viewports:viewports.length,clicks:clicks.length,questionClicks:questionClicks.length,sources:build.sources.length,offline:true}));
})().catch(error=>{console.error(error);process.exit(1);});
