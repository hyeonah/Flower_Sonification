/*function setup() {
    var tone = document.getElementById("comment").nodeValue;
    var osc = new Tone.Oscillator(tone, "sine").toMaster().start();
    return osc.start();
}
*/
var synthA = new Tone.Synth({
    oscillator: {
      type: 'fmsquare',
      modulationType: 'sawtooth',
      modulationIndex: 3,
      harmonicity: 3.4
    },
    envelope: {
      attack: 0.001,
      decay: 0.1,
      sustain: 0.1,
      release: 0.1
    }
  }).toMaster()
  
  var synthB = new Tone.Synth({
    oscillator: {
      type: 'triangle8'
    },
    envelope: {
      attack: 2,
      decay: 1,
      sustain: 0.4,
      release: 4
    }
  }).toMaster()
  
  //mouse events
  document.querySelector('#synthA').addEventListener('mousedown', function() {
    synthA.triggerAttack('C4')
  })
  document.querySelector('#synthA').addEventListener('mouseup', function() {
    synthA.triggerRelease()
  })
  document.querySelector('#synthB').addEventListener('mousedown', function() {
    synthB.triggerAttack('C4')
  })
  document.querySelector('#synthB').addEventListener('mouseup', function() {
    synthB.triggerRelease()
  })
  