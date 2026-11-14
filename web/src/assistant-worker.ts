import {env,pipeline,AutoTokenizer} from '@huggingface/transformers';
let extractor:any;let cachedKey='';let vectors:number[][]=[];
self.onmessage=async(e:MessageEvent)=>{const {id,query,documents,base}=e.data;try{
 if(!extractor){env.allowRemoteModels=false;env.allowLocalModels=true;env.localModelPath=new URL(base+'models/').pathname;env.backends.onnx.wasm!.numThreads=1;env.backends.onnx.wasm!.wasmPaths=base+'ai-runtime/';extractor=await pipeline('feature-extraction','minilm',{dtype:'q8',device:'wasm',progress_callback:(p:any)=>{if(p.status==='progress')self.postMessage({id,progress:Math.round(p.progress||0)});}});if(!extractor.tokenizer)extractor.tokenizer=await AutoTokenizer.from_pretrained('minilm');}
 const key=JSON.stringify(documents);if(key!==cachedKey){const out=await extractor(documents.map((d:any)=>d.text),{pooling:'mean',normalize:true});vectors=out.tolist();cachedKey=key;}
 const out=await extractor(query,{pooling:'mean',normalize:true});const q=out.tolist()[0];const ranked=vectors.map((v,i)=>({id:documents[i].id,score:v.reduce((s,n,j)=>s+n*q[j],0)})).sort((a,b)=>b.score-a.score);self.postMessage({id,ranked});
 }catch(err){console.error('Local evidence model initialization failed',err);self.postMessage({id,diagnostic:String(err),error:'The local AI model could not load. Keyword evidence search is still available.'});}};

