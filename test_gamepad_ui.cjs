const test=require('node:test'), assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const logic=require('./gamepad.js');
function makePad(x=0,y=0,pressed=[]){return {id:'Xbox test fixture',index:0,connected:true,mapping:'standard',axes:[x,y],buttons:Array.from({length:17},(_,i)=>({pressed:pressed.includes(i)}))}}
async function setup(){
  const elements=new Map(),calls=[],timers=[];let pad=makePad(),focus=true,state={connected:false,armed:false,error:'',reason:'Test fixture'};
  function element(key){if(!elements.has(key))elements.set(key,{textContent:'',value:key==='#speed'?'10':'',style:{},classList:{add(){},remove(){}},dataset:{},tagName:'DIV'});return elements.get(key)}
  const sandbox={console,Math,Date,Number,String,Promise,Error,AbortController,URL,location:{hash:'#test-key'},RoboPilotGamepad:logic,
    setTimeout:()=>1,clearTimeout(){},setInterval(fn){timers.push(fn);return fn},clearInterval(){},
    document:{hidden:false,hasFocus:()=>focus,querySelector:element,querySelectorAll:()=>[],addEventListener(){}},
    navigator:{getGamepads:()=>pad?[pad]:[]},window:{isSecureContext:true,addEventListener(){}},
    fetch:async(url,opts)=>{if(url==='/api/command'){const d=JSON.parse(opts.body);calls.push(d);if(d.action==='connect')state.connected=true;if(d.action==='arm')state.armed=true;if(d.action==='stop')state.armed=false}return {ok:true,json:async()=>({...state,hardware:false})}}};
  vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(__dirname,'app.js'),'utf8'),sandbox);
  const flush=()=>new Promise(resolve=>setImmediate(resolve));
  await flush();await element('#connect').onclick();await element('#xboxMode').onclick();
  const tick=timers.find(fn=>fn.name==='gamepadTick');
  return {calls,element,setPad:p=>pad=p,setFocus:f=>focus=f,async tick(){tick();await flush()},async arm(){pad=makePad();tick();await flush();pad=makePad(0,0,[0]);tick();await flush();pad=makePad();tick();await flush()}};
}
test('selecting Xbox never arms automatically',async()=>{const h=await setup();await h.tick();assert.equal(h.calls.filter(c=>c.action==='arm').length,0)});
test('A with neutral and LB released arms',async()=>{const h=await setup();await h.arm();assert.equal(h.calls.filter(c=>c.action==='arm').length,1)});
test('A with displaced stick cannot arm',async()=>{const h=await setup();await h.tick();h.setPad(makePad(0,-1,[0]));await h.tick();assert.equal(h.calls.filter(c=>c.action==='arm').length,0)});
test('movement needs LB and release stops',async()=>{const h=await setup();await h.arm();h.setPad(makePad(0,-1,[4]));await h.tick();assert.ok(h.calls.some(c=>c.action==='drive'&&c.throttle===1),JSON.stringify(h.calls)+h.element('#message').textContent);h.setPad(makePad(0,-1));await h.tick();assert.equal(h.calls.at(-1).action,'stop')});
test('B stops instead of sending a drive',async()=>{const h=await setup();await h.arm();h.setPad(makePad(0,-1,[1,4]));await h.tick();assert.equal(h.calls.at(-1).action,'stop')});
test('controller disappearance stops',async()=>{const h=await setup();await h.arm();h.setPad(null);await h.tick();assert.equal(h.calls.at(-1).action,'stop')});
test('focus loss stops',async()=>{const h=await setup();await h.arm();h.setFocus(false);await h.tick();assert.equal(h.calls.at(-1).action,'stop')});

