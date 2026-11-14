import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {readBrief} from '../src/brief-core.ts';
import {simpleAnswer,calendarCells,briefCSV} from '../src/simple-view.ts';
const load=id=>JSON.parse(gunzipSync(fs.readFileSync(new URL('../public/data/briefs/'+id+'.json.gz',import.meta.url))));
test('plain language preserves direction and distinguishes tiny differences from equality',()=>{
 const a=readBrief(load('australia'),{kind:'recent',year:2025,month:11});
 assert.equal(simpleAnswer({...a,ratio:1}),'At the usual level');
 assert.equal(simpleAnswer({...a,ratio:1.00001}),'Less than 0.1% above usual');
 assert.equal(simpleAnswer({...a,ratio:0.99999}),'Less than 0.1% below usual');
 assert.equal(simpleAnswer({...a,ratio:0}),'100% below usual');
 assert.equal(simpleAnswer({...a,ratio:null}),'There is no usable comparison.');
 assert.equal(simpleAnswer({...a,outage:true}),'We cannot compare this month.');
});
test('all 185 calendars retain missing months, explicit partial dates, outages and source policy',()=>{
 const catalog=JSON.parse(fs.readFileSync(new URL('../public/data/global/catalog.json',import.meta.url)));
 for(const c of catalog.countries){
  const p=load(c.id),rows=calendarCells(p),current=rows[0].cells;
  assert.equal(rows.length,24);assert.equal(current.filter(c=>c.analysis).length,1,c.id);
  assert.equal(current[10].partial,true);assert.match(current[10].analysis.period,/1–13/);
  assert.equal(current[9].analysis,null);
  for(const row of rows)for(const cell of row.cells){
   if(!cell.analysis)continue;
   const a=cell.analysis;
   if(cell.year===2020&&[8,9].includes(cell.month)){assert.equal(cell.tone,'unknown');assert.equal(a.value,null);continue;}
   assert.equal(a.value,cell.year>=2022&&p.primary_policy!=='aqua_only'?a.row.adjusted:a.row.aqua);
  }
 }
});
test('October extension adds only supplied months without inventing current-year coverage',()=>{
 const p=load('mexico'),ext=JSON.parse(fs.readFileSync(new URL('../public/data/new-observations.json',import.meta.url)));
 p.monthly.push(ext.countries.find(c=>c.id===p.id).monthly);
 const current=calendarCells(p)[0].cells;
 assert.equal(current.filter(c=>c.analysis).length,2);
 assert.equal(simpleAnswer(current[9].analysis),'1.2% above usual');
 assert.equal(current[9].analysis.value,412);
});
test('CSV leaves outage values blank and does not call missing observations zero',()=>{
 const csv=briefCSV(load('australia'),{kind:'history',year:2020,month:8});
 const rows=csv.split('\r\n').map(r=>r.slice(1,-1).split('\",\"'));
 const outage=rows.find(r=>r[1]==='2020');
 assert.equal(outage[7],'');assert.equal(outage[10],'');assert.equal(outage[12],'unknown');assert.equal(outage[13],'true');
});
test('CSV export matches the selected answer and records additional October provenance',()=>{
 const p=load('mexico'),ext=JSON.parse(fs.readFileSync(new URL('../public/data/new-observations.json',import.meta.url)));
 p.monthly.push(ext.countries.find(c=>c.id===p.id).monthly);
 const period={kind:'history',year:2026,month:10},a=readBrief(p,period);
 const row=briefCSV(p,period).split('\r\n').at(-1).slice(1,-1).split('\",\"');
 assert.equal(+row[7],a.value);assert.equal(+row[10],a.ratio);assert.match(row[17],/october-transfer.json$/);
});
test('CSV historical rows use the same leave-one-year-out baseline as calendar cells',()=>{
 const p=load('mexico'),period={kind:'history',year:2010,month:10},a=readBrief(p,period);
 const row=briefCSV(p,period).split('\r\n').map(r=>r.slice(1,-1).split('\",\"')).find(r=>r[1]==='2010');
 assert.equal(+row[9],a.median);assert.equal(+row[10],a.ratio);assert.match(row[14],/row year 2010 excluded/);
});
