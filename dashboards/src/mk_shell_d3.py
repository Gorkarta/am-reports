"""Оболочка «Анализ продажи билетов» (Д3): интерфейс из мастер-копии, данные — events.json с GitHub.

  python3 -s mk_shell_d3.py <events.json> <мастер «Анализ продажи билетов».html> <выходной.html> [BASE_URL]

Запускается из папки src (нужен shell_common.py). В файл встроен последний снимок данных на случай, если GitHub недоступен.
"""
import sys, json, re
from shell_common import STATUS_CSS, loader, js_safe

EV_JSON, MASTER, OUT = sys.argv[1:4]
BASE = sys.argv[4] if len(sys.argv) > 4 else 'https://raw.githubusercontent.com/Gorkarta/am-reports/main/dashboards/data/'


def rep(text, old, new, n=1):
    assert text.count(old) == n, f'фрагмент встречается {text.count(old)} раз, ожидалось {n}: ' + old[:70]
    return text.replace(old, new)


h = open(MASTER, encoding='utf-8').read()
emb = json.load(open(EV_JSON, encoding='utf-8'))

h = rep(h, '</style>', STATUS_CSS + '</style>')
h = rep(h, '</p>\n    </div>\n  </header>', '</p>\n      <div id="dstat" class="ds"></div>\n    </div>\n  </header>')

# данные: вместо вшитого массива — параметр функции
a = h.index('const DATA = ')
b = h.index('const FILTERS')
h = h[:a] + 'const DATA = payload.events;\n' + h[b:]
h = rep(h, '<script>\n', '<script>\nfunction startD3(payload){\n')
last = h.rindex('</script>')
h = h[:last] + '}\n</script>\n<script>' + loader(BASE) + '\nvar EMB=' + js_safe(json.dumps(emb, ensure_ascii=False, separators=(',', ':'))) + ';\n' \
    "function prep(d){d.events.forEach(function(e){e.venue_name=AMEsc(e.venue_name);e.hall_name=AMEsc(e.hall_name);" \
    "Object.keys(e.breakdowns).forEach(function(k){var b=e.breakdowns[k];b.zones.forEach(function(r){r.name=AMEsc(r.name)});b.channels.forEach(function(r){r.name=AMEsc(r.name)})})});return d}\n" \
    "AMLoad({file:'events.json',embedded:EMB,cur:function(d){return d.export_cur},render:function(d){startD3(prep(d))}});\n</script>" + h[last + len('</script>'):]

# тексты: определения по правилам обработки выгрузок БС v1.5
h = rep(h, 'Временная ось — по дате оплаты заказа (orders.sold_at).', 'Временная ось — по дате оформления билета.')
h = rep(h, '<li><b>Возвраты</b> — билет аннулирован, и по его заказу есть денежный возврат (платёж типа refund). Статус заказа не учитывается: после полного возврата он становится −5. Отметки refunded_at до августа 2026 — артефакт БС, возвратом не считаются.</li>',
        '<li><b>Возвраты</b> — билет аннулирован, а его заказ был оплачен (orders.sold_at заполнено).</li>')
h = rep(h, '<li><b>Сгоревшие брони</b> — билет аннулирован, и по его заказу нет платежа refund.</li>',
        '<li><b>Сгоревшие брони</b> — билет аннулирован, а его заказ так и не был оплачен.</li>')
h = rep(h, 'Билет аннулирован, и по заказу есть платёж refund (статус заказа не важен). refunded_at до августа 2026 — артефакт БС.',
        'Билет аннулирован, а его заказ был оплачен (orders.sold_at заполнено).')
h = rep(h, 'Билет аннулирован, и по его заказу нет платежа refund.', 'Билет аннулирован, а его заказ не был оплачен.')
h = rep(h, 'заказ оплачен (orders.status 10 или 15).', 'заказ оплачен (orders.sold_at заполнено).', 2)
h = rep(h, 'Данные: выгрузка билетной системы (csv_export). Продано/возврат/сгоревшая бронь определяются по статусу заказа (<code>orders.status</code>) и, для возвратов, по платежу типа <code>refund</code>; тестовые мероприятия и служебные покупатели исключены (см. «Правила обработки выгрузок БС»). Статический снимок на 03.10.2026, без подключения к базе.',
        'Данные: выгрузка билетной системы (GitHub), обновляется ежедневно после 09:00 МСК. Продано/возврат/сгоревшая бронь определяются по оплате заказа (<code>orders.sold_at</code>); тестовые мероприятия и служебные покупатели исключены (см. «Правила обработки выгрузок БС» v1.5).')
h = h.replace('неоплаченных заказов (orders.status = 0)', 'неоплаченных заказов (orders.sold_at пусто)')
open(OUT, 'w', encoding='utf-8').write(h)
print('ok', len(h))
