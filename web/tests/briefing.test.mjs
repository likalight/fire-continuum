import test from 'node:test';
import assert from 'node:assert/strict';
import {quantile,category,makeBrief} from '../src/briefing.ts';
const fixture=()=>Array.from({length:23*12},(_,i)=>({year:2003+Math.floor(i/12),month:i%12+1,raw:[10,50,60],active:[10,50,60],adjusted:[10,10,10]}));
test('baseline excludes target year and uses Aqua only',()=>{
 const data=fixture();data.find(d=>d.year===2015&&d.month===9).active[0]=10000;
 for(const d of data)d.adjusted[1]=999;
 data.find(d=>d.year===2015&&d.month===9).adjusted[1]=10;
 const b=makeBrief(data,2015,9);assert.equal(b.median,10);assert.equal(b.baselineYears,14);assert.equal(b.agreement,false);
});
test('anomaly threshold is strict and interpolated',()=>{
 assert.equal(quantile([0,10,20],.9),18);assert.equal(category(18,10,18),'Above typical');assert.equal(category(18.01,10,18),'Unusually high');
});
test('zero baseline does not manufacture an anomaly or agreement',()=>{
 const data=fixture();for(const d of data)d.active[0]=0;
 const b=makeBrief(data,2023,9);assert.equal(b.ratio,null);assert.equal(b.agreement,null);assert.equal(b.adjustedClass,'Insufficient baseline');assert.equal(b.hasRhythm,false);
});
test('Aqua-only years are not counted as cross-sensor corroboration',()=>{
 assert.equal(makeBrief(fixture(),2009,9).agreement,null);
});
test('peak window wraps year boundary and selects a consecutive window',()=>{
 const data=fixture();for(const d of data)if([11,12,1].includes(d.month))d.active[0]=100;
 assert.deepEqual(makeBrief(data,2023,9).peakMonths,[10,11,0]);
});
