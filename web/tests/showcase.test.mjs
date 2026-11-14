import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {openingMarkup,benchmarkMarkup} from '../src/showcase.ts';
import {transferMarkup} from '../src/transfer.ts';
import {imageryMarkup} from '../src/imagery.ts';
const read=name=>JSON.parse(fs.readFileSync(new URL('../public/data/'+name,import.meta.url),'utf8').replace(/^\uFEFF/,''));
test('opening has three explicit evidence stages without autoplay',()=>{
 const s=openingMarkup();assert.equal((s.match(/data-story=/g)||[]).length,3);assert.match(s,/The satellite changed/);assert.match(s,/Indonesia explorer/);
});
test('benchmark exposes rare-category failures alongside agreement',()=>{
 const d=read('decision-benchmark.json'),s=benchmarkMarkup(d,'/data/');
 assert.match(s,/82.9%/);assert.match(s,/79.6%/);assert.match(s,/3 \/ 6/);assert.match(s,/simple calibration misses 1/);
 assert.match(s,/195 \/ 240/);assert.match(s,/not a blind final benchmark/);
 const gated=benchmarkMarkup(d,'/data/','noaa20',true);assert.match(gated,/86.7%/);assert.match(gated,/195 region-month/);
});
test('transfer viewer preserves frozen/local distinction and Australia failure',()=>{
 const d=read('transfer-cases.json');const au=d.regions.find(r=>r.country==='Australia');
 const s=transferMarkup(d,'/data/',au.id,'local',2023,9);
 assert.match(s,/72.9%/);assert.match(s,/66.7%/);assert.match(s,/worsens seasonal category agreement/);
 assert.match(s,/transfer-protocol.json/);assert.equal((s.match(/data-transfer-month=/g)||[]).length,12);
 const fitting=transferMarkup(d,'/data/',d.regions[0].id,'transferred',2020,8);assert.match(fitting,/Known Aqua archive outage/);assert.match(fitting,/fitting era/);
});
test('imagery cannot convert QA passage into corroboration',()=>{
 const d=read('imagery-audit.json'),s=imageryMarkup(d,'/data/','candidate-3');
 assert.match(s,/Fire attribution remains inconclusive/);assert.match(s,/Passing QA does not establish/);assert.match(s,/not known fire-free controls/);
 assert.match(s,/2019-09-15/);assert.match(s,/loading="lazy"/);assert.equal((s.match(/<option value=/g)||[]).length,6);
});
