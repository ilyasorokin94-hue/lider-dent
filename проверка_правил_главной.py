# Проверка собранной главной на правила проекта «Сайты - Тест».
# Ищет в видимом тексте, alt, title, aria-label, мета-тегах и JSON-LD:
#   длинное и среднее тире, нумерацию «01 / 02», цены, служебные пометки,
#   остатки текстов шаблона и прошлой клиники.
#
# Запуск из корня репозитория клиники:
#   python3 -I проверка_правил_главной.py index.html --prev "Академия улыбки,Рязан,Лазарев,Попова"
# --prev: слова прошлой клиники через запятую (часть слова тоже годится: «Рязан» найдёт «Рязани»).
# --allow-prices: не считать цены ошибкой (если Илья для этой клиники цены разрешил).
# --final: перед показом клиенту пометки «уточнить» и «согласовать» становятся ошибками.
# Код выхода 1, если есть ошибки.
import argparse, html, json, re, sys
from html.parser import HTMLParser

TEMPLATE_WORDS = ['Вайтис', 'Одинцов', 'White Teeth', 'wtdent', 'Lava', 'Умная медицина', 'Смартмед']
# Нельзя \b и \w: они не видят кириллицу. Границы слов пишем через [а-яё].
# U+2012..U+2015: цифровое, среднее, длинное тире и горизонтальная черта (через chr, чтобы в файле не было самих знаков)
DASH = re.compile('[' + ''.join(map(chr, range(0x2012, 0x2016))) + ']')
# дефис перед цифрами: хвост телефона вроде 22-26-02, это не нумерация
NUMBERING = re.compile(r'(?<![\d.,:-])0[1-9](?![\d.,:])\s*(/|из|\||$)|Шаг\s+\d+\s+из\s+\d+', re.I | re.M)
PRICE = re.compile(r'₽|(?<![а-яё])руб(лей|ля|ль|\.)?(?![а-яё])|(?<![а-яё])тыс\.?\s*(₽|руб)|\d\s?000\s?(₽|р\.)', re.I)
MARKS = re.compile(r'уточнить|уточняем|согласовать|TODO|FIXME|lorem|\[[А-ЯA-Z_]{3,}\]', re.I)


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self.ld = [], 0, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
            self.ld = tag == 'script' and a.get('type') == 'application/ld+json'
        for k in ('alt', 'title', 'aria-label', 'placeholder'):
            if a.get(k):
                self.parts.append((f'{tag}[{k}]', a[k]))
        if tag == 'meta' and a.get('content') and (a.get('name') in ('description',) or (a.get('property') or '').startswith('og:')):
            self.parts.append((f'meta {a.get("name") or a.get("property")}', a['content']))

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1
            self.ld = False

    def handle_data(self, data):
        if self.ld:
            try:
                self.parts.append(('JSON-LD', json.dumps(json.loads(data), ensure_ascii=False)))
            except ValueError:
                self.parts.append(('JSON-LD', data))
        elif not self.skip and data.strip():
            self.parts.append(('текст', data.strip()))


def ctx(s, m, w=40):
    a, b = max(0, m.start() - w), min(len(s), m.end() + w)
    return ('…' if a else '') + s[a:b].replace('\n', ' ') + ('…' if b < len(s) else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?', default='index.html')
    ap.add_argument('--prev', default='', help='слова прошлой клиники через запятую')
    ap.add_argument('--allow-prices', action='store_true')
    ap.add_argument('--final', action='store_true')
    o = ap.parse_args()
    src = open(o.file, encoding='utf-8').read()
    p = Text(); p.feed(src)
    title = re.search(r'<title>(.*?)</title>', src, re.S)
    if title:
        p.parts.append(('title', html.unescape(title.group(1))))

    words = TEMPLATE_WORDS + [w.strip() for w in o.prev.split(',') if w.strip()]
    rules = [
        ('ОШИБКА', 'длинное или среднее тире', DASH),
        ('ОШИБКА', 'нумерация «01 / 02» или «Шаг N из M»', NUMBERING),
        ('ВНИМАНИЕ' if o.allow_prices else 'ОШИБКА', 'цена на странице', PRICE),
        ('ОШИБКА' if o.final else 'ВНИМАНИЕ', 'служебная пометка', MARKS),
    ]
    if words:
        rules.append(('ОШИБКА', 'остаток шаблона или прошлой клиники', re.compile('|'.join(re.escape(w) for w in words), re.I)))

    errors = 0
    for level, name, rx in rules:
        hits = [(where, ctx(t, m)) for where, t in p.parts for m in rx.finditer(t)]
        if not hits:
            print(f'ok       {name}: 0')
            continue
        if level == 'ОШИБКА':
            errors += len(hits)
        print(f'{level.lower():9}{name}: {len(hits)}')
        seen = set()
        for where, c in hits:
            if (where, c) in seen:
                continue
            seen.add((where, c))
            print(f'          [{where}] {c}')
    print('\nИтого ошибок:', errors)
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
