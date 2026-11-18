/* Open Indus site script: theme switch on every page, task list on the tracker page. No dependencies. */
(function () {
  var root = document.documentElement;

  // Theme: Auto -> Light -> Dark. Saved per browser; works without storage.
  var btn = document.getElementById('theme'), label = document.getElementById('theme-label');
  function current() { return root.getAttribute('data-theme') || 'auto'; }
  function show() {
    var t = current(), name = t === 'auto' ? 'Auto' : t === 'light' ? 'Light' : 'Dark';
    if (label) label.textContent = name;
    if (btn) btn.setAttribute('aria-label', 'Colour theme: ' + name.toLowerCase() + '. Press to change.');
  }
  if (btn) btn.addEventListener('click', function () {
    var next = { auto: 'light', light: 'dark', dark: 'auto' }[current()];
    if (next === 'auto') root.removeAttribute('data-theme'); else root.setAttribute('data-theme', next);
    try { if (next === 'auto') localStorage.removeItem('oi-theme'); else localStorage.setItem('oi-theme', next); } catch (e) {}
    show();
  });
  show();

  // Phone menu (CSS shows the button at 900px and below). Disclosure pattern: the button toggles the list,
  // Escape closes it and returns focus to the button, a click or focus outside the header closes it.
  var head = document.getElementById('site-head'), menu = document.getElementById('menu-btn');
  function setMenu(open, refocus) {
    if (!head || !menu) return;
    head.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
    if (!open && refocus) menu.focus();
  }
  if (menu) {
    menu.addEventListener('click', function () { setMenu(menu.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { setMenu(false, true); }
    });
    document.addEventListener('click', function (e) { if (!head.contains(e.target)) setMenu(false); });
    head.addEventListener('focusout', function (e) { if (e.relatedTarget && !head.contains(e.relatedTarget)) setMenu(false); });
    window.matchMedia('(min-width: 901px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });
  }


  // Grouped menus (Research, Resources): open on hover (CSS) or a tap; one open at a time; Escape or a tap elsewhere closes.
  var dds = [].slice.call(document.querySelectorAll('.site-nav .dd'));
  function ddClose(d) { d.classList.remove('open'); d.querySelector('button').setAttribute('aria-expanded', 'false'); }
  dds.forEach(function (d) {
    var b = d.querySelector('button');
    b.addEventListener('click', function (e) {
      e.stopPropagation(); var on = !d.classList.contains('open'); dds.forEach(ddClose);
      if (on) { d.classList.add('open'); b.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) { dds.forEach(function (d) { if (!d.contains(e.target)) ddClose(d); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') dds.forEach(ddClose); });

  // News: one detail level for the whole feed (a sentence, plain words, technical); remembered per viewer.
  var zb = [].slice.call(document.querySelectorAll('.zoombar button'));
  if (zb.length) {
    var feeds = [].slice.call(document.querySelectorAll('.news-feed'));
    var setZoom = function (z) {
      feeds.forEach(function (f) { f.setAttribute('data-zoom', z); });
      zb.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-zoom') === z)); });
      try { localStorage.setItem('oi-zoom', z); } catch (e) {}
    };
    zb.forEach(function (b) { b.addEventListener('click', function () { setZoom(b.getAttribute('data-zoom')); }); });
    try { var z0 = localStorage.getItem('oi-zoom'); if (z0) setZoom(z0); } catch (e) {}
  }

  // Hero seal: turns with a fine pointer and the light swings with it. Eases to the target, then stops
  // (no frames while the pointer is still), and ignores the pointer while the seal is off screen.
  // Touch devices and reduced motion keep the fixed pose set in CSS.
  var seal = document.getElementById('seal');
  if (seal && !matchMedia('(prefers-reduced-motion: reduce)').matches && matchMedia('(hover: hover) and (pointer: fine)').matches) {
    var L = [document.getElementById('L1'), document.getElementById('L2')], scene = seal.parentNode;
    var RX = 12, RY = -18, tx = RX, ty = RY, cx = RX, cy = RY, raf = 0, visible = true;
    var frame = function () {
      cx += (tx - cx) * 0.12; cy += (ty - cy) * 0.12;
      var done = Math.abs(tx - cx) < 0.05 && Math.abs(ty - cy) < 0.05;
      if (done) { cx = tx; cy = ty; }
      seal.style.setProperty('--rx', cx.toFixed(2) + 'deg');
      seal.style.setProperty('--ry', cy.toFixed(2) + 'deg');
      var az = (225 + (cy - RY) * 1.5 - (cx - RX) * 1.2).toFixed(1);
      L.forEach(function (l) { if (l) l.setAttribute('azimuth', az); });
      scene.style.setProperty('--sx', (-cy * 0.75).toFixed(1) + 'px');
      raf = done ? 0 : requestAnimationFrame(frame);
    };
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(scene);
    window.addEventListener('pointermove', function (e) {
      if (!visible) return;
      var r = scene.getBoundingClientRect();
      var dx = Math.max(-1, Math.min(1, (e.clientX - (r.left + r.width / 2)) / (window.innerWidth / 2)));
      var dy = Math.max(-1, Math.min(1, (e.clientY - (r.top + r.height / 2)) / (window.innerHeight / 2)));
      ty = RY + dx * 12; tx = RX - dy * 9;   // tilt range: rotateY -30..-6deg, rotateX 3..21deg
      if (!raf) raf = requestAnimationFrame(frame);
    }, { passive: true });
  }

  // Tracker
  var dataEl = document.getElementById('board');
  if (!dataEl) return;
  var D = JSON.parse(dataEl.textContent), T = D.tasks;
  var REPO = JSON.parse(document.getElementById('repo').textContent);
  var $ = function (id) { return document.getElementById(id); };
  var el = function (tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  var MS = { M1: 'Names on seals found abroad', M2: 'Test the 2026 published readings', M3: 'South Indian graffiti beside early Tamil',
             M4: 'Sign meaning classes', M5: 'Research sweep', M6: 'Red team' };
  var VERDICT = { positive: ['Held up', 'good'], negative: ['Ruled out', 'out'], mixed: ['Mixed', 'weak'], untestable: ["Can\u2019t test yet", 'wait'], data: ['Data built', ''], tool: ['Tool built', ''] };
  var STATE = { running: ['Being worked on', 'run'], ready: ['Ready', ''], blocked: ['Waiting', 'wait'] };
  var count = function (f) { return T.filter(f).length; };

  [[count(function (t) { return t.state === 'done'; }), 'tasks finished'],
   [count(function (t) { return t.state === 'running'; }), 'being worked on'],
   [count(function (t) { return t.verdict === 'positive'; }), 'results that held up'],
   [count(function (t) { return t.verdict === 'negative'; }), 'routes ruled out']
  ].forEach(function (s) { var d = el('div', 'stat'); d.appendChild(el('b', '', s[0])); d.appendChild(el('span', '', s[1])); $('stats').appendChild(d); });

  Object.keys(MS).forEach(function (m) {
    var all = T.filter(function (t) { return t.ms === m; }); if (!all.length) return;
    var done = all.filter(function (t) { return t.state === 'done'; }).length;
    var name = el('div', '', m + ' · ' + MS[m]);
    $('ms').appendChild(name);
    var tr = el('span', 'mtrack'), f = el('span', 'mfill'); f.style.width = (100 * done / all.length) + '%'; tr.appendChild(f);
    tr.setAttribute('aria-hidden', 'true'); $('ms').appendChild(tr);
    var n = el('div', 'n', done + ' of ' + all.length); n.setAttribute('aria-label', done + ' of ' + all.length + ' tasks finished'); $('ms').appendChild(n);
  });

  var FILTERS = [['open', 'Not finished'], ['positive', 'Held up'], ['mixed', 'Mixed'], ['negative', 'Ruled out'], ['all', 'All']];
  var cur = 'open';
  try { cur = localStorage.getItem('oi-filter') || 'open'; } catch (e) {}
  function match(t) { return cur === 'all' ? true : cur === 'open' ? t.state !== 'done' : t.verdict === cur; }
  function draw() {
    var box = $('tasks'); box.textContent = '';
    var rows = T.filter(match).sort(function (a, b) { return (a.state === 'done') - (b.state === 'done') || b.id - a.id; });
    if (!rows.length) box.appendChild(el('p', 'note', 'No tasks in this group yet. Choose All to see every task.'));
    $('count').textContent = rows.length + (rows.length === 1 ? ' task shown' : ' tasks shown');
    rows.forEach(function (t) {
      var d = el('details', 'task'), s = el('summary');
      s.appendChild(el('span', 'id', '#' + t.id));
      s.appendChild(el('span', 't', t.title));
      var p = t.state === 'done' ? (VERDICT[t.verdict] || ['Done', '']) : STATE[t.state];
      s.appendChild(el('span', 'tag ' + p[1], p[0]));
      d.appendChild(s);
      var more = el('div', 'more-t');
      more.appendChild(el('span', '', (t.ms + ' · ' + (MS[t.ms] || ''))));
      var txt = t.state === 'done' ? (t.summary || '') :
        t.state === 'blocked' ? 'Waits for task ' + t.waits.map(function (w) { return '#' + w; }).join(', ') + ' to finish.' :
        t.state === 'running' ? 'Claimed by agent ' + t.owner + '.' : 'Ready for the next free agent.';
      more.appendChild(el('p', '', txt));
      if (t.path) {
        var a = el('a', 'file', t.path); a.href = REPO + '/blob/main/' + t.path; more.appendChild(a);
      }
      d.appendChild(more);
      box.appendChild(d);
    });
    Array.prototype.forEach.call($('filters').children, function (b) { b.setAttribute('aria-pressed', String(b.dataset.f === cur)); });
  }
  FILTERS.forEach(function (f) {
    var n = f[0] === 'all' ? T.length : f[0] === 'open' ? count(function (t) { return t.state !== 'done'; }) : count(function (t) { return t.verdict === f[0]; });
    var b = el('button', '', f[1] + ' ' + n); b.type = 'button'; b.dataset.f = f[0];
    b.addEventListener('click', function () { cur = f[0]; try { localStorage.setItem('oi-filter', cur); } catch (e) {} draw(); });
    $('filters').appendChild(b);
  });
  draw();
})();

/* Newsletter signup (footer). Endpoint and CORS are set in newsletter/; nobody is subscribed until they confirm by email. */
(function () {
  var ENDPOINT = 'https://hardy-capybara-487.convex.site/subscribe';
  var form = document.getElementById('newsletter-form');
  if (!form) return;
  var input = form.querySelector('#newsletter-email');
  var button = form.querySelector('button[type=submit]');
  var status = form.querySelector('#newsletter-status');
  var OFFLINE = 'You are offline. Try again when you are connected.';
  function say(text, state) { status.textContent = text; form.setAttribute('data-state', state); }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = input.value.trim();
    if (!email || !input.checkValidity()) {
      input.setAttribute('aria-invalid', 'true');
      say('Enter a valid email address, like name@example.com.', 'error');
      input.focus();
      return;
    }
    input.removeAttribute('aria-invalid');
    if (navigator.onLine === false) { say(OFFLINE, 'error'); return; }
    button.disabled = true;
    form.setAttribute('aria-busy', 'true');
    say('Sending…', 'sending');
    fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, source: location.pathname, website: form.querySelector('#newsletter-website').value })
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (res.ok && data.ok) {
          form.reset();
          say('Almost done. Check your inbox for a confirmation email. You are not subscribed until you click the link in it.', 'success');
        } else if (res.status === 429) {
          say('Too many tries. Wait a few minutes and try again.', 'error');
        } else {
          say(data.message || 'Unable to sign you up. Try again in a moment.', 'error');
        }
      });
    }).catch(function () {
      say(navigator.onLine === false ? OFFLINE : 'Unable to reach the server. Check your connection and try again.', 'error');
    }).then(function () { button.disabled = false; form.removeAttribute('aria-busy'); });
  });
})();
