import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {readBrief,taskIntent,savedPlaces} from '../src/brief-core.ts';
const load=id=>JSON.parse(gunzipSync(fs.readFileSync(new URL('../public/data/briefs/'+id+'.json.gz',import.meta.url))));
test('failed adjustment keeps Aqua primary and cannot imply current accuracy',()=>{
 const p=load('mexico'),a=readBrief(p,{kind:'recent',year:2025,month:11});
 assert.equal(a.value,p.recent.at(-1).aqua);assert.match(a.status,/failed/);
 const sample=p.recent.filter(x=>x.year<=2017).map(x=>x.aqua).sort((a,b)=>a-b);
 assert.equal(a.median,sample[7]);assert.equal(a.rows.length,24);assert.match(a.period,/1–13/);
});
test('passing historical calibration never certifies the current snapshot',()=>{
 const a=readBrief(load('australia'),{kind:'recent',year:2025,month:11});
 assert.ok(['Current-period accuracy unvalidated','Sensors give different answers'].includes(a.status));
});
test('outage is not an ordinary low-fire month and pre-VIIRS years are unavailable',()=>{
 const p=load('australia'),a=readBrief(p,{kind:'history',year:2020,month:8});
 assert.equal(a.value,null);assert.equal(a.ratio,null);assert.equal(a.status,'Known observation outage');
 const early=readBrief(p,{kind:'history',year:2010,month:10});assert.equal(early.row.noaa20,null);assert.equal(early.row.adjusted,null);
});
test('zero historical baseline cannot manufacture an anomaly',()=>{
 const p=load('singapore');p.recent.forEach(x=>{if(x.year<=2017)x.aqua=0;});
 const a=readBrief(p,{kind:'recent',year:2025,month:11});assert.equal(a.ratio,null);assert.equal(a.category,'Insufficient baseline');
});
test('selected historical year is excluded from its own baseline and seasonal peak',()=>{
 const p=load('mexico'),before=readBrief(p,{kind:'history',year:2010,month:10});
 p.monthly.filter(x=>x.year===2010).forEach(x=>x.aqua*=10000);
 const after=readBrief(p,{kind:'history',year:2010,month:10});assert.equal(before.median,after.median);assert.deepEqual(before.season,after.season);assert.equal(after.samples,14);
});
test('saved-place input rejects corrupt or unrecognized IDs, duplicates and overflow',()=>{
 const allowed=new Set(['a','b','c','d','e','f','g']);assert.deepEqual(savedPlaces('oops',allowed),[]);
 assert.deepEqual(savedPlaces('["a","a","x",null,"b"]',allowed),['a','b']);assert.equal(savedPlaces(JSON.stringify([...allowed]),allowed).length,6);
});
test('finite assistant actions do not interpret negations or explanation questions as commands',()=>{
 assert.equal(taskIntent('Compare this November with history'),'recent');assert.equal(taskIntent('Make a briefing'),'briefing');assert.equal(taskIntent('Show sensor differences'),'sensors');
 for(const q of ["Don't save this place",'Why compare the latest month?','What does save place mean?','Predict a fire tomorrow','Delete all files'])assert.equal(taskIntent(q),null);
});
test('only actually supplied 2026 months can be analyzed',()=>{
 const p=load('mexico');assert.throws(()=>readBrief(p,{kind:'history',year:2026,month:10}));
 const ext=JSON.parse(fs.readFileSync(new URL('../public/data/new-observations.json',import.meta.url)));p.monthly.push(ext.countries.find(x=>x.id==='mexico').monthly);
 const a=readBrief(p,{kind:'history',year:2026,month:10});assert.equal(a.row.aqua,412);assert.equal(a.value,412);assert.throws(()=>readBrief(p,{kind:'history',year:2026,month:9}));
});
