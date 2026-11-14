import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {dayState,qualityMarkup,timeMarkup,decisionMarkup} from '../src/research.ts';
const read=name=>JSON.parse(fs.readFileSync(new URL('../public/data/'+name,import.meta.url),'utf8'));
test('unavailable products never render as a zero-hotspot day',()=>{
 const d=read('quality-calendar.json');const absent=d.days.find(x=>x.date==='2020-08-20');
 assert.equal(dayState(absent),'Archive unavailable');
 const markup=qualityMarkup(d,'/data/');assert.equal((markup.match(/data-quality-date=/g)||[]).length,184);
 assert.match(markup,/167 daily layers/);assert.match(markup,/17 dates without a product/);
});
test('no detected hotspots and cloud are distinguishable',()=>{
 const basic={date:'2020-01-01',status:'available',counts:Array(10).fill(0)};
 assert.match(dayState({...basic,counts:[0,0,0,0,50,50,0,0,0,0]}),/some cloud/);
 assert.equal(dayState({...basic,counts:[0,0,0,0,0,100,0,0,0,0]}),'No hotspot detected in daily composite');
 assert.equal(dayState({...basic,counts:[0,0,0,0,0,99,0,0,1,0]}),'Fire detected');
});
test('time matching withholds unsupported current estimates',()=>{
 const markup=timeMarkup(read('time-comparison.json'),'/data/');
 assert.equal((markup.match(/Withheld: insufficient support/g)||[]).length,2);
 assert.match(markup,/not the published model/);assert.match(markup,/Zero retained Aqua detections does not mean zero Aqua overpasses/);
});
test('decision brief exposes lack of external validation and exploratory candidates',()=>{
 const r=read('robustness.json').case.samples.find(x=>x.year===2019);
 const markup=decisionMarkup(read('decision-case.json'),'/data/',{ratio:r.adjusted_over_median,aquaRatio:r.aqua_over_median});
 assert.match(markup,/not conducted; 0 participants/);assert.match(markup,/17 days later/);
 assert.equal((markup.match(/data-review-cell=/g)||[]).length,3);
 assert.match(markup,/coverage-affected/);assert.match(markup,/not first ignition/);
});
