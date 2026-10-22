#!/usr/bin/env python3
"""Ежедневная сборка данных дашбордов Аренамастер Бизнес-аналитика по выгрузке БС.

Запускается GitHub Actions в репозитории bs-reports (см. dashboards/README.md). Читает две выгрузки (cur — свежая,
prev — прошлая; плоские папки CSV), считает данные дашбордов и кладёт их в <am>/dashboards/data/ (+ архив по дате).
Коммит и push делает workflow.

  python3 -s build_all.py --src dashboards/src --cur data/cur --prev data/prev \
      --cur-time '2026-10-22 09:00' --prev-time '2026-10-21 09:00' --am am-reports

Время выгрузок — МСК, из коммитов bs-reports. Код выхода: 0 — всё собрано; 2 — «Портфель» остановлен проверкой
подозрительных мероприятий (нужен ответ владельца в exclusions.json), остальное собрано; 1 — ошибка.
Персональные данные (tickets.data, individuals, payments) скрипты не читают и в результат не попадают.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, datetime

ap = argparse.ArgumentParser()
ap.add_argument('--src', required=True)
ap.add_argument('--cur', required=True)
ap.add_argument('--prev', required=True)
ap.add_argument('--cur-time', required=True)
ap.add_argument('--prev-time', required=True)
ap.add_argument('--am', required=True)
a = ap.parse_args()

cur_dir, prev_dir = os.path.abspath(a.cur), os.path.abspath(a.prev)
am = os.path.abspath(a.am)
data_dir = os.path.join(am, 'dashboards', 'data')
os.makedirs(data_dir, exist_ok=True)
day = a.cur_time[:10]
ddmmyyyy = f'{day[8:10]}.{day[5:7]}.{day[:4]}'
work = tempfile.mkdtemp(prefix='dash_')
src = os.path.join(work, 'src')
shutil.copytree(a.src, src, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
os.symlink(cur_dir, os.path.join(src, 'cur'))
os.symlink(prev_dir, os.path.join(src, 'prev'))
env = dict(os.environ, PYTHONPATH='.')


def run(*args):
    r = subprocess.run([sys.executable, '-s', *args], cwd=src, env=env, capture_output=True, text=True)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


built = {}
status = 0

# ---- Портфель мероприятий (Д9) ----
code, log = run('mk_pf.py', a.cur_time, a.prev_time)
print(log[-1500:])
if code == 2:
    status = 2
    with open(os.path.join(data_dir, 'blocked.json'), 'w', encoding='utf-8') as f:
        json.dump({'export_cur': a.cur_time, 'dashboard': 'pf_page.json', 'message': log[-3000:]}, f, ensure_ascii=False, indent=1)
    print('СТОП: «Портфель» не построен — подозрительные мероприятия, нужен ответ владельца (exclusions.json).')
elif code != 0:
    sys.exit('mk_pf.py завершился с ошибкой:\n' + log[-3000:])
else:
    for step in (('mk_pf3.py',), ('mk_page.py', os.path.join(work, 'pf_page.json'))):
        c, l = run(*step)
        if c != 0:
            sys.exit(f'{step[0]} завершился с ошибкой:\n' + l[-3000:])
    shutil.copy(os.path.join(work, 'pf_page.json'), os.path.join(data_dir, 'pf_page.json'))
    built['pf_page.json'] = a.cur_time
    blocked = os.path.join(data_dir, 'blocked.json')
    if os.path.exists(blocked):
        os.remove(blocked)

# ---- Каналы продаж (Д4) ----
ch_out = os.path.join(work, 'channels.json')
c, l = run('build_channels.py', cur_dir, ch_out, ddmmyyyy)
print(l[-1200:])
if c != 0:
    sys.exit('build_channels.py завершился с ошибкой:\n' + l[-3000:])
d = json.load(open(ch_out, encoding='utf-8'))
d['export_cur'] = a.cur_time
json.dump(d, open(os.path.join(data_dir, 'channels.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
built['channels.json'] = a.cur_time

# ---- Анализ продажи билетов (Д3) ----
ev_out = os.path.join(work, 'events.json')
c, l = run('build_events.py', cur_dir, ev_out, a.cur_time)
print(l[-1200:])
if c != 0:
    sys.exit('build_events.py завершился с ошибкой:\n' + l[-3000:])
shutil.copy(ev_out, os.path.join(data_dir, 'events.json'))
built['events.json'] = a.cur_time

# ---- meta.json и архив по дате ----
meta_path = os.path.join(data_dir, 'meta.json')
meta = json.load(open(meta_path, encoding='utf-8')) if os.path.exists(meta_path) else {}
files = meta.get('files', {})
files.update(built)
msk_now = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
meta = {'updated': msk_now, 'export_cur': a.cur_time, 'export_prev': a.prev_time, 'files': files}
json.dump(meta, open(meta_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
arch = os.path.join(am, 'dashboards', 'archive', f'{day[8:10]}{day[5:7]}{day[:4]}')
os.makedirs(arch, exist_ok=True)
for name in list(built) + ['meta.json']:
    shutil.copy(os.path.join(data_dir, name), os.path.join(arch, name))
print('Собрано:', built, '| обновлено', msk_now, 'МСК | выгрузка', a.cur_time)
shutil.rmtree(work, ignore_errors=True)
sys.exit(status)
