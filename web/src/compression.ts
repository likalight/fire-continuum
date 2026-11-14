// Servers may deliver .gz as an encoded HTTP response (already decoded by fetch)
// or as an opaque gzip file. Inspect bytes instead of decompressing twice.
export async function decodedResponse(response:Response):Promise<Response>{
 if(!response.ok)throw Error('Data unavailable ('+response.status+')');
 const bytes=new Uint8Array(await response.arrayBuffer());
 const blob=new Blob([bytes]);
 return bytes[0]===0x1f&&bytes[1]===0x8b
  ?new Response(blob.stream().pipeThrough(new DecompressionStream('gzip')))
  :new Response(blob);
}
