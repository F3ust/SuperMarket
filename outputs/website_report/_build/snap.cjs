const {chromium}=require('C:/Users/pc/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const OUT=process.argv[2];fs.mkdirSync(OUT,{recursive:true});
(async()=>{const b=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('http://localhost:8765/index.html');await p.waitForFunction(()=>window.RETAIL_APP?.getState().ready,null,{timeout:180000});
const pages=['overview','growth','netsales','catalog','stores','loyalty','customers','basket','forecast','risk','inference','finance','explorer','quality'];
for(const lang of ['vi','en']){await p.click(`.lang-switch button[data-lang="${lang}"]`);await p.waitForTimeout(600);
 for(const r of pages){await p.evaluate(k=>RETAIL_APP.go(k),r);await p.waitForTimeout(1100);await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:`${OUT}/${lang}_${r}.png`,fullPage:true});}}
await b.close()})();
