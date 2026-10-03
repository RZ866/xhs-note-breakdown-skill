// Developer-only Chromium checks. No browser dependency is required by the Skill.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require('playwright');
const args=process.argv.slice(2),get=k=>args[args.indexOf(k)+1];
const root=path.resolve(__dirname,'..'),out=path.resolve(get('--output')||path.join(root,'.qa/browser'));
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,...(args.includes('--browser')?{executablePath:get('--browser')}:{})});
 const context=await browser.newContext({offline:true,viewport:{width:1440,height:1000}});
 const page=await context.newPage(),requests=[],errors=[];
 page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
 page.on('pageerror',e=>errors.push(e.message));
 const report=path.join(root,'examples/reports/full/xiaohongshu-analysis-report.html');
 await page.goto(pathToFileURL(report).href);await page.evaluate(()=>document.fonts.ready);
 await page.addStyleTag({content:'html{scroll-behavior:auto!important}'});
 const results={browser:browser.version(),desktop:false,mobile:false,offline:false,chinese:false,print:false,safety:false};
 const check=async()=>await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),title:document.querySelector('h1')?.textContent,text:document.body.innerText}));
 let state=await check();if(state.overflow||!state.images)throw Error('desktop layout or images');results.desktop=true;
 results.chinese=state.text.includes('先解决“是否适合”')&&state.title.includes('小红书');
 await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
 await page.screenshot({path:path.join(out,'preview.png'),fullPage:false});
 await page.locator('.dna').screenshot({path:path.join(out,'dna.png')});
 await page.locator('.cover-grid').screenshot({path:path.join(out,'cover.png')});
 await page.setViewportSize({width:390,height:844});state=await check();if(state.overflow||!state.images)throw Error('mobile layout or images');results.mobile=true;
 await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:false});
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({media:'print'});
 await page.pdf({path:path.join(out,'print.pdf'),format:'A4',printBackground:true});
 await page.screenshot({path:path.join(out,'print.png'),fullPage:true});
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,'print-preview.png'),fullPage:false});
 results.print=fs.statSync(path.join(out,'print.pdf')).size>10000&&await page.evaluate(()=>getComputedStyle(document.body).backgroundColor==='rgb(255, 255, 255)');
 // Exercise the rendered hostile-input report if created by the Python test runner.
 const attack=path.join(root,'.qa/hostile.html');
 if(fs.existsSync(attack)){await page.emulateMedia({media:'screen'});await page.goto(pathToFileURL(attack).href);results.safety=await page.evaluate(()=>!globalThis.pwned&&document.querySelectorAll('script').length===0);}
 results.offline=requests.length===0&&errors.length===0;
 if(Object.values(results).some(v=>v===false))throw Error(JSON.stringify(results));
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results));
 await browser.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
