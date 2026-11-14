import test from 'node:test';
import assert from 'node:assert/strict';
import {parseState,analysisLink} from '../src/analysis-state.ts';
import {seasonPlan} from '../src/planning.ts';
import {groupCounts} from '../src/observations.ts';
const state={bbox:[108,-5,120,4.5],year:2019,month:9,from:2003,to:2025,mode:'adjusted'};
test('shared analysis round trips all selected state',()=>assert.deepEqual(parseState(new URL(analysisLink('https://example.com/',state)).search),state));
test('invalid or off-grid shared bounds cannot enter the analysis',()=>{
 for(const mutation of [{bbox:[108,-5,120,99]},{bbox:[108.1,-5,120,4.5]},{month:13},{year:2026},{from:2020},{mode:'<script>'}])assert.equal(parseState(new URL(analysisLink('https://example.com/',{...state,...mutation})).search),null);
});
test('daily grouping partitions every native pixel without discarding missing data',()=>{
 const input=[1,2,3,4,5,6,7,8,9,10];assert.deepEqual(groupCounts(input),[27,6,4,5,13]);assert.equal(groupCounts(input).reduce((a,b)=>a+b,0),55);
});
test('season planning excludes selected year and future years and supports wrapping',()=>{
 const data=Array.from({length:23*12},(_,i)=>({year:2003+Math.floor(i/12),month:i%12+1,raw:[0],active:[[11,12,1].includes(i%12+1)?100:1],adjusted:[0]}));
 const before=seasonPlan(data,2015);for(const d of data)if(d.year===2015||d.year>2017)d.active[0]=d.month===6?999999:0;
 assert.deepEqual(seasonPlan(data,2015),before);assert.equal(before.start,10);assert.equal(before.stable,14);assert.equal(before.years,14);
});
test('no seasonal signal or an incomplete year cannot produce a peak',()=>{
 const zero=Array.from({length:15*12},(_,i)=>({year:2003+Math.floor(i/12),month:i%12+1,active:[0]}));assert.equal(seasonPlan(zero,2025),null);
 for(const d of zero)d.active[0]=10;zero.pop();assert.equal(seasonPlan(zero,2025),null);
});
