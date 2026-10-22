"""Карточки темпа продаж (Инструкция п. 9). Данные pf_data.json (после mk_pf3.py)."""
import json,html as _h
_all=[e for e in json.load(open('pf_data.json')) if e['sold_p']>0 and 'не трогать' not in e['name'] and e['id']!='58']

def _tempo(e):
    if e['since_last'] is not None and e['since_last']>=6: return 'l'
    if e['pw7']>=10:
        r=e['w7']/e['pw7']; return 'h' if r>=1.3 else ('l' if r<0.5 else 'm')
    if e['w7']>=10: return 'h'
    return 'l' if e['w7']==0 else 'm'
_f=lambda x:f"{x:,.0f}".replace(',',' ')
_mln=lambda v:'—' if v<=0 else f"{v/1e6:.2f}".replace('.',',')
CD=sorted(_all,key=lambda e:('hml'.index(_tempo(e)),e['start']))
TN={k:sum(1 for e in CD if _tempo(e)==k) for k in 'hml'}
CARDS='<style>.kk3{grid-template-columns:repeat(3,1fr)!important}.kk4{grid-template-columns:repeat(4,1fr)!important}.kk3 .c,.kk4 .c{padding:8px 12px}.lgd{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0 8px;font-size:12px;color:#c7c2d6}.lgd i{font-style:normal;font-size:10px;padding:3px 10px;border-radius:5px;color:#fff;font-weight:600}.cg{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:10px}.cd{border-radius:10px;padding:9px 11px;color:#fff;line-height:1.3}.cd b{font-size:14px;display:block;color:#fff}.cd .s{font-size:10px;opacity:.9;margin:2px 0 6px}.cd.h{background:#1f7a52}.cd.m{background:#c98a00}.cd.l{background:#9b2226}.cr{display:grid;grid-template-columns:62px 1fr 38px;align-items:baseline;margin:3px 0}.cr span{font-size:10px;opacity:.85}.cr em{display:inline;font-style:normal;color:#fff;font-weight:700;font-variant-numeric:tabular-nums;font-size:14px}.cr i{font-style:normal;text-align:right;font-weight:700}.cv{font-size:9.5px;opacity:.85;margin-top:6px}@media(max-width:700px){.kk3,.kk4{grid-template-columns:1fr 1fr!important}.cg{grid-template-columns:1fr}}</style>'
CARDS+='<div class=lgd>ТЕМП ПРОДАЖ: 7 ДНЕЙ К ПРЕДЫДУЩИМ 7 <i style="background:#1f7a52">Высокий ≥1,3×</i><i style="background:#c98a00">Средний 0,5–1,3×</i><i style="background:#9b2226">Низкий &lt;0,5× / стоит / 0 за 7 дн.</i></div><div class=cg>'
for e in CD:
    nm=e['name']
    for a_,b_ in SHORT: nm=nm.replace(a_,b_)
    pt=100*e['sold_p']/e['plan_t'] if e['plan_t'] else 0; pr=(100*e['rev']/e['plan_r']) if e['plan_r'] else None
    CARDS+=f"""<div class="cd {_tempo(e)}"><b>{_h.escape(nm)}</b><div class=s>{e['start'][8:10]}.{e['start'][5:7]}.{e['start'][:4]} — {e['days_left']} дн. до · Сред. в день за 7 дн. — {e['w7']/7:.0f} шт. · За 3 дня +{e['d3']} шт.</div><div class=cr><span>билеты/шт</span><em>{_f(e['sold_p'])}/{_f(e['plan_t'])}</em><i>{pt:.0f}%</i></div><div class=cr><span>рубли/млн</span><em>{_mln(e['rev'])}/{_mln(e['plan_r'])}</em><i>{('%.0f%%'%pr) if pr is not None else '—'}</i></div><div class=cv>Витрины: {', '.join(e['vit'])}</div></div>"""
CARDS+='</div>'
