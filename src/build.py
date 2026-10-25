# Собирает index.html «Лидер Дент» из вёрстки vaitis-preview (эталон Lava Dental):
# та же структура и классы, новый контент, палитра и прелоадер. Шаблон: akademiya-ulybki.
import re, json, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, 'src/vaitis-index.html'), encoding='utf-8').read()

# ---------- контакты: два филиала ----------
PHONE = '+7 (8652) 409-700'
TEL = '+78652409700'
MAIL = 'liderdent26@mail.ru'
TG = 'https://t.me/liderdent_stav'
WA = 'https://wa.me/79624400504'
VK = 'https://vk.com/liderdent.stav'
OK = 'https://ok.ru/stomatologiya.liderdent'
BR = [  # филиалы: адрес, телефон, часы, карты, координаты входа (широта, долгота)
    dict(key='okt', name='Октябрьская', addr='ул. Октябрьская, 202', floor='2 этаж, 18-й микрорайон',
         phone=PHONE, tel=TEL, hours='Пн-Сб с 9:00 до 24:00, Вс с 9:00 до 20:00',
         hrs={'0': [540, 1200], 'd': [540, 1440]},
         ya='https://yandex.ru/maps/org/lider_dent/103452608871/', ya_id='103452608871',
         gis='https://2gis.ru/stavropol/firm/70000001027420233', geo=(45.077697, 41.939529),
         ent='ООО «Лидер-Дент», ИНН 2636212195, ОГРН 1162651074805',
         lic='лицензия Л041-01197-26/00323220 от 30.10.2018',
         perks='Парковка, велопарковка, детский приём, оплата картой, рассрочка'),
    dict(key='tol', name='Л. Толстого', addr='ул. Л. Толстого, 121Б', floor='2 этаж',
         phone='+7 (8652) 22-26-02', tel='+78652222602', hours='Ежедневно с 9:00 до 20:00',
         hrs={'0': [540, 1200], 'd': [540, 1200]},
         ya='https://yandex.ru/maps/org/lider_dent/120244608451/', ya_id='120244608451',
         gis='https://2gis.ru/stavropol/firm/70000001068840490', geo=(45.022527, 41.953938),
         ent='ООО «Стом Лайн», ИНН 2635241355, ОГРН 1192651010936',
         lic='лицензия Л041-01197-26/00335833 от 12.11.2019',
         perks='Парковка, Wi-Fi, детский приём, оплата картой, рассрочка'),
]
for b in BR:
    b['route'] = f'https://yandex.ru/maps/?rtext=~{b["geo"][0]},{b["geo"][1]}'
YA, GIS, ROUTE = BR[0]['ya'], BR[0]['gis'], BR[0]['route']
ARROW = '<svg viewBox="0 0 60 60"><path d="M24 36 36 24M27 24h9v9"/></svg>'

# рейтинги на 25.10.2026 (Яндекс Карты: оба филиала вместе; 2ГИС: Октябрьская)
YA_RATE, YA_VOTES, YA_REV = '5,0', 579, 378
GIS_RATE, GIS_VOTES, GIS_REV = '4,9', 673, 614


def block(start, end_tag, new):
    """Заменяет фрагмент от start до ближайшего end_tag включительно."""
    global s
    i = s.index(start)
    j = s.index(end_tag, i) + len(end_tag)
    s = s[:i] + new + s[j:]


def plural(n, one, few, many):
    n = abs(n) % 100
    if 10 < n < 20: return many
    n %= 10
    return one if n == 1 else few if 1 < n < 5 else many


# Кадры, которые нужно согласовать с клиникой: на сайте у них плашка «уточнить»
ASK = {}
SHOW_ASK = True  # перед показом клиенту False

def _dims(p):
    try:
        from PIL import Image
        return Image.open(os.path.join(ROOT, p.split('?')[0])).size
    except Exception:
        return None

# ширина показа на компьютере в vw, замерена в браузере (src/img-sizes.json)
try:
    IMG_VW = json.load(open(os.path.join(ROOT, 'src/img-sizes.json'), encoding='utf-8'))
except Exception:
    IMG_VW = {}

def img(path, alt='', cls='', style='', extra=''):
    if not path:
        return ''
    a = f'<img src="{path}" alt="{html.escape(alt)}" loading="lazy" decoding="async" onerror="umImg(this)"'
    d = _dims(path)
    if d and 'width=' not in extra:
        a += f' width="{d[0]}" height="{d[1]}"'
    # у крупных фото есть копия 900 px для телефонов
    base = path.split('?')[0]
    q = path[len(base):]
    m = base[:-5] + '-m.webp'
    if base.endswith('.webp') and os.path.exists(os.path.join(ROOT, m)) and 'srcset' not in extra and d:
        dm = _dims(m)
        a += f' srcset="{m}{q} {dm[0]}w, {path} {d[0]}w" sizes="(max-width: 760px) 60vw, {IMG_VW.get(base, 50)}vw"'
    if cls: a += f' class="{cls}"'
    if style: a += f' style="{style}"'
    if extra: a += ' ' + extra
    a += '>'
    if SHOW_ASK and base in ASK:
        a += f'<span class="au-ask" title="{ASK[base]}">уточнить</span>'
    return a


# ---------- фото клиники (images/real, из открытых источников: сайт, Яндекс Карты, 2ГИС, ВК) ----------
P = json.load(open(os.path.join(ROOT, 'src/photos.json'), encoding='utf-8'))
ASK.update(P.get('ask', {}))

# ---------- HEAD ----------
SITE_URL = 'https://ilyasorokin94-hue.github.io/lider-dent/'
TITLE = 'Стоматология «Лидер Дент» в Ставрополе: импланты, брекеты, лечение до полуночи'
DESC = 'Семейная стоматология в Ставрополе: Октябрьская, 202 (до 24:00) и Л. Толстого, 121Б. Имплантация и «Всё на 4», брекеты и элайнеры, лечение зубов, детский приём. Осмотр бесплатно.'
THEME = '#15171c'
head_end = s.index('</head>')
head = s[:head_end]
head = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', head)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', head)
head = re.sub(r'<link rel="canonical"[^>]*>\n', '', head)
head = re.sub(r'<meta property="og:[^>]*>\n', '', head)
head = head.replace('<meta name="theme-color" content="#ffffff">',
                    f'<meta property="og:type" content="website">\n<meta property="og:title" content="{TITLE}">\n<meta property="og:description" content="{DESC}">\n<meta property="og:locale" content="ru_RU">\n<meta property="og:url" content="{SITE_URL}">\n<meta property="og:image" content="{SITE_URL}images/og.jpg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="theme-color" content="{THEME}">')
head = re.sub(r'<link rel="apple-touch-icon"[^>]*>\n', '', head)
head = head.replace('<link rel="icon" type="image/svg+xml" href="images/brand/favicon.svg">', '<link rel="icon" type="image/svg+xml" href="images/brand/favicon.svg">\n<link rel="apple-touch-icon" href="images/brand/apple-touch-icon.png">')
head = head.replace('<link rel="stylesheet" href="assets/styles.css?v=d847b31c">',
                    '<link rel="stylesheet" href="assets/styles.css?v=ld1">\n<link rel="stylesheet" href="assets/lider-dent.css?v=ld1">')
# свой прелоадер вместо интро Вайтис: js-intro не ставим, держим страницу под заставкой
head = head.replace('if(d.dataset.page==="home"&&!sessionStorage.getItem("um2-intro"))d.classList.add("js-intro")',
                    'if(sessionStorage.getItem("au-pl"))d.classList.add("au-nopl");else d.classList.add("au-loading")')
head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', '', head, flags=re.S)
def ld_place(b, main=False):
    o = {"@type": "Dentist", "name": f'Стоматология «Лидер Дент», {b["addr"]}', "telephone": b['phone'],
         "address": {"@type": "PostalAddress", "streetAddress": b['addr'], "addressLocality": "Ставрополь", "addressCountry": "RU"},
         "geo": {"@type": "GeoCoordinates", "latitude": b['geo'][0], "longitude": b['geo'][1]},
         "openingHours": ["Mo-Sa 09:00-24:00", "Su 09:00-20:00"] if b['key'] == 'okt' else "Mo-Su 09:00-20:00"}
    if main:
        o = {"@context": "https://schema.org", **o, "name": "Стоматология «Лидер Дент»", "email": MAIL, "sameAs": [YA, GIS, VK, TG, OK]}
    return o
LD = ld_place(BR[0], True)
LD["address"]["postalCode"] = "355047"
LD["department"] = [ld_place(BR[1])]
head += '<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>\n'
head = head.replace('<script src="assets/cookie.js?v=886e3f70" data-privacy="privacy/" data-ym="" defer></script>',
                    '<script src="assets/cookie.js?v=886e3f70" data-privacy="#" data-ym="" defer></script>')
head = re.sub(r'<script src="assets/hero-3d.js[^"]*" defer></script>\n', '<script>addEventListener("load",function(){var go=function(){var t=document.createElement("script");t.src="assets/logo-3d.js?v=ld1";document.head.appendChild(t)};window.requestIdleCallback?requestIdleCallback(go,{timeout:1500}):setTimeout(go,300)})</script>\n', head)
# латиницу не грузим заранее: в заголовке первого экрана только кириллица
head = re.sub(r'<link rel="preload" href="assets/fonts/[a-z-]+-latin\.woff2"[^>]*>\n', '', head)
head = head.replace('<script src="assets/app.js?v=9b97a404" defer></script>', '<script src="assets/preloader.js?v=ld1" defer></script>\n<script src="assets/app.js?v=ld1" defer></script>')
s = head + s[head_end:]

# ---------- демо-плашка, прелоадер ----------
# logo_parts.json: viewBox всего логотипа, markBox знака, mark (пути знака: режутся на осколки),
# accent (детали знака в цвете акцента), ring (дуги вокруг знака), letters (буквы подписи)
logo = json.load(open(os.path.join(ROOT, 'logo_parts.json')))
VB = logo['viewBox']
# ring (необязательно): кольцо или дуги вокруг знака, в заставке поворачиваются на место
mark = ''.join(f'<path class="pl-ring" fill-rule="evenodd" d="{d}"/>' for d in logo.get('ring', []))
mark += ''.join(f'<path class="pl-seg" fill-rule="evenodd" d="{d}"/>' for d in logo['mark'])
mark += ''.join(f'<path class="pl-seg pl-acc" fill-rule="evenodd" d="{d}"/>' for d in logo.get('accent', []))
letters = ''.join(f'<path class="pl-l" style="--i:{i}" fill-rule="evenodd" d="{d}"/>' for i, d in enumerate(logo['letters']))
PRELOADER = f'''<div class="pl" id="pl" aria-hidden="true">
  <div class="pl__half pl__half--a"></div><div class="pl__half pl__half--b"></div><svg class="pl__seam" viewBox="0 0 100 100" preserveAspectRatio="none"><line x1="-2" y1="77.05" x2="102" y2="35.45" pathLength="1"/></svg>
  <svg class="pl__logo" viewBox="{VB}">
    <defs>
      <linearGradient id="pl-gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" class="pl-g2"/><stop offset="1" class="pl-g3"/></linearGradient>
      <linearGradient id="pl-ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" class="pl-g2"/><stop offset=".5" stop-color="#ffffff"/><stop offset="1" class="pl-g2"/></linearGradient>
    </defs>
    <g class="pl__shards"></g>
    <g class="pl__mark">{mark}</g>
    <g class="pl__word">{letters}</g>
  </svg>
  <div class="pl__count"><span data-pl-num>0</span>%</div>
</div>'''
s = s.replace('<div class="demo-bar">Демонстрационный макет нового сайта стоматологии «Вайтис». Заявки из форм пока никуда не отправляются.</div>',
              '<div class="demo-bar">Демонстрационный макет нового сайта стоматологии «Лидер Дент». Заявки из форм пока никуда не отправляются.</div>')
s = s.replace('<div class="intro" aria-hidden="true"><div class="intro__bg"></div><img class="intro__mark" src="images/brand/header-logo-light.svg" alt=""></div>', PRELOADER)

# ---------- шапка и меню ----------
s = s.replace('aria-label="Вайтис. Стоматология в Одинцово, на главную"', 'aria-label="Лидер Дент. Стоматология в Ставрополе, на главную"')
s = s.replace('<span class="logo__text">Вайтис<small>стоматология в Одинцово</small></span>', '<span class="logo__text">Лидер Дент<small>стоматология в Ставрополе</small></span>')
s = s.replace('<span class="logo__unit">Стоматология</span>', '<span class="logo__unit">Семейная стоматология</span>')
s = s.replace('src="images/brand/header-logo.svg" alt="" width="184" height="48"', 'src="images/brand/header-logo.svg" alt="" width="218" height="48"')
s = s.replace('tel:+79037977688', 'tel:' + TEL).replace('+7 903 797-76-88', PHONE)
s = re.sub(r'<li class="nav__item"><a class="nav__link" href="ceny/">Цены</a>.*?</li>', '', s, count=1, flags=re.S)
s = re.sub(r'<li><a class="mnav__link" href="ceny/">Цены</a></li>|<a class="mnav__link" href="ceny/">Цены</a>', '', s)
s = re.sub(r'<details class="menu__svc">.*?</details>',
           '<a href="#services">Услуги</a>', s, flags=re.S)
s = s.replace('<a href="ceny/">Цены</a><a href="#akcii">Акции</a>', '<a href="#akcii">Акции</a>')

# часы из базы Вайтиса (ежедневно 9:00 до 21:00) меняем на часы двух филиалов
NB = '\xa0'
for a, b in [
    (f'<small>Ежедневно с{NB}9:00 до{NB}21:00</small>', f'<small>С{NB}9:00, Пн-Сб до{NB}24:00</small>'),
    (f'<span class="note">Ежедневно с{NB}9:00 до{NB}21:00. Перезвоним в{NB}часы работы.</span>', f'<span class="note">Октябрьская: Пн-Сб с{NB}9:00 до{NB}24:00, Вс до{NB}20:00. Л.{NB}Толстого: ежедневно с{NB}9:00 до{NB}20:00.</span>'),
    (f'удобное время. Ежедневно с{NB}9:00 до{NB}21:00.</p>', f'удобное время. Звоним с{NB}9:00, с{NB}понедельника по{NB}субботу до{NB}полуночи.</p>'),
    (f'Заявки после 21:00 перезваниваем с{NB}9:00 утра. </p>', f'Ночные заявки перезваниваем с{NB}9:00 утра.</p>'),
    (f'<p class="modal__note">Ежедневно с{NB}9:00 до{NB}21:00.</p>', f'<p class="modal__note">С{NB}9:00, с{NB}понедельника по{NB}субботу до{NB}24:00.</p>'),
]:
    assert a in s, a
    s = s.replace(a, b)

# ---------- HERO ----------
def rot(lines):
    out = ''
    for words in lines:
        out += '<span aria-hidden="true">' + ' '.join(f'<span class="sw"><span style="--i:{i}">{w}</span></span>' for i, w in enumerate(words)) + '</span>'
    return out
ROT = [['На Октябрьской', 'принимаем', 'до 24:00.'],
       ['Ставрополь,', 'Октябрьская, 202', 'и Л. Толстого, 121Б.'],
       ['Осмотр', 'и консультация', 'бесплатно.']]
LOGO_3D = json.dumps({'mark': logo['mark'], 'accent': logo.get('accent', []), 'ring': logo.get('ring', []), 'accent3d': logo.get('accent3d', 'accent')})
flat = ''.join(f'<path class="hx__ring" d="{d}"/>' for d in logo.get('ring', [])) + ''.join(f'<path d="{d}"/>' for d in logo['mark'])
flat += ''.join(f'<path class="{"" if logo.get("accent3d") == "mark" else "hx__acc"}" d="{d}"/>' for d in logo.get('accent', []))
HERO = f'''<section class="hero hero--v hero--v1" aria-labelledby="h1"><div class="hx--a" id="hx" data-v="1" aria-hidden="true"><svg class="hx__flat" fill-rule="evenodd" viewBox="{logo.get('markBox', VB)}" preserveAspectRatio="xMidYMid meet">{flat}</svg></div><script type="application/json" id="logo-a">{LOGO_3D}</script><div class="wrap hero__in">
  <div class="hero__text">
    <h1 id="h1"><span data-split>Ваша улыбка</span> <span class="hv__l2" data-split>выходит в лидеры.</span></h1>
    <p class="hv__rot"><span class="sr">На Октябрьской принимаем до 24:00. Ставрополь, Октябрьская, 202 и Л. Толстого, 121Б. Осмотр и консультация бесплатно.</span>{rot(ROT)}</p>
    <div class="hero__actions"><a class="btn btn--lg" href="zapis" data-modal="book" data-magnet>Записаться на бесплатную консультацию</a></div>
  </div>
</div></section>'''
block('<section class="hero hero--v', '</section>', HERO)
# зуб Вайтис и переключатель его вариантов убираем
s = re.sub(r'<div class="hx hx--tooth".*?</div>\n', '', s, count=1)
s = re.sub(r'<div class="hx-switch".*?</div>\n', '', s, count=1)

# ---------- врачи ----------
# Только врачи со страницы «Наша команда» lider-dent26.ru. Порядок: хирургия, ортопедия, ортодонтия, терапия.
DOCS = [
    dict(slug='gadzhiev', fam='Гаджиев', name='Кямран', otch='Надирович', role='Хирург-имплантолог', short='Имплантолог',
         focus='Имплантация и «Всё на 4», удаление зубов мудрости, синус-лифтинг', tags='hirurgiya'),
    dict(slug='rudnev', fam='Руднев', name='Даниил', otch='Сергеевич', role='Ортопед', short='Ортопед',
         focus='Коронки, протезы, протезирование на имплантах', tags='protezirovanie'),
    dict(slug='nikonova', fam='Никонова', name='Наталья', otch='Николаевна', role='Ортодонт', short='Ортодонт',
         focus='Брекеты и элайнеры, исправление прикуса', tags='ortodontiya'),
    dict(slug='koldasov', fam='Колдасов', name='Мухамедали', otch='Хамитович', role='Терапевт, хирург', short='Терапевт, хирург',
         focus='Лечение кариеса и каналов, удаление зубов', tags='lechenie-zubov hirurgiya'),
    dict(slug='soloveva', fam='Соловьева', name='Ольга', otch='Анатольевна', role='Ортопед, терапевт', short='Ортопед',
         focus='Протезирование, лечение и восстановление зубов', tags='protezirovanie lechenie-zubov'),
    dict(slug='homutov', fam='Хомутов', name='Роман', otch='Олегович', role='Ортопед, терапевт', short='Ортопед',
         focus='Коронки и протезы, лечение кариеса и каналов', tags='protezirovanie lechenie-zubov'),
    dict(slug='shamarin', fam='Шамарин', name='Егор', otch='Николаевич', role='Терапевт', short='Терапевт',
         focus='Лечение кариеса и пульпита, реставрация зубов', tags='lechenie-zubov'),
    dict(slug='husejnova', fam='Хусейнова', name='Диана', otch='Султановна', role='Терапевт', short='Терапевт',
         focus='Лечение кариеса и каналов, эстетическая реставрация', tags='lechenie-zubov'),
    dict(slug='melkumova', fam='Мелкумова', name='Кристина', otch='Михайловна', role='Терапевт', short='Терапевт',
         focus='Лечение кариеса и каналов, эстетическая реставрация', tags='lechenie-zubov'),
    dict(slug='grigoryan', fam='Григорян', name='Гаяне', otch='Размиковна', role='Терапевт', short='Терапевт',
         focus='Лечение кариеса и каналов, эстетическая реставрация', tags='lechenie-zubov'),
    dict(slug='tekeeva', fam='Текеева', name='Камила', otch='Рашидовна', role='Стоматолог', short='Стоматолог',
         focus='Лечение зубов, профессиональная гигиена', tags='lechenie-zubov'),
]
# стаж, вуз и уточнённые направления с ПроДокторов и страниц врачей
DOC_EXTRA = json.load(open(os.path.join(ROOT, 'src/doctors.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'src/doctors.json')) else {}
for d in DOCS:
    d.update(DOC_EXTRA.get(d['slug'], {}))
    d['ini'] = d['name'][0] + d['fam'][0]
def doc_photo(d):
    p = f'images/doctors/{d["slug"]}.webp'
    return p if os.path.exists(os.path.join(ROOT, p)) else ''
FACES = [d for d in DOCS if doc_photo(d)][:4] or DOCS[:4]

trio = ''.join(f'<li><a href="#team" aria-label="{d["short"]}: {d["name"]} {d["fam"]}"><span class="hero__face" data-ph><span class="doc__initials" aria-hidden="true">{d["ini"]}</span>{img(doc_photo(d), d["name"] + " " + d["fam"])}</span><b>{d["short"]}</b><span>{d["name"]}<br>{d["fam"]}</span></a></li>' for d in FACES)
SLOGAN_T = 'Улыбка, которая всегда впереди.'
SLOGAN = f'''<section class="slogan on-dark" aria-label="{SLOGAN_T}">
  <div class="marquee" aria-hidden="true"><div class="marquee__track">{''.join(f'<span class="marquee__item">{SLOGAN_T} <em>{SLOGAN_T}</em></span>' for _ in range(4))}</div></div>
  <div class="slogan__head" aria-hidden="true"><p class="slogan__title"><span class="line">{SLOGAN_T}</span></p></div>
  <div class="slogan__more"><div class="wrap"><p class="au-slogan-sub">С 2018 года нам доверились больше 12 000 пациентов. Два филиала и 11 врачей в Ставрополе.</p><ul class="hero__trio" aria-label="Врачи клиники">{trio}</ul></div></div>
</section>'''
block('<section class="slogan on-dark"', '</section>', SLOGAN)

# ---------- КЛИНИКА (тур) ----------
CL, CL2 = P['CL'], P['CL2']
def tfig(p, alt, kind, hidden=False):
    return f'<figure class="tfig{" tfig--tall" if kind == "tall" else ""}"{" aria-hidden=\"true\"" if hidden else ""}><span class="tfig__img">{img(p, alt)}</span><figcaption>{alt}</figcaption></figure>'
row1 = ''.join(tfig(*c) for c in CL) + ''.join(tfig(*c, hidden=True) for c in CL)
row2 = ''.join(tfig(*c) for c in CL2) + ''.join(tfig(*c, hidden=True) for c in CL2)
TOUR_T = ['Здесь', 'улыбки', 'на первом', 'месте']
TOUR_P = 'Две клиники в Ставрополе: на Октябрьской, 202 и на Л. Толстого, 121Б. Семейная стоматология с 2018 года: лечим взрослых и детей, ставим импланты и брекеты, работаем по ДМС.'
def full(p):
    d = _dims(p)
    return f'srcset="{p} {d[0]}w" sizes="100vw"' if d else ''
def pwin(p, alt, ar, p0, p1, pos, cls=''):
    return f'<div class="ptour__item{cls}"><div class="ptour__win" style="--ar:{ar};--p0:{p0};--p1:{p1}"><span class="ptour__rail">{img(p, alt, "ptour__img", "object-position:" + pos, full(p))}</span></div></div>'
def pfig(p, alt, r, par=False):
    return f'<figure class="ptour__fig"{" data-par" if par else ""} style="--r:{r}"><span class="ptour__pic">{img(p, alt, extra=full(p))}</span></figure>'
M = P['mobile']
TOUR = f'''<section class="tour on-dark" id="clinic" aria-labelledby="tr-title">
  <div class="tour__pin">
    <div class="tour__frame">{img(P['frame'][0], P['frame'][1], style="object-position:50% 50%")}</div>
    <div class="tour__title wrap"><span class="label label--light">Клиника</span><h2 id="tr-title" data-split>{' '.join(TOUR_T)}</h2><p>{TOUR_P}</p><a class="btn btn--light" href="#contacts">Два адреса на карте</a></div>
  </div>
  <p class="tour__lead wrap">{TOUR_P}</p>
  <div class="tour__rows" aria-label="Фото клиники">
    <div class="tour__row" data-dir="-1">{row1}</div><div class="tour__row" data-dir="1">{row2}</div>
  </div>
  <div class="ptour">
    <div class="ptour__car"><div class="ptour__items">
      <div class="ptour__item ptour__item--empty"></div>
      {pwin(M['w1'][0], M['w1'][1], "3 / 4", .1, .6, "50% 40%")}{pwin(M['w2'][0], M['w2'][1], "1 / 1", .1, .6, "50% 38%")}{pwin(M['w3'][0], M['w3'][1], "3 / 2", .2, .7, "50% 60%", " ptour__item--left")}
      <div class="ptour__item ptour__item--main">{img(M['main'][0], M['main'][1], "ptour__img", "object-position:50% 50%", full(M['main'][0]))}<span class="ptour__shade"></span>
        <div class="ptour__slogan"><span class="label label--light"><span class="w" style="--i:0">Клиника</span></span><h2 class="ptour__title">{' '.join(f'<span class="w" style="--i:{i + 1}">{w}</span>' for i, w in enumerate(TOUR_T))}</h2></div></div>
      <div class="ptour__item ptour__item--right">{img(M['right'][0], M['right'][1], "ptour__img", "object-position:50% 40%", full(M['right'][0]))}</div>
    </div></div>
    <div class="ptour__spacer"></div>
    <div class="ptour__after">
      <div class="ptour__grid">{''.join(pfig(p, a, r, par) for p, a, r, par in M['grid'])}</div>
      <div class="ptour__text"><p>{TOUR_P}</p><a class="btn btn--light" href="#contacts">Два адреса на карте</a></div>
    </div>
  </div>
</section>'''
block('<section class="tour on-dark"', '</section>', TOUR)

# ---------- ПОЧЕМУ МЫ ----------
FEAT = [
    (YA_RATE, 'на Яндекс Картах', f'{YA_VOTES} {plural(YA_VOTES, "оценка", "оценки", "оценок")} двух филиалов, у обоих знак «Хорошее место 2026». В 2ГИС {GIS_RATE} по {GIS_VOTES} оценкам.'),
    ('12 000+', 'пациентов с 2018 года', 'Семейная клиника: лечим взрослых и детей, многие приходят всей семьёй.'),
    ('24:00', 'принимаем до полуночи', 'Октябрьская, 202: с понедельника по субботу до 24:00, в воскресенье до 20:00.'),
    ('11', 'врачей в команде', 'Терапевты, хирурги и имплантолог, ортопеды и ортодонт.'),
    ('2', 'филиала в Ставрополе', 'Октябрьская, 202 и Л. Толстого, 121Б. Осмотр и консультация бесплатно.'),    ('2025', 'премия ПроДокторов', 'У обоих филиалов отметка «Победитель премии 2025». На Октябрьской 5,0 по 492 отзывам.'),
]
feat = ''.join(f'<article class="fcard"><div class="fcard__body"><b class="fcard__big">{a}</b><h3>{b}</h3><p>{c}</p></div></article>' for a, b, c in FEAT)
FOIL = f'''<section class="foil on-dark" id="path" aria-labelledby="ph-title">
  <div class="foil__bg"></div>
  <div class="feat"><div class="feat__pin"><div class="feat__track">
    <div class="fcard fcard--intro"><span class="label">Почему нам доверяют</span><h2 id="ph-title" data-split>Лидерство, которое можно проверить</h2><p>Только то, что видно в открытых источниках и на приёме.</p></div>
    {feat}
  </div><div class="wrap cta-strip"><p>Осмотр и консультация бесплатно. Ни к чему не обязывает.</p><a class="btn btn--light btn--lg" href="zapis" data-modal="book" data-magnet>Записаться на бесплатную консультацию</a></div></div></div>
</section>'''
block('<section class="foil on-dark"', '</section>', FOIL)

# ---------- УСЛУГИ ----------
SV = [
    ('implantaciya', 'Имплантация и «Всё на 4»', '50% 62%'),
    ('lechenie-zubov', 'Лечение зубов и лазер', ''),
    ('ortodontiya', 'Брекеты и элайнеры', ''),
    ('protezirovanie', 'Коронки и протезы', ''),
    ('detskaya', 'Детская стоматология', ''),
]
cards = ''.join(f'''
    <a class="svl-card" href="zapis" data-modal="book" style="--delay:{i * .3:.1f}s">
      {img(f"images/uslugi/{k}.webp", "", "svl-card__img", ("object-position:" + pos) if pos else "")}
      <span class="svl-card__in"><span class="svl-card__top"><span class="svl-go" aria-hidden="true">{ARROW}</span></span><h3 class="svl-card__title">{t}</h3></span>
    </a>''' for i, (k, t, pos) in enumerate(SV))
ROWS = ['Профессиональная гигиена и отбеливание', 'Удаление зубов, в том числе мудрости', 'Компьютерная томография', 'Лечение дёсен и плазмолифтинг']
rows = ''.join(f'\n    <a class="svl-row" href="zapis" data-modal="book" style="--delay:{i * .3:.1f}s"><h3 class="svl-row__title">{t}</h3><span class="svl-row__act"><span class="svl-go" aria-hidden="true">{ARROW}</span></span></a>' for i, t in enumerate(ROWS))
SERV = f'''<section class="section section--sage svs" id="services" aria-labelledby="sv-title">
<div class="svl">
  <div class="svl__head"><div class="wrap"><h2 id="sv-title" data-split>Услуги</h2><span class="svl__links"><a class="link" href="zapis" data-modal="book">Записаться</a></span></div></div>
  <div class="svl__top"><div class="wrap"><div class="svl-grid" data-svl>{cards}
  </div></div></div>
  <div class="svl__bottom"><div class="wrap"><div class="svl-list" data-svl>{rows}
  </div><div class="svl__more"><a class="btn btn--light btn--lg" href="zapis" data-modal="book">Записаться на консультацию</a></div></div></div>
</div>
</section>'''
block('<section class="section section--sage svs"', '</section>', SERV)

# ---------- АКЦИИ ----------
# Условия из раздела «Акции» lider-dent26.ru, без сумм (правило: на сайте нет цен)
PR = [
    (P['exam'][0], P['exam'][1], 'Бесплатно', 'Осмотр и консультация', 'Бесплатно', 'Врач осмотрит, ответит на вопросы и подскажет, с чего начать лечение', 'Записаться бесплатно', 'бесплатный осмотр'),
    ('images/gen/akcii-implant.webp', 'Имплант с коронкой и снимок КТ', 'Имплантация', 'Имплант под ключ', 'КТ включена', 'Установка импланта под ключ вместе с компьютерной томографией. Рассрочка до 12 месяцев', 'Записаться на консультацию', 'имплант под ключ'),
    ('images/gen/akcii-allon4.webp', 'Протез челюсти на четырёх имплантах', 'Все зубы', '«Всё на 4»', 'Зубы за день', 'Несъёмный протез всей челюсти на четырёх имплантах. Рассрочка до 12 месяцев', 'Узнать подробнее', 'всё на 4'),
    ('images/gen/akcii-combo.webp', 'Зеркало, наконечник и снимок КТ на столе врача', 'Комплекс', 'Супер-Комбо', 'Четыре в одном', 'Консультация, чистка зубов с лазерным фторированием, КТ и лечение одного кариеса', 'Записаться', 'супер-комбо'),
]
# Что входит в предложение: пациент видит, за что платит
INCL = [
    [('Осмотр врача', 'бесплатно'), ('Ответы на вопросы', 'бесплатно'), ('Рекомендации по лечению', 'бесплатно')],
    [('Компьютерная томография', 'входит'), ('Установка импланта', 'входит'), ('Рассрочка до 12 месяцев', 'есть')],
    [('Импланты и несъёмный протез', 'входит'), ('Протез в день операции', 'входит'), ('Рассрочка до 12 месяцев', 'есть')],
    [('Консультация', 'входит'), ('Чистка с лазерным фторированием', 'входит'), ('Компьютерная томография', 'входит'), ('Лечение одного кариеса', 'входит')],
]
pr = ''.join(f'''<article class="pr4-card" style="--i:{i}">
    <span class="pr4-card__pic">{img(p, alt)}</span>
    <div class="pr4-card__text">
      <span class="label pr-tag">{tag}</span>
      <h3 class="pr-title">{t}</h3>
      <p class="pr-price"><b>{price}</b></p>
      <p class="pr-gift">{gift}</p>
      <div class="au-incl"><p class="au-incl__t">Что входит</p><ul>{''.join(f'<li><span>{a}</span><i aria-hidden="true"></i><b>{b}</b></li>' for a, b in INCL[i])}</ul></div>
      <a class="btn btn--lg" href="zapis" data-modal="book" data-promo="{promo}">{btn}</a>
    </div>
  </article>''' for i, (p, alt, tag, t, price, gift, btn, promo) in enumerate(PR))
AL = [('Осмотр', 'Консультация врача в обоих филиалах', 'Бесплатно'), ('Рассрочка', 'До 12 месяцев, можно оплатить долями', 'Частями'),
      ('ДМС', 'Лечим по полисам страховых компаний', 'По полису'), ('Бонусы', 'Баллы за лечение в приложении UDS', 'UDS'),
      ('Подарочный сертификат', 'Здоровая улыбка в подарок близким', 'Подарок'), ('До полуночи', 'Октябрьская, 202, с понедельника по субботу', '24:00')]
alv = ''.join(f'<li data-reveal><span class="alv4__l"><span class="alv__t">{a}</span><span class="alv__d">{b}</span></span><i aria-hidden="true"></i><b class="alv__n">{c}</b></li>' for a, b, c in AL)
alp = ''.join(f'<li data-reveal><em class="pr-al__n">{c}</em><b>{a}</b><span>{b}</span></li>' for a, b, c in AL)
AKCII = f'''<section class="section pr on-dark" id="akcii" aria-labelledby="pr-title"><div class="wrap">
  <div class="section__head"><div><span class="label label--light">Акции</span><h2 id="pr-title" data-split>Выгодные условия для пациентов</h2></div><p>Назовите акцию, когда администратор перезвонит.</p></div>
  <div class="pr4">{pr}</div>
  <div class="alx"><div class="alx__desk"><div class="alv4"><h3 class="pr-al__title">Выгодно всегда</h3><ul class="alv4__list">{alv}</ul></div></div><div class="alx__phone"><div class="pr-al" id="alw" data-v="3"><h3 class="pr-al__title">Выгодно всегда</h3><ul class="pr-al__list">{alp}</ul></div></div></div>
</div></section>'''
block('<section class="section pr on-dark"', '</div></section>', AKCII)

# ---------- ВРАЧИ: много врачей, раскладка Lava Dental из базы (две колонки со сдвигом вниз) ----------
TABS = [('', 'Все врачи'), ('lechenie-zubov', 'Лечение зубов'), ('hirurgiya', 'Хирургия и импланты'), ('protezirovanie', 'Протезирование'), ('ortodontiya', 'Брекеты и элайнеры')]
def doc_card(d, col):
    full_name = f'{d["fam"]} {d["name"]} {d["otch"]}'
    role = d['role'] + (f' · {d["exp"]}' if d.get('exp') else '')
    return f'''<article class="doc" data-tags="{d["tags"]}" data-col="{col}">
  <div class="doc__photo" data-ph><span class="doc__initials" aria-hidden="true">{d["ini"]}</span>{img(doc_photo(d), full_name, extra='sizes="auto, (max-width: 760px) 80vw, 30vw"')}
    <a class="doc__cover" href="zapis?doctor={d["slug"]}" data-modal="book" data-doctor="{d["slug"]}" tabindex="-1" aria-hidden="true"></a>
    <a class="doc__go" href="zapis?doctor={d["slug"]}" data-modal="book" data-doctor="{d["slug"]}" aria-label="Записаться: {d["name"]} {d["fam"]}">{ARROW}</a></div>
  <h3><a href="zapis?doctor={d["slug"]}" data-modal="book" data-doctor="{d["slug"]}">{full_name}</a></h3>
  <p class="doc__role">{role}</p>
  <p class="doc__focus">{d["focus"]}</p>
  <a class="btn btn--ghost btn--sm doc__cta" href="zapis?doctor={d["slug"]}" data-modal="book" data-doctor="{d["slug"]}">Записаться к врачу</a>
</article>'''
tabs = ''.join(f'<button class="chip" type="button" role="tab" data-tab="{k}" aria-selected="{"true" if not k else "false"}">{t}</button>' for k, t in TABS)
TEAM = f'''<section class="section section--sage" id="team" aria-labelledby="tm-title"><div class="wrap">
  <div class="section__head"><div><span class="label">Врачи</span><h2 id="tm-title" data-split>Кто будет вас лечить</h2></div><p>Одиннадцать врачей в двух филиалах: терапевты, хирурги и имплантолог, ортопеды и ортодонт.</p></div>
  <div class="team__tabs chips" role="tablist" aria-label="Направления" data-tabs="team">{tabs}</div>
  <div class="team__grid team__grid--lava">{''.join(doc_card(d, "lr"[i % 2]) for i, d in enumerate(DOCS))}</div>
  <div class="team__more"><a class="btn btn--ghost" href="zapis" data-modal="book">Подобрать врача и записаться</a></div>
</div></section>'''
i = s.index('<section class="section section--sage" id="team"')
j = s.index('</div></section>', s.index('</article></div>', i)) + len('</div></section>')
s = s[:i] + TEAM + s[j:]

# ---------- ОТЗЫВЫ ----------
STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 2.5 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>'
# дословно с Яндекс Карт и 2ГИС: [текст, текст с выделением, длина, цитата для блока рейтинга, подпись]
R = json.load(open(os.path.join(ROOT, 'src/reviews.json'), encoding='utf-8'))
Q, QUOTE = R['rows'], R['quote']
def rvrow(items, d):
    one = ''.join(f'<figure class="rv{" rv--short" if k == "short" else ""}"><blockquote>{q}</blockquote></figure>' for q, _, k in items)
    hid = one.replace('<figure class="rv', '<figure aria-hidden="true" class="rv')
    return f'<div class="rv__row" data-dir="{d}">{one}{one}{hid}{hid}</div>'
tones = ['ink', 'green', 'sage', 'white']
TOTAL = YA_VOTES + GIS_VOTES
TOTAL_T = f'{TOTAL // 100 * 100:,}'.replace(',', ' ')
half = (len(Q) + 1) // 2
REV = f'''<section class="section reviews" id="reviews" aria-labelledby="rv-title">
  <div class="wrap section__head"><div><span class="label">Отзывы</span><h2 id="rv-title" data-split>Больше {TOTAL_T} оценок, и почти все на пятёрку</h2></div></div>
  <div class="wrap"><div class="rt" aria-label="Оценки клиники на площадках" data-reveal>
    <div class="rt-avg">
      <div class="rt-avg__num" data-count="{YA_RATE}">{YA_RATE}</div>
      <div class="rt-stars" role="img" aria-label="5 из 5">{STAR * 5}</div>
      <p class="rt-avg__cap">Оценка на Яндекс Картах по {YA_VOTES} оценкам двух филиалов</p>
    </div>
    <div class="rt-sites">
      <a class="rt-site" href="{YA}reviews/" target="_blank" rel="noopener" data-goal="reviews_yandex">
        <span class="rt-site__top"><span class="rt-mark rt-mark--ya"><img src="images/brand/yandex-maps.svg" alt="" loading="lazy" decoding="async"></span><span class="rt-site__val">{YA_RATE}{STAR}</span></span>
        <span><span class="rt-site__name">Яндекс Карты</span><span class="rt-site__count">{YA_VOTES} {plural(YA_VOTES, "оценка", "оценки", "оценок")}, {YA_REV} {plural(YA_REV, "отзыв", "отзыва", "отзывов")}</span></span>
        <span class="rt-site__link">Смотреть отзывы</span>
      </a><a class="rt-site" href="{GIS}/tab/reviews" target="_blank" rel="noopener" data-goal="reviews_2gis">
        <span class="rt-site__top"><span class="rt-mark rt-mark--2gis"><img src="images/brand/2gis.webp" alt="" loading="lazy" decoding="async"></span><span class="rt-site__val">{GIS_RATE}{STAR}</span></span>
        <span><span class="rt-site__name">2ГИС</span><span class="rt-site__count">{GIS_VOTES} {plural(GIS_VOTES, "оценка", "оценки", "оценок")}, {GIS_REV} {plural(GIS_REV, "отзыв", "отзыва", "отзывов")}</span></span>
        <span class="rt-site__link">Смотреть отзывы</span>
      </a>
    </div>
    <div class="rt-pd au-rt-quote">
      <div class="rt-pd__text">
        <p class="rt-pd__quote">{QUOTE[0]}</p>
        <a class="link rt-pd__link" href="{YA}reviews/" target="_blank" rel="noopener">{QUOTE[1]}</a>
      </div>
    </div>
  </div></div>
  <div class="rv__rows">
    {rvrow(Q[:half], -1)}{rvrow(Q[half:], 1)}
  </div>
  <div class="rvm rvm--stack">
    <div class="rvs" role="group" aria-label="Отзывы пациентов">
      {''.join(f'<figure class="rvs__card rvs__card--{k}" data-tone="{tones[n % len(tones)]}"><blockquote>{b}</blockquote></figure>' for n, (_, b, k) in enumerate(Q))}
    </div>
    <div class="rvs__bar"><p class="rvs__hint">Смахните отзыв, чтобы прочитать следующий</p><button class="btn btn--sm rvs__next" type="button">Следующий</button></div>
  </div>
</section>'''
block('<section class="section reviews"', '</section>', REV)

# ---------- FAQ ----------
FAQ = [
    ('Оплата', [
        ('Сколько стоит лечение?', 'Стоимость зависит от состояния зубов, поэтому мы не называем цену заочно. Врач осмотрит вас на бесплатной консультации и до начала лечения распишет план с ценой каждого этапа.'),
        ('Осмотр правда бесплатный?', 'Да. Осмотр и консультация врача бесплатные в обоих филиалах.'),
        ('Есть ли рассрочка?', 'Да: рассрочка до 12 месяцев, оплата долями и по карте рассрочки. Принимаем карты, наличные и оплату по QR-коду.')]),
    ('Лечение и боль', [
        ('Больно ли лечить зубы?', 'Перед лечением врач делает анестезию. В отзывах пациенты часто пишут, что лечение прошло без дискомфорта.'),
        ('Зачем лечить лазером?', 'Диодный лазер работает с дёснами и мягкими тканями, помогает обработать каналы при лечении пульпита и отбелить зубы. Врач скажет на приёме, подходит ли он в вашем случае.'),
        ('Болит зуб вечером. Куда идти?', 'На Октябрьскую, 202: с понедельника по субботу принимаем до 24:00. Позвоните, администратор запишет на ближайшее время.')]),
    ('Дети', [
        ('С какого возраста можно прийти?', 'С первых зубов. Первый визит начинается со знакомства с врачом и креслом.'),
        ('Ребёнок боится. Что делать?', 'Скажите об этом при записи. Врач не торопит, объясняет и договаривается с ребёнком.'),
        ('Нужно ли лечить молочные зубы?', 'Да. Кариес молочного зуба переходит на соседние и на зачаток постоянного.')]),
    ('Импланты и брекеты', [
        ('Что такое «Всё на 4»?', 'Несъёмный протез всей челюсти на четырёх имплантах. Подходит, когда зубов почти не осталось.'),
        ('Правда можно получить зубы за день?', 'Да, по протоколу «Всё на 4» несъёмный протез фиксируют вскоре после установки имплантов. Подходит ли он вам, хирург скажет после КТ.'),
        ('Что лучше: брекеты или элайнеры?', 'Зависит от прикуса и образа жизни. Ортодонт Наталья Николаевна Никонова осмотрит и предложит варианты.')]),
    ('Запись и визит', [
        ('Как вы работаете?', 'Октябрьская, 202: с понедельника по субботу с 9:00 до 24:00, в воскресенье до 20:00. Л. Толстого, 121Б: ежедневно с 9:00 до 20:00.'),
        ('Принимаете по ДМС?', 'Да, лечим по полисам ДМС. Название страховой уточните у администратора при записи.'),
        ('Можно написать в мессенджер?', 'Да: WhatsApp и Telegram. Ссылки внизу страницы.')]),
]
faq_html = ''
for gi, (g, qs) in enumerate(FAQ):
    qh = ''.join(f'<details class="faqq"{" open" if gi == 0 and qi == 0 else ""}><summary><span>{q}</span><i aria-hidden="true"></i></summary><div class="faqq__a"><p>{a}</p></div></details>' for qi, (q, a) in enumerate(qs))
    faq_html += f'<details class="faqt"{" open" if gi == 0 else ""} data-reveal><summary><h3>{g}</h3><i aria-hidden="true"></i></summary><div class="faqt__body"><div class="faqt__list">{qh}</div></div></details>'
FAQS = f'''<section class="section faqv" id="faq" aria-labelledby="fq-title"><div class="wrap">
  <h2 id="fq-title" class="section__title faqv__title" data-split>Прежде чем прийти, вам, возможно, захочется узнать больше.</h2>
  <div class="faqv__main">{faq_html}</div>
</div></section>'''
block('<section class="section faqv" id="faq"', '</div></section>', FAQS)

# ---------- КОНТАКТЫ: два филиала ----------
def place(b, i):
    return f'''<div class="place ld-place{" ld-place--alt" if i else ""}">
    <div class="place__map place__map--img" data-clip>{img("images/map/map.svg", f"Карта: стоматология «Лидер Дент», {b['addr']}", "place__img")}<span class="place__pin" aria-hidden="true">{b["name"]}</span><iframe title="Карта: стоматология «Лидер Дент», {b['addr']}" data-src="https://yandex.ru/map-widget/v1/org/lider_dent/{b['ya_id']}/" loading="lazy"></iframe><button class="place__unlock" type="button">Нажмите, чтобы двигать карту</button></div>
    <div class="place__info" data-reveal>
      <h3>{b["addr"].replace("ул. ", "")}</h3>
      <dl class="place__list">
        <div><dt>Адрес</dt><dd>г. Ставрополь, {b["addr"]},<br>{b["floor"]}</dd></div>
        <div><dt>Телефон</dt><dd><a href="tel:{b["tel"]}">{b["phone"]}</a></dd></div>
        <div><dt>Часы работы</dt><dd>{b["hours"]}<span class="place__status" data-ld-open='{json.dumps(b["hrs"])}'></span></dd></div>
        <div><dt>Удобства</dt><dd>{b["perks"]}</dd></div>
      </dl>
      <div class="place__btns"><a class="btn btn--sm" href="{b["route"]}" target="_blank" rel="noopener">Построить маршрут</a><a class="btn btn--ghost btn--sm" href="{b["gis"]}" target="_blank" rel="noopener">Маршрут в 2ГИС</a><a class="btn btn--ghost btn--sm" href="tel:{b["tel"]}">Позвонить</a></div>
      <button class="way__link place__share" type="button" data-share data-share-text="Стоматология «Лидер Дент»: Ставрополь, {b["addr"]}. {b["hours"]}. {b["phone"]}" data-share-url="{b["ya"]}">Отправить адрес</button>
    </div>
  </div>'''
CONT = f'''<section class="section ctum" id="contacts" aria-labelledby="ct-title"><div class="wrap">
  <div class="section__head"><div><span class="label">Контакты</span><h2 id="ct-title" data-split>Два адреса в Ставрополе</h2></div><p>Октябрьская, 202 принимает до полуночи с понедельника по субботу. На Л. Толстого, 121Б ждём ежедневно с 9:00 до 20:00. Обе клиники на втором этаже.</p></div>
  {''.join(place(b, i) for i, b in enumerate(BR))}
</div></section>'''
block('<section class="section ctum"', '</div></section>', CONT)
# статус «открыто» по часам каждого филиала (в app.js часы базы зашиты на 9:00-21:00)
OPEN_JS = '''<script>(function(){function now(){var p=new Intl.DateTimeFormat("ru-RU",{timeZone:"Europe/Moscow",weekday:"short",hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).formatToParts(new Date),g=function(t){return p.find(function(x){return x.type===t}).value};var w=["вс","пн","вт","ср","чт","пт","сб"].indexOf(g("weekday").replace(".","").toLowerCase());return{w:w,m:+g("hour")*60+ +g("minute")}}
function fmt(m){return m>=1440?"24:00":Math.floor(m/60)+":"+("0"+m%60).slice(-2)}
document.querySelectorAll("[data-ld-open]").forEach(function(el){try{var h=JSON.parse(el.getAttribute("data-ld-open")),n=now(),d=h[String(n.w)]||h.d;if(n.m>=d[0]&&n.m<d[1]){el.textContent="Сейчас открыто, до "+fmt(d[1]);el.classList.add("is-open")}else el.textContent=n.m<d[0]?"Сейчас закрыто, откроемся в "+fmt(d[0]):"Сейчас закрыто, откроемся завтра в 9:00"}catch(e){}})})();</script>'''

# ---------- ПОДВАЛ ----------
f0 = s.index('<footer'); f1 = s.index('</footer>') + len('</footer>')
foot = s[f0:f1]
foot = foot.replace('https://t.me/wtdent', TG)
foot = re.sub(r'<span class="footer__word">Вайтис</span>', '<span class="footer__word">Лидер Дент</span>', foot)
foot = re.sub(r'<div class="fstage__info".*?</div>\n  </div>\n  <div class="footer__legal">', lambda m: f'''<div class="fstage__info">
      <div class="fstage__group">
        <h3>Контакты</h3>
        <a class="fstage__big" href="tel:{BR[0]["tel"]}">{BR[0]["phone"]}</a>
        <a class="fstage__big" href="tel:{BR[1]["tel"]}">{BR[1]["phone"]}</a>
        <a class="fstage__big fstage__big--mail" href="mailto:{MAIL}">{MAIL}</a>
      </div>
      <div class="fstage__group">
        <h3>Адреса</h3>
        <p class="fstage__addr">г. Ставрополь, {BR[0]["addr"]}<br>г. Ставрополь, {BR[1]["addr"]}</p>
        <p class="fstage__links"><a href="{BR[0]["route"]}" target="_blank" rel="noopener">Маршрут на Октябрьскую</a><a href="{BR[1]["route"]}" target="_blank" rel="noopener">Маршрут на Л. Толстого</a></p>
      </div>
      <div class="fstage__group">
        <h3>Часы работы</h3>
        <p class="fstage__text">Октябрьская: {BR[0]["hours"]}<br>Л. Толстого: {BR[1]["hours"].lower()}</p>
      </div>
      <nav class="fstage__group" aria-label="Услуги">
        <h3>Услуги</h3>
        <p class="fstage__list fstage__list--1">{''.join(f'<a href="#services">{t}</a>' for _, t, _ in SV)}{''.join(f'<a href="#services">{t}</a>' for t in ROWS[:2])}<a href="#akcii">Акции</a></p>
      </nav>
      <nav class="fstage__group" aria-label="Клиника">
        <h3>Клиника</h3>
        <p class="fstage__list fstage__list--2"><a href="#clinic">О клинике</a><a href="#akcii">Акции</a><a href="#team">Врачи</a><a href="#reviews">Отзывы</a><a href="#faq">Вопросы</a><a href="#contacts">Контакты</a></p>
      </nav>
      <div class="fstage__group">
        <h3>Пациентам</h3>
        <p class="fstage__list fstage__list--2">
          <a href="zapis" data-modal="book">Бесплатный осмотр</a>
          <a href="#faq">Рассрочка и ДМС</a>
          <a href="#akcii">Подарочные сертификаты</a>
        </p>
      </div>
      <div class="fstage__group">
        <h3>На связи</h3>
        <p class="fstage__list fstage__list--2">
          <a href="{WA}" target="_blank" rel="noopener">WhatsApp</a>
          <a href="{TG}" target="_blank" rel="noopener">Telegram</a>
          <a href="{VK}" target="_blank" rel="noopener">ВКонтакте</a>
          <a href="{OK}" target="_blank" rel="noopener">Одноклассники</a>
        </p>
      </div>
    </div>
  </div>
  <div class="footer__legal">''', foot, flags=re.S)
foot = re.sub(r'<span>© 2026 ООО «ВАЙТИС».*?</span>', f'<span>© 2026 {BR[0]["ent"]}, {BR[0]["lic"]}, г. Ставрополь, {BR[0]["addr"]}. {BR[1]["ent"]}, {BR[1]["lic"]}, г. Ставрополь, {BR[1]["addr"]}.</span>', foot, flags=re.S)
foot = re.sub(r'<span class="footer__docs">.*?</span>', '<span class="footer__docs"><a href="#">Политика конфиденциальности</a><a href="#">Согласие на обработку персональных данных</a><a href="#" data-cookie-settings>Настройки cookie</a></span>', foot, flags=re.S)
s = s[:f0] + foot + s[f1:]

# ---------- модалки и хвост ----------
s = re.sub(r'<script type="application/json" id="um-docs">.*?</script>',
           '<script type="application/json" id="um-docs">' + json.dumps({d['slug']: f'{d["name"]} {d["fam"]}' for d in DOCS}, ensure_ascii=False) + '</script>', s, flags=re.S)
s = s.replace('https://t.me/wtdent', TG).replace('https://wa.me/79037977688', WA)
s = s.replace('https://max.ru/+79661723378', WA)
s = s.replace('Консультация по All-on-4</h2><p class="modal__sub">Хирург, ортопед и терапевт осмотрят вас вместе, сделаем КТ.', 'Консультация по «Всё на 4»</h2><p class="modal__sub">Хирург-имплантолог осмотрит вас, сделаем КТ и составим план.')
# ссылки на внутренние страницы Вайтис ведут на якоря главной
s = re.sub(r'href="(privacy|soglasie|soglashenie|svedeniya|gosudarstvennye-garantii)/[^"]*"', 'href="#"', s)
s = re.sub(r'href="(uslugi|implantaciya|lechenie-zubov|detskaya|ortodontiya|protezirovanie|gigiena|estetika|hirurgiya|diagnostika)/"', 'href="#services"', s)
s = s.replace('href="ceny/"', 'href="#services"').replace('href="vrachi/"', 'href="#team"')
s = s.replace('action="spasibo/"', 'action="#"')
s = re.sub(r'стоматология в\W*Одинцово', 'стоматология в Ставрополе', s)
s = s.replace('Хирург, ортопед и терапевт осмотрят вас вместе, сделаем КТ.', 'Хирург-имплантолог осмотрит вас, сделаем КТ и составим план.')
inv = ''.join(f'<li><span class="invite__pic" data-ph><span class="doc__initials" aria-hidden="true">{d["ini"]}</span>{img(doc_photo(d), d["name"] + " " + d["fam"])}</span><b>{d["short"]}</b><span>{d["name"]}<br>{d["fam"]}</span></li>' for d in FACES)
s = re.sub(r'<ul class="invite__docs">.*?</ul>', '<ul class="invite__docs">' + inv + '</ul>', s, flags=re.S)
s = re.sub(r'\+7\W903\W797-76-88', PHONE, s)
s = s.replace('images/brand/header-logo-light.svg', 'images/brand/header-logo.svg')
s = s.replace('Вайтис', 'Лидер Дент').replace('White Teeth', 'Лидер Дент')

# ---------- демо-переключатель палитры (убрать после выбора Ильи) ----------
VPANEL = """<div class="au-vp" role="group" aria-label="Варианты оформления (демо)"><b>Палитра</b>
<span class="au-vp__g" data-t="pal"><button data-v="1">1</button><button data-v="2">2</button></span></div>
<script>(function(){var K="ld-v-";function set(t,v){var el=document.documentElement;el.setAttribute("data-"+t,v);document.querySelectorAll('.au-vp__g[data-t="'+t+'"] button').forEach(function(b){b.classList.toggle("on",b.getAttribute("data-v")==v)});try{localStorage.setItem(K+t,v)}catch(e){}if(window.__ld3d)window.__ld3d()}
document.querySelectorAll(".au-vp__g").forEach(function(g){var t=g.getAttribute("data-t"),v="1";try{v=localStorage.getItem(K+t)||"1"}catch(e){}set(t,v);g.addEventListener("click",function(e){var b=e.target.closest("button");if(b)set(t,b.getAttribute("data-v"))})})})();</script>
"""
s = s.replace('</body>', OPEN_JS + VPANEL + '</body>', 1)
# свои стили встраиваем в страницу: на один блокирующий запрос меньше
s = s.replace('<link rel="stylesheet" href="assets/lider-dent.css?v=ld1">', '<style>' + re.sub(r'/\*.*?\*/', '', open(os.path.join(ROOT, 'assets/lider-dent.css'), encoding='utf-8').read().replace('\n', '')) + '</style>')
s = re.sub(r'href="zapis(\?doctor=\w+)?"', 'href="#contacts"', s)
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(s)
left = [w for w in ['Одинцов', 'Одинбург', 'Северная', 'Гвиниашвили', 'Чилингарян', 'Казарян', 'wtdent', '79037977688', 'Академи', 'Рязан', 'Лазарев', 'Попова', 'Герасимов', 'academy_smile', 'akademiya'] if w in s]
print('OK', len(s), 'leftovers:', left)
