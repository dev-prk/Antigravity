// Hand-worked expected values. Usage: node physics_test.js <app_dir>
const p = require(require('path').resolve(process.argv[2], 'js/physics.js'));
const near = (a,b)=>Math.abs(a-b)<1e-9;
const t = [
 ['accel 10N/2kg=5', near(p.accel(10,2),5)],
 ['v from rest, a=5, t=3 -> 15', near(p.velocityAfter(0,5,3),15)],
 ['distance u=2,a=4,t=3 -> 6+18=24', near(p.distance(2,4,3),24)],
 ['stick 2kg@3 hits 1kg rest -> 2', near(p.stickCollision(2,3,1,0),2)],
 ['recoil 0.02kg@400, gun 4kg -> -2', near(p.recoilVelocity(0.02,400,4),-2)],
 ['stick opposite 1kg@4 & 3kg@-2 -> -0.5', near(p.stickCollision(1,4,3,-2),-0.5)],
];
let bad=0; for(const [n,ok] of t){console.log(ok?'PASS':'FAIL',n); if(!ok)bad++;}
process.exit(bad?1:0);
