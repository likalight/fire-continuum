// Preserve every existing research deep link while making the simple guide the default.
const research=()=>!!location.hash&&!['#guide','#place','#saved','#event','#try-it','#field-audit'].includes(location.hash);
const initial=research();
if(initial)void import('./main');else void import('./journey');
addEventListener('hashchange',()=>{if(research()!==initial)location.reload();});
