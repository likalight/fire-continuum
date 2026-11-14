import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {correctionRows,replay,clockLabel,correctionLines,correctionMarkup} from '../src/corrections.ts';
const read=name=>JSON.parse(readFileSync(new URL('../public/data/'+name,import.meta.url)));
const t=read('correction-trials.json'),d=read('daynight-audit.json');
test('all seven alternatives remain visible with original result',()=>{
 const rows=correctionRows(t,d,'kalimantan');assert.equal(rows.length,7);assert.equal(rows[0].id,'original');
 assert.ok(rows.every(r=>r.disagreement>=rows[0].disagreement));assert.ok(rows.every(r=>r.category==='Above typical'));
});
test('replay uses excluded years and correctly shows a category disagreement',()=>{
 const rows=replay(t,'kalimantan',2025);assert.equal(rows.length,5);assert.equal(rows[0].aqua,52);assert.equal(rows[0].adjusted_category,'At or below typical');assert.equal(rows[0].aqua_category,'Above typical');
 assert.equal(replay(t,'kalimantan',2026).length,0);
});
test('timing labels and interpretation boundaries remain explicit',()=>{
 assert.equal(clockLabel(15.667074),'15:40');assert.equal(clockLabel(null),'Unavailable');
 const markup=correctionMarkup(t,d,'kalimantan','data/');assert.ok(markup.includes('not an orbit-wide timing'));assert.ok(markup.includes('80.3%'));assert.ok(markup.includes('does not automatically replace'));
});
test('custom rectangles do not borrow local validation or coefficients',()=>{
 assert.equal(correctionRows(t,d,'custom').length,0);assert.match(correctionLines(t,d,undefined).join(' '),/has not been evaluated/);assert.match(correctionMarkup(t,d,undefined,'data/'),/unavailable for this custom area/);
});
