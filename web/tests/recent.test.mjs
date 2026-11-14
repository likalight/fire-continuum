import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {recentAssessment,recentLines} from '../src/recent.ts';
const meta=JSON.parse(readFileSync(new URL('../public/data/recent-comparison.json',import.meta.url)));
const rows=JSON.parse(gunzipSync(readFileSync(new URL('../public/data/recent-history.json.gz',import.meta.url))));

test('all study areas reproduce scientific current values and day sensitivity',()=>{
 for(const region of Object.values(meta.regions)){
  const r=recentAssessment(meta,rows,region.bbox);
  assert.equal(r.current.aqua,region.current.aqua);assert.ok(Math.abs(r.current.adjusted-region.current.adjusted)<1e-8);
  assert.equal(r.median,region.current.median);assert.equal(r.adjustedClass,region.current.adjusted_category);
  assert.deepEqual(r.omissions.map(o=>[o.day,o.aquaClass,o.adjustedClass]),region.leave_one_day_out.map(o=>[o.omitted_day,o.aqua_category,o.adjusted_category]));
 }
});
test('no recent activity does not become a confirmed absence of fire',()=>{
 const r=recentAssessment(meta,rows,[94,-12,94.25,-11.75]);assert.equal(r.ratio,null);assert.equal(r.agreement,null);assert.equal(r.diagnostic,undefined);
 assert.match(recentLines(meta,r,'Empty area').join(' '),/complete observations/);
});
test('recent sample never enters the historical baseline',()=>{
 const r=recentAssessment(meta,rows,meta.regions.kalimantan.bbox);
 const modified=rows.map(r=>r[0]===2026?[...r.slice(0,8),r[8]*100]:r);
 const changed=recentAssessment(meta,modified,meta.regions.kalimantan.bbox);
 assert.equal(changed.median,r.median);assert.equal(changed.p90,r.p90);assert.equal(changed.agreement,false);
});
test('brief export carries dates, short-window limits and processing boundary',()=>{
 const r=recentAssessment(meta,rows,meta.regions.kalimantan.bbox),text=recentLines(meta,r,'Kalimantan').join('\n');
 for(const term of ['2026-11-08','2026-11-12','48 windows','NRT','cloud','not distinct fires','SHA-256'])assert.ok(text.includes(term),term);
 assert.equal(r.stable,5);
});
test('a less stable region is not labeled as five stable checks',()=>{
 const r=recentAssessment(meta,rows,meta.regions.java.bbox);assert.equal(r.stable,4);assert.ok(r.diagnostic.same_calendar_dates.wape>2);
});
