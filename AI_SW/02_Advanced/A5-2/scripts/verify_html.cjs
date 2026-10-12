/** Standalone offline artifacts, source integrity, code navigation and contrast. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const {chromium}=require('/Users/oliverjoo/.npm/_npx/616f69621f722dde/node_modules/playwright');
const root=path.resolve(__dirname,'..');
fs.mkdirSync(path.join(root,'.cache'),{recursive:true});
process.env.TMPDIR=path.join(root,'.cache');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--disable-crash-reporter','--disable-breakpad']});
 const context=await browser.newContext(),page=await context.newPage(),requests=[],errors=[],views=[],contrast=[];
 await context.route(/^https?:/,route=>{requests.push(route.request().url());return route.abort();});
 page.on('pageerror',e=>errors.push(String(e)));
 for(const file of ['README.html','docs/code_walkthrough.html'])for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await page.goto(pathToFileURL(path.join(root,file)).href);
  await page.evaluate(async()=>{await Promise.all([...document.images].map(image=>image.decode()));await document.fonts.ready;});
  const stats=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,images:document.images.length,diagrams:document.querySelectorAll('svg').length,math:document.querySelectorAll('math').length,missing:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash),ids:[...document.querySelectorAll('[id]')].map(e=>e.id),overflow:[...document.querySelectorAll('svg text')].filter(e=>{const b=e.getBBox(),v=e.ownerSVGElement.viewBox.baseVal;return b.x<0||b.x+b.width>v.width||b.y<0||b.y+b.height>v.height;}).map(e=>e.textContent)}));
  if(stats.documentWidth>width||stats.images!==10||stats.diagrams!==(file==='README.html'?1:6)||stats.missing.length||stats.overflow.length||new Set(stats.ids).size!==stats.ids.length)throw Error(JSON.stringify({file,stats}));
  delete stats.ids;views.push({file,...stats});
  const links=await page.locator('a').evaluateAll(list=>list.map(a=>a.getAttribute('href')));
  for(const link of links.filter(x=>!x.startsWith('#'))){const target=path.resolve(path.dirname(path.join(root,file)),link.split('#')[0]);if(!fs.existsSync(target))throw Error('Missing local file '+link);}
  await page.screenshot({path:path.join(root,'.cache',path.basename(file)+'-'+width+'.png')});
 }
 const build=JSON.parse(fs.readFileSync(path.join(root,'reports/document_build.json')));
 const clicks=[];
 for(const link of (await page.locator('a[href^="#code-"]').evaluateAll(a=>a.map(x=>x.getAttribute('href')))).slice(0,6)){
  await page.locator(`a[href="${link}"]`).first().click();
  const clicked=await page.evaluate(()=>{const e=document.getElementById(location.hash.slice(1)),b=e.getBoundingClientRect();return {hash:location.hash,visible:b.top>=0&&b.top<innerHeight,text:e.textContent};});
  if(!clicked.visible)throw Error('Code link failed '+JSON.stringify(clicked));clicks.push(clicked);
 }
 for(const [file,entry] of Object.entries(build.sources)){
  const bytes=fs.readFileSync(path.join(root,file));if(crypto.createHash('sha256').update(bytes).digest('hex')!==entry.sha256)throw Error('Stale source '+file);
  const prefix='code-'+file.replaceAll('/','-').replaceAll('.','-')+'-L';
  const actual=await page.locator(`.source-line[id^="${prefix}"]`).evaluateAll(lines=>lines.map(line=>{const copy=line.cloneNode(true);copy.querySelector('.ln').remove();return copy.textContent;}));
  if(JSON.stringify(actual)!==JSON.stringify(bytes.toString('utf8').trimEnd().split('\n')))throw Error('Source mismatch '+file);
 }
 const luminance=c=>{const rgb=c.match(/[\d.]+/g).slice(0,3).map(x=>Number(x)/255),l=rgb.map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*l[0]+.7152*l[1]+.0722*l[2];};
 for(const scheme of ['light','dark']){
  await page.emulateMedia({colorScheme:scheme});await page.goto(pathToFileURL(path.join(root,'docs/code_walkthrough.html')).href);
  const measured=await page.evaluate(()=>{const e=document.querySelector('.source-line');location.hash=e.id;function sample(x){let parent=x,b;while(parent){b=getComputedStyle(parent).backgroundColor;if(b!=='rgba(0, 0, 0, 0)')break;parent=parent.parentElement;}return {foreground:getComputedStyle(x).color,background:b};}return {code:sample(document.querySelector('pre code')),number:sample(document.querySelector('.ln')),target:sample(e),padding:getComputedStyle(document.querySelector('pre code')).padding};});
  for(const key of ['code','number','target']){const a=luminance(measured[key].foreground),b=luminance(measured[key].background);measured[key].contrast=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);if(measured[key].contrast<4.5)throw Error('Low contrast');}
  if(measured.code.foreground!=='rgb(20, 33, 61)'||measured.code.background!=='rgb(231, 235, 240)'||measured.padding!=='0px')throw Error('Code palette mismatch');contrast.push({scheme,...measured});
 }
 if(requests.length||errors.length)throw Error(JSON.stringify({requests,errors}));
 const report={passed:true,offline:true,views,clicks,sourceFiles:Object.keys(build.sources).length,contrast,requests,errors};
 fs.writeFileSync(path.join(root,'reports/browser_verification.json'),JSON.stringify(report,null,2));
 await browser.close();console.log(JSON.stringify({passed:true,views:views.length,clicks:clicks.length,sourceFiles:Object.keys(build.sources).length}));
})().catch(e=>{console.error(e);process.exit(1);});
