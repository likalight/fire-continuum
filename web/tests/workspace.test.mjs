import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import zlib from 'node:zlib';
import {recordHighlights} from '../src/workspace.ts';
import {monthsBetween,filterPointCSV,analyticsCSV} from '../src/export-pack.ts';
import {confirmedMarkup} from '../src/story.ts';
import {monthToDateMarkup} from '../src/current.ts';
import {recentAssessment} from '../src/recent.ts';
const read=name=>JSON.parse(fs.readFileSync(new URL('../public/data/'+name,import.meta.url),'utf8').replace(/^\uFEFF/,''));
test('ranked years require twelve months and omit the documented outage year',()=>{
 const rows=[2019,2020,2021].flatMap(y=>Array.from({length:y===2021?11:12},(_,i)=>({year:y,month:i+1,raw:[0,0,0],active:[0,0,0],adjusted:[0,y===2020?999:y===2021?200:100,0]})));
 const r=recordHighlights(rows,2019,2021);assert.equal(r.year.year,2019);assert.equal(r.excluded,2);assert.equal(r.month.year,2020);assert.equal(r.month.month,1);
 assert.equal(recordHighlights([],2003,2004).month,null);
});
test('exact-date export validates dates and traverses calendar boundaries',()=>{
 assert.deepEqual(monthsBetween('2019-12-31','2020-02-29'),['2019-12','2020-01','2020-02']);
 for(const [a,b] of [['2021-02-29','2021-03-01'],['2026-01-01','2026-01-02'],['2020-05-01','2020-04-01']])assert.throws(()=>monthsBetween(a,b));
});
test('original point export respects inclusive UTC dates and half-open effective AOI',()=>{
 const h='latitude,longitude,acq_date,acq_time,satellite,confidence,frp,daynight,type,version';
 const lines=[h,'-3,113,2019-09-15,0530,N,nominal,2,D,0,2','-3,114,2019-09-15,0530,N,nominal,2,D,0,2','-3,113,2019-09-16,0530,N,nominal,2,D,0,2'];
 const r=filterPointCSV(lines.join('\n'),[113,-3,114,-2],'2019-09-15','2019-09-15');assert.equal(r.rows.length,1);assert.match(r.rows[0],/2019-09-15/);assert.throws(()=>filterPointCSV('wrong\n1,2',[],'',''));
});
test('evidence pack analytics preserve platform and baseline rather than summing sensors',()=>{
 const rows=Array.from({length:23},(_,i)=>Array.from({length:12},(_,m)=>({year:2003+i,month:m+1,raw:[10,20,30],active:[5,15,25],adjusted:[5,6,7]}))).flat();
 const csv=analyticsCSV(rows,{bbox:[108,-5,120,4.5],year:2023,month:9,from:2023,to:2023,mode:'raw'});
 assert.equal(csv.split('\n').length,13);assert.match(csv,/2023,9,noaa20,30,25,7.000000,5/);assert.match(csv,/unknown/);
});
test('curated success retains timing limit and does not relabel the fixed audit',()=>{
 const s=confirmedMarkup(read('confirmed-case.json'),'/data/');assert.match(s,/3 h 47 m/);assert.match(s,/No observation meets/);assert.match(s,/all six outcomes remain inconclusive/);assert.match(s,/different spatial scopes/);assert.match(s,/retrospective|Retrospective/);assert.match(s,/Same place and date, different times/);
});
test('month-to-date renders its own dates, availability and unresolved older experiment',()=>{
 const d=read('month-to-date.json'),rows=JSON.parse(zlib.gunzipSync(fs.readFileSync(new URL('../public/data/month-to-date-history.json.gz',import.meta.url))));
 const a=recentAssessment(d,rows,[108,-5,120,4.5]),s=monthToDateMarkup(d,a,'Kalimantan','/data/');
 assert.match(s,/1–13 NOVEMBER/);assert.match(s,/26\/26/);assert.match(s,/not a correction of the earlier five-day 46.8%/);assert.match(s,/without an additional 24-hour/);assert.match(s,/observation completeness still unknown/);
 const java=recentAssessment(d,rows,[105,-9,116,-5]);assert.equal(java.agreement,false);assert.match(monthToDateMarkup(d,java,'Java','/data/'),/satellites disagree/);
});
