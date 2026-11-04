const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(''+require('path').resolve(__dirname,'../index.html').replace(/^/,'file://')+'');await p.waitForTimeout(500);
const t=await p.evaluate(()=>window.__spTexts());require('fs').writeFileSync(process.argv[2],JSON.stringify(t,null,1));
console.log(t.length,'texts', t.reduce((a,x)=>a+x.text.length,0),'chars', errs);await b.close()})();
