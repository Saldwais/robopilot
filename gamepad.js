/* Pure Xbox standard-mapping decoder. No motor or network access here. */
(function(root){
  function axis(value, zone=0.18){
    if(!Number.isFinite(value))return 0;
    value=Math.max(-1,Math.min(1,value));
    return Math.abs(value)<=zone?0:Math.sign(value)*(Math.abs(value)-zone)/(1-zone);
  }
  function decode(pad){
    if(!pad||!pad.connected||pad.mapping!=='standard'||pad.axes.length<2||pad.buttons.length<6)return {valid:false};
    if(!Number.isFinite(pad.axes[0])||!Number.isFinite(pad.axes[1]))return {valid:false};
    const pressed=i=>!!pad.buttons[i]?.pressed;
    const throttle=-axis(pad.axes[1])||0,turn=-axis(pad.axes[0])||0;
    return {valid:true,throttle,turn,neutral:throttle===0&&turn===0,hold:pressed(4),arm:pressed(0),stop:pressed(1)};
  }
  const api={axis,decode};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.RoboPilotGamepad=api;
})(typeof window!=='undefined'?window:this);
