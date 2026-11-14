import test from 'node:test';
import assert from 'node:assert/strict';
import {filterCountries,catalogCSV,wrapLongitude,statusInfo} from '../src/global-catalog.ts';
const countries=[{id:'france',name:'France',primary_policy:'aqua_only',validation:{status:'insufficient_support',wape:null,category_agreement:null,reference_extreme_months:0}},{id:'brazil',name:'Brazil',primary_policy:'stitched',validation:{status:'agreement_checks_passed',wape:.1,category_agreement:.9,reference_extreme_months:8}}];
test('search and status filters combine without dropping failed results',()=>{assert.equal(filterCountries(countries,' FRA ','insufficient_support')[0].id,'france');assert.equal(filterCountries(countries,'fra','agreement_checks_passed').length,0);assert.equal(filterCountries(countries,'','').length,2);});
test('export preserves unavailable calibration as blank rather than zero',()=>{const csv=catalogCSV(countries);assert.match(csv,/"aqua_only","","","0"/);assert.equal(Object.keys(statusInfo).length,4);});
test('wrapped map clicks normalize without expanding dateline selection',()=>{assert.equal(wrapLongitude(181),-179);assert.equal(wrapLongitude(-181),179);assert.equal(wrapLongitude(0),0);});
