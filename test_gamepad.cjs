const test=require('node:test');
const assert=require('node:assert/strict');
const {axis,decode}=require('./gamepad.js');
function pad(x=0,y=0,pressed=[]){return {connected:true,mapping:'standard',axes:[x,y],buttons:Array.from({length:17},(_,i)=>({pressed:pressed.includes(i)}))}}
test('neutral stick is zero',()=>assert.deepEqual([decode(pad()).throttle,decode(pad()).turn],[0,0]));
test('stick up is forward',()=>assert.equal(decode(pad(0,-1)).throttle,1));
test('stick down is backward',()=>assert.equal(decode(pad(0,1)).throttle,-1));
test('stick left is positive turn',()=>assert.equal(decode(pad(-1,0)).turn,1));
test('stick right is negative turn',()=>assert.equal(decode(pad(1,0)).turn,-1));
test('dead zone rejects drift',()=>assert.equal(axis(.15),0));
test('axis output is bounded',()=>assert.equal(axis(4),1));
test('invalid numeric axis is rejected',()=>assert.equal(decode(pad(NaN,0)).valid,false));
test('disconnected controller is rejected',()=>assert.equal(decode({...pad(),connected:false}).valid,false));
test('nonstandard mappings rejected',()=>assert.equal(decode({...pad(),mapping:''}).valid,false));
test('LB is the hold button',()=>assert.equal(decode(pad(0,0,[4])).hold,true));
test('A arms and B stops',()=>{const d=decode(pad(0,0,[0,1]));assert.equal(d.arm,true);assert.equal(d.stop,true)});
test('triggers do not allow driving',()=>assert.equal(decode(pad(0,0,[6,7])).hold,false));
