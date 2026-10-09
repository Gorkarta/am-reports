n_=lambda x:f"{int(round(x)):,}".replace(',',' ')
def pct1(x):return (f"{x*100:.1f}").replace('.',',')+'%'
def dev(x):
    r=round(abs(x)*100)
    if r==0:return '<span class=sub>0%</span>'
    return f"<span class={'bad' if x<0 else 'good'}><b>{'−' if x<0 else '+'}{r}%</b></span>"
def mlnp(v,dec=1,keep=False):
    s=f"{v/1e6:.{dec}f}".replace('.',',')
    if s.endswith(',0') and not keep:s=s[:-2]
    return s+' млн ₽'
def cards(real,PN,rev,PR,MINT,MINR,GT,GR,sub_t,sub_r=''):
    t=(f"<div class=k><div class=l>Реализовано билетов</div><div class=v>{n_(real)}</div><div class=s>{dev(real/PN-1)} от <nobr>план‑прогноза {n_(PN)}</nobr><br>"
       f"<b>{pct1(real/MINT)}</b> от <nobr>минплана {n_(MINT)}</nobr><br><b>{pct1(real/GT)}</b> от <nobr>цели {n_(GT)}</nobr><br><span class=sub>{sub_t}</span></div></div>")
    r=(f"<div class=k><div class=l>Выручка</div><div class=v>{(f'{rev/1e6:.2f}').replace('.',',')} млн ₽</div><div class=s>{dev(rev/PR-1)} от <nobr>план‑прогноза {mlnp(PR)}</nobr><br>"
       f"<b>{pct1(rev/MINR)}</b> от <nobr>минплана {mlnp(MINR)}</nobr><br><b>{pct1(rev/GR)}</b> от <nobr>цели {mlnp(GR)}</nobr>{('<br><span class=sub>'+sub_r+'</span>') if sub_r else ''}</div></div>")
    return t,r
def path(real,rev,MINT,MINR,GT,GR):
    mk=lambda m,g:f"{m/g*100:.1f}"
    def bar(v,g,m):return f"<div class=pbw><div class=pbm><i style='width:{min(v/g*100,100):.1f}%'></i><b class=mk style='left:{mk(m,g)}%'></b></div></div>"
    return (f"<div class=card style='margin-top:8px'><div class=t>Путь к цели</div><div class=pgm>"
     f"<div class=h></div><div class=h>Факт</div><div class=h>Минимум</div><div class=h>Цель</div>"
     f"<div class=lb>Выручка</div><div class=n>{(f'{rev/1e6:.2f}').replace('.',',')} млн ₽</div><div class=n>{mlnp(MINR)}<small>{pct1(rev/MINR)}</small></div><div class=n>{mlnp(GR)}<small>{pct1(rev/GR)}</small></div>"
     f"{bar(rev,GR,MINR)}"
     f"<div class=lb>Билеты</div><div class=n>{n_(real)}</div><div class=n>{n_(MINT)}<small>{pct1(real/MINT)}</small></div><div class=n>{n_(GT)}<small>{pct1(real/GT)}</small></div>"
     f"{bar(real,GT,MINT)}</div>"
     f"<div class=rest>До минимума осталось: <b>{mlnp(max(MINR-rev,0),keep=True)}</b> · <b>{n_(max(MINT-real,0))} {'билет' if (MINT-real)%10==1 and (MINT-real)%100!=11 else ('билета' if 2<=(MINT-real)%10<=4 and not 12<=(MINT-real)%100<=14 else 'билетов')}</b></div>"
     f"<div class=sub style='margin-top:6px'>зелёная метка — план-минимум; полоса — до расчётной цели; % — доля выполнения</div></div>")
CSS="""<style>.pgm{display:grid;grid-template-columns:62px 1fr 1fr 1fr;column-gap:8px;align-items:start}
.pgm .h{color:#a29cb3;font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;padding-bottom:4px}
.pgm .lb{color:#c7c2d6;font-size:12px;padding:8px 0 0;border-top:1px solid #2a2635}
.pgm .n{font-weight:700;font-size:13.5px;padding:7px 0 0;border-top:1px solid #2a2635;white-space:nowrap}.pgm .n small{display:block;color:#a29cb3;font-weight:400;font-size:10.5px;margin-top:2px}
.pgm .pbw{grid-column:2/5;padding:2px 0 8px}.pbm{position:relative;height:10px;background:#2a2635;border-radius:5px;margin-top:6px}.pbm i{display:block;height:100%;background:#ffb238;border-radius:5px}
.pbm .mk{position:absolute;top:-4px;width:2px;height:18px;background:#34d399}.rest{color:#c7c2d6;font-size:12px;margin-top:6px}.rest b{color:#f5f3fa}
.k .s b.bad{color:#ff5470}</style>"""
