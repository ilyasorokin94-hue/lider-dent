// Объёмный знак из логотипа справа на первом экране: глянцевый акрил, как знак на стене клиники.
// Части берутся из logo_parts.json: mark (основной цвет), accent (цвет акцента или основной при accent3d: "mark"), ring (цвет акцента). Медленно вращается и чуть следует за курсором.
import { WebGLRenderer, Scene, PMREMGenerator, PerspectiveCamera, DirectionalLight, AmbientLight, MeshPhysicalMaterial, Group, ExtrudeGeometry, Mesh, Box3, Vector3, Clock, MathUtils, ACESFilmicToneMapping, SRGBColorSpace } from 'three';
var THREE = { WebGLRenderer, Scene, PMREMGenerator, PerspectiveCamera, DirectionalLight, AmbientLight, MeshPhysicalMaterial, Group, ExtrudeGeometry, Mesh, Box3, Vector3, Clock, MathUtils, ACESFilmicToneMapping, SRGBColorSpace };
import { SVGLoader } from 'three/examples/jsm/loaders/SVGLoader.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

(function () {
  var box = document.querySelector('.hx--a'), data = document.getElementById('logo-a');
  if (!box || !data) return;
  try {
    var c = document.createElement('canvas'), gl = c.getContext('webgl2') || c.getContext('webgl');
    if (!gl) return box.classList.add('is-flat');
    // без видеокарты (программный WebGL) вращение грузит процессор: оставляем плоский знак
    // новые Chrome отдают настоящее имя в RENDERER, а расширение может отсутствовать: проверяем оба
    var dbg = gl.getExtension('WEBGL_debug_renderer_info');
    var gpu = String(gl.getParameter(gl.RENDERER) || '') + ' ' + (dbg ? String(gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) || '') : '');
    if (/swiftshader|llvmpipe|software|basic render|subzero/i.test(gpu)) return box.classList.add('is-flat');
  } catch (e) { return box.classList.add('is-flat'); }
  var parts = JSON.parse(data.textContent);
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  box.appendChild(renderer.domElement);

  var scene = new THREE.Scene();
  var pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  var camera = new THREE.PerspectiveCamera(30, 1, 1, 5000);
  camera.position.set(0, 0, 1500);

  var key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(500, 700, 900); scene.add(key);
  var rim = new THREE.DirectionalLight(0x9db7e0, 2.6); rim.position.set(-800, 200, -600); scene.add(rim);
  scene.add(new THREE.AmbientLight(0xffffff, 0.25));

  // Акрил: основной цвет знака и цвет акцента берём из CSS-переменных страницы
  var css = getComputedStyle(document.documentElement);
  function col(v, def) { var x = (css.getPropertyValue(v) || '').trim(); return x || def; }
  var mat = new THREE.MeshPhysicalMaterial({ color: col('--ld-mark', '#0c0d10'), metalness: 0.15, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.06, envMapIntensity: 1.25 });
  var matAcc = mat.clone(); matAcc.color.set(col('--ld-mark-acc', col('--ld-acc', '#2b4c7e')));
  rim.color.set(col('--ld-acc-l', '#9db7e0'));
  // смена палитры в демо-переключателе
  window.__ld3d = function () { css = getComputedStyle(document.documentElement); mat.color.set(col('--ld-mark', '#0c0d10')); matAcc.color.set(col('--ld-mark-acc', col('--ld-acc', '#2b4c7e'))); rim.color.set(col('--ld-acc-l', '#9db7e0')); };
  var group = new THREE.Group(), inner = new THREE.Group();
  // accent3d: "mark" красит детали акцента в основной цвет (у «Лидер Дент» цилиндр графитовый, а в цвете акцента дуги ring)
  [['mark', mat], ['accent', parts.accent3d === 'mark' ? mat : matAcc], ['ring', matAcc]].forEach(function (kv) {
    var list = parts[kv[0]] || [];
    if (!list.length) return;
    var svg = '<svg xmlns="http://www.w3.org/2000/svg">' + list.map(function (d) { return '<path fill-rule="evenodd" d="' + d + '"/>'; }).join('') + '</svg>';
    new SVGLoader().parse(svg).paths.forEach(function (p) {
      SVGLoader.createShapes(p).forEach(function (sh) {
        var g = new THREE.ExtrudeGeometry(sh, { depth: 46, bevelEnabled: true, bevelThickness: 5, bevelSize: 3, bevelSegments: 4, curveSegments: 18 });
        inner.add(new THREE.Mesh(g, kv[1]));
      });
    });
  });
  inner.scale.set(1, -1, 1);
  var bb = new THREE.Box3().setFromObject(inner), ctr = bb.getCenter(new THREE.Vector3()), size = bb.getSize(new THREE.Vector3());
  inner.position.set(-ctr.x, -ctr.y, -ctr.z);
  group.add(inner); scene.add(group);

  // мягкая синяя тень-пятно под знаком

  function fit() {
    var cv = renderer.domElement, w = cv.clientWidth, h = cv.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
    var dist = camera.position.z, vh = 2 * dist * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    var k = Math.min((vh * 0.82) / size.y, (vh * camera.aspect * 0.8) / size.x);
    group.scale.setScalar(k);
  }
  fit(); addEventListener('resize', fit);
  // на телефоне размер блока меняется вместе с вариантом оформления
  if (window.ResizeObserver) new ResizeObserver(fit).observe(box);

  var mx = 0, my = 0, tx = 0, ty = 0;
  addEventListener('pointermove', function (e) { mx = (e.clientX / innerWidth) * 2 - 1; my = (e.clientY / innerHeight) * 2 - 1; }, { passive: true });
  var visible = true;
  new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(box);
  var clock = new THREE.Clock(), intro = 0, angle = -0.5;
  function tick() {
    requestAnimationFrame(tick);
    if (!visible) return;
    var dt = Math.min(clock.getDelta(), 0.05);
    intro = Math.min(1, intro + dt * 0.6);
    tx += (mx - tx) * 0.05; ty += (my - ty) * 0.05;
    var e = 1 - Math.pow(1 - intro, 3);
    angle += dt * (reduce ? 0 : 0.4);
    group.rotation.y = angle + tx * 0.3;
    group.rotation.x = 0.06 + ty * 0.1 + (1 - e) * 0.4;
    renderer.render(scene, camera);
  }
  tick();
  box.classList.add('is-ready');
})();
