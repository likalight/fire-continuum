import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {validatePackage,aggregateMonths,selectedValidation,dailyTotals} from '../src/geography.ts';
const root=new URL('../public/data/global/',import.meta.url);
const read=path=>JSON.parse(gunzipSync(fs.readFileSync(new URL(path,root))));
test('all 185 browser calculations reconcile with independently compiled Python results',()=>{
 const catalog=JSON.parse(fs.readFileSync(new URL('catalog.json',root),'utf8'));
 assert.equal(catalog.countries.length,185);
 const dailyChecked=new Set();
 for(const entry of catalog.countries){
  const p=read(entry.package);validatePackage(p);
  const months=aggregateMonths(p,p.bounds),v=selectedValidation(months);
  assert.equal(months.length,276);
  for(const [i,m] of months.entries()){
   const r=p.totals[i];assert.equal(m.aqua,r.aqua,entry.id);assert.equal(m.rawAqua,r.raw_aqua);
   assert.equal(m.rawNoaa,m.year>=2019?r.raw_noaa20:null);
   assert.equal(m.value,p.primary_policy==='aqua_only'||m.year<2022?r.aqua:r.adjusted,entry.id);
  }
  if(v.wape===null)assert.equal(p.validation.wape,null,entry.id);else assert.ok(Math.abs(v.wape-p.validation.wape)<1e-10,entry.id);
  assert.equal(v.agreement,p.validation.category_agreement,entry.id);
  if(!dailyChecked.has(p.validation.status)){
   dailyChecked.add(p.validation.status);
   for(const y of [2020,2023]){
    const rows=read(entry.id+'/days-'+y+'.json.gz');
    for(let m=1;m<=12;m++){
     const start=`${y}-${String(m).padStart(2,'0')}-01`,end=new Date(Date.UTC(y,m,0)).toISOString().slice(0,10);
     const d=dailyTotals(rows,p,p.bounds,start,end),monthly=months.find(r=>r.year===y&&r.month===m);
     assert.equal(d.aqua,monthly.aqua);assert.equal(d.noaa,monthly.noaa);
     assert.ok(Math.abs(d.value-monthly.value)<1e-7,entry.id);
    }
   }
  }
 }
 assert.equal(dailyChecked.size,Object.values(catalog.status_counts).filter(n=>n>0).length);
});
