import html
exec(open('mk_html.py').read())
off=[e for e in D if e['st']=='Не открыто']; D2=[e for e in D if e['st']!='Не открыто']
order={'Стоит':0,'Замедление':1,'Внимание':2,'Нет продаж':3}
prob=sorted([e for e in D2 if e['st'] in order],key=lambda e:(order[e['st']],e['days_left']))
SH=8
