/* Стартовая заставка: логотип клиники собирается из сегментов.
   Знак (пути .pl-seg) режется на диагональные полосы, полосы слетаются, по знаку проходит блик,
   детали в цвете акцента (.pl-acc) опускаются сверху, дуги вокруг знака (.pl-ring, если есть) поворачиваются на место,
   затем подпись по буквам и раскрытие по диагонали.
   Границы полос считаются по размеру знака, поэтому подходит любой логотип из logo_parts.json. */
(function () {
  var d = document.documentElement, pl = document.getElementById('pl');
  var heroStart = null, released = false;
  // app.js вызывает старт анимации героя через этот хук, когда заставка уходит
  window.__auStart = function (fn) { if (released || !pl) fn(); else heroStart = fn; };
  function release() {
    if (released) return; released = true;
    d.classList.remove('au-loading');
    if (heroStart) heroStart();
  }
  if (!pl) { release(); return; }
  // заставка один раз за визит: при повторном открытии в той же вкладке сразу страница
  if (d.classList.contains('au-nopl')) { release(); pl.remove(); return; }
  try { sessionStorage.setItem('au-pl', '1'); } catch (e) {}
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !window.gsap) { release(); pl.remove(); return; }

  var NS = 'http://www.w3.org/2000/svg', svg = pl.querySelector('.pl__logo');
  var segs = [].slice.call(svg.querySelectorAll('.pl-seg:not(.pl-acc)')), acc = [].slice.call(svg.querySelectorAll('.pl-acc'));
  var ring = [].slice.call(svg.querySelectorAll('.pl-ring'));
  var letters = svg.querySelectorAll('.pl-l'), defs = svg.querySelector('defs'), shards = svg.querySelector('.pl__shards');
  var markG = svg.querySelector('.pl__mark');
  // рамка только режущихся частей знака, без дуг и деталей акцента
  function box(list) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    list.forEach(function (el) { var b = el.getBBox(); x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height); });
    return { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
  }
  var bb = box(segs), rb = ring.length ? box(ring) : bb;

  // Полосы под наклоном K, как срезы одного камня; c = y - K * x
  var K = -0.62, N = 8, pad = 4;
  var x0 = bb.x - pad, x1 = bb.x + bb.width + pad;
  var cs = [[bb.x, bb.y], [bb.x + bb.width, bb.y], [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]].map(function (p) { return p[1] - K * p[0]; });
  var cTop = Math.min.apply(0, cs) - pad, cBot = Math.max.apply(0, cs) + pad, step = (cBot - cTop) / N;
  var parts = [];
  for (var i = 0; i < N; i++) {
    var c0 = cTop + step * i - 0.6, c1 = cTop + step * (i + 1) + 0.6;
    var cp = document.createElementNS(NS, 'clipPath'); cp.id = 'pl-band-' + i;
    var poly = document.createElementNS(NS, 'polygon');
    poly.setAttribute('points', [x0, K * x0 + c0, x1, K * x1 + c0, x1, K * x1 + c1, x0, K * x0 + c1].join(' '));
    cp.appendChild(poly); defs.appendChild(cp);
    var g = document.createElementNS(NS, 'g'); g.setAttribute('clip-path', 'url(#pl-band-' + i + ')');
    segs.forEach(function (src) { var p = src.cloneNode(); p.removeAttribute('class'); g.appendChild(p); });
    shards.appendChild(g); parts.push(g);
  }

  // Блик проходит по собранному знаку
  var glCp = document.createElementNS(NS, 'clipPath'); glCp.id = 'pl-glint-clip';
  var glRect = document.createElementNS(NS, 'rect'), gw = bb.width * 0.16;
  glRect.setAttribute('x', bb.x - gw * 6); glRect.setAttribute('y', bb.y - bb.height); glRect.setAttribute('width', gw); glRect.setAttribute('height', bb.height * 3);
  glRect.setAttribute('transform', 'rotate(28 ' + (bb.x + bb.width / 2) + ' ' + (bb.y + bb.height / 2) + ')');
  glCp.appendChild(glRect); defs.appendChild(glCp);
  var glint = document.createElementNS(NS, 'g'); glint.setAttribute('class', 'pl-glint'); glint.setAttribute('clip-path', 'url(#pl-glint-clip)'); glint.setAttribute('fill', 'url(#pl-gold)');
  segs.forEach(function (src) { var p = src.cloneNode(); p.removeAttribute('class'); p.style.opacity = 1; glint.appendChild(p); });
  markG.appendChild(glint);

  var num = pl.querySelector('[data-pl-num]'), counter = { v: 0 };
  var g = gsap, tl = g.timeline({ defaults: { ease: 'power3.out' } });
  g.set(segs.concat(acc, ring), { autoAlpha: 0 });
  g.set('.pl__count', { autoAlpha: 1 });
  // заставка не дольше 2 секунд: весь таймлайн вдвое быстрее
  tl.timeScale(2);
  window.__plTl = tl;
  var dbg = /plpause/.test(location.search); if (dbg) tl.pause();
  var sh = bb.height * 0.08;

  tl.to(counter, { v: 100, duration: 3.1, ease: 'power1.inOut', onUpdate: function () { num.textContent = Math.round(counter.v); } }, 0)
    .from(parts, {
      x: function (k) { return (k % 2 ? 1 : -1) * (bb.width * 0.25 + k * sh * 0.4); },
      y: function (k) { return (k - N / 2) * sh; },
      rotation: function (k) { return (k % 2 ? 1 : -1) * (14 + k * 2); },
      transformOrigin: '50% 50%', autoAlpha: 0, duration: 1.15, stagger: { each: 0.07, from: 'edges' }, ease: 'expo.out'
    }, 0.15)
    .fromTo(ring, { autoAlpha: 0, rotation: -160, svgOrigin: (rb.x + rb.width / 2) + ' ' + (rb.y + rb.height / 2) }, { autoAlpha: 1, rotation: 0, svgOrigin: (rb.x + rb.width / 2) + ' ' + (rb.y + rb.height / 2), duration: 1.6, ease: 'expo.out', stagger: 0.1 }, 0.1)
    .to(segs, { autoAlpha: 1, duration: 0.2 }, 1.5)
    .set(shards, { autoAlpha: 0 }, 1.7)
    .fromTo(glRect, { attr: { x: bb.x - gw * 6 } }, { attr: { x: bb.x + bb.width + gw * 4 }, duration: 1.1, ease: 'power2.inOut' }, 1.5)
    .fromTo(acc, { autoAlpha: 0, y: -bb.height * 0.4, rotation: -14, transformOrigin: '50% 50%' }, { autoAlpha: 1, y: 0, rotation: 0, duration: 0.9, ease: 'back.out(1.6)', stagger: 0.08 }, 1.75)
    .fromTo(letters, { autoAlpha: 0, y: sh }, { autoAlpha: 1, y: 0, duration: 0.6, stagger: 0.035 }, 2.15)
    .to('.pl__count', { autoAlpha: 0, duration: 0.3 }, 3.2)
    .fromTo('.pl__seam', { clipPath: 'inset(0% 100% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.45, ease: 'power2.inOut' }, 3.1)
    .to(svg, { scale: 0.86, autoAlpha: 0, duration: 0.6, ease: 'power2.in' }, 3.35)
    .add(release, 3.55)
    .to('.pl__half--a', { yPercent: -100, duration: 1.0, ease: 'expo.inOut' }, 3.55)
    .to('.pl__half--b', { yPercent: 100, duration: 1.0, ease: 'expo.inOut' }, 3.55)
    .to('.pl__seam', { autoAlpha: 0, duration: 0.3 }, 3.6)
    .add(function () { pl.remove(); });

  // если вкладка открыта в фоне, не держим страницу
  if (!dbg) setTimeout(function () { release(); if (pl.isConnected) pl.remove(); }, 3000);
})();
