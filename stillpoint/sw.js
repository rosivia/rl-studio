// Stillpoint service worker: full offline use after one online visit, plus notifications (mirrored to Garmin).
const CACHE='stillpoint-v4';
const FONTS='https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap';
const SHELL=['./','./index.html','./manifest.webmanifest','./icon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(async c=>{
  await c.addAll(SHELL);
  try{ // studio voice clips: all of them, so guided sessions work with no signal
    const r=await fetch('./audio/en/index.json',{cache:'no-cache'});if(r.ok){const j=await r.clone().json();await c.put('./audio/en/index.json',r);
      const list=[...Object.values(j.files),...(j.samples||[]).map(x=>x.file)].map(f=>'./audio/en/'+f);
      for(let i=0;i<list.length;i+=12)await Promise.all(list.slice(i,i+12).map(u=>fetch(u).then(res=>res.ok&&c.put(u,res)).catch(()=>{})))}
  }catch(err){}
  try{ // fonts are optional: system fonts take over if these are missing
    const css=await fetch(FONTS);await c.put(FONTS,css.clone());
    const text=await css.text();
    const urls=[...text.matchAll(/url\((https:[^)]+)\)/g)].map(m=>m[1]).filter(u=>!/Noto\+?Sans\+?TC|notosanstc/i.test(u)||true);
    // Latin faces are small; cache them all. Chinese slices are cached as they are used.
    const latin=[];let block='';for(const line of text.split('\n')){block+=line+'\n';if(line.trim()==='}'){if(!/Noto Sans TC/.test(block)){const m=block.match(/url\((https:[^)]+)\)/);if(m)latin.push(m[1])}block=''}}
    await Promise.all(latin.map(u=>fetch(u).then(r=>r.ok&&c.put(u,r)).catch(()=>{})));
  }catch(err){}
}));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
// Cache first (works with zero signal), refresh in the background when online.
self.addEventListener('fetch',e=>{const req=e.request;if(req.method!=='GET')return;
  const isNav=req.mode==='navigate';
  e.respondWith(caches.open(CACHE).then(async c=>{
    const hit=await c.match(isNav?'./index.html':req,{ignoreSearch:isNav});
    const net=fetch(req).then(res=>{if(res&&(res.ok||res.type==='opaque'))c.put(isNav?'./index.html':req,res.clone());return res}).catch(()=>null);
    if(hit){e.waitUntil(net);return hit}
    const res=await net;return res||(isNav?c.match('./index.html'):new Response('',{status:504}));
  }))});
self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(self.clients.matchAll({type:'window'}).then(cs=>cs[0]?cs[0].focus():self.clients.openWindow('./')))});
