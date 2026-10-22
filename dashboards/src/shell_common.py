"""Общий загрузчик данных для дашбордов Аренамастер Бизнес-аналитика, которые берут расчёт с GitHub.

Схема: ежедневный расчёт (GitHub Actions в bs-reports) кладёт готовые агрегаты в
Gorkarta/am-reports/dashboards/data/ (meta.json, pf_page.json, channels.json). Дашборд при открытии
запрашивает свой файл; если связи нет — показывает встроенный снимок (последний при сборке дашборда).
Выгрузка БС появляется около 09:00 МСК; расчёт занимает несколько минут.
"""

STATUS_CSS = (
    ".ds{display:flex;align-items:center;gap:8px;margin:8px 0 4px;font:12px/1.35 Inter,Arial,sans-serif;color:#c7c2d6}"
    ".ds i{flex:none;width:8px;height:8px;border-radius:50%;background:#a29cb3}"
    ".ds.ds-ok i{background:#34d399}.ds.ds-wait i{background:#ffcf5c;animation:dsp 1.4s ease-in-out infinite}.ds.ds-err i{background:#ff5470}"
    "@keyframes dsp{50%{opacity:.35}}"
)

LOADER_JS = r"""
(function(){
'use strict';
var BASE=__BASE__;
var EXPECT_H=9, STALE_H=12, POLL_MS=120000;   /* выгрузка ~09:00 МСК; после 12:00 считаем, что её нет */
function mskNow(){return new Date(Date.now()+10800000)}
function fmtD(s){return s.slice(8,10)+'.'+s.slice(5,7)+'.'+s.slice(0,4)}
function fmtDT(s){return fmtD(s)+' '+s.slice(11,16)}
function expectedDay(){var n=mskNow();if(n.getUTCHours()<EXPECT_H)n=new Date(n.getTime()-86400000);return n.toISOString().slice(0,10)}
function getJSON(name,ms){
  var c=new AbortController(),id=setTimeout(function(){c.abort()},ms||12000);
  return fetch(BASE+name+'?t='+Date.now(),{cache:'no-store',signal:c.signal}).then(function(r){
    clearTimeout(id);if(!r.ok)throw new Error('HTTP '+r.status);return r.json()});
}
/* Данные приходят из публичного репозитория: HTML-фрагменты чистим от скриптов и обработчиков событий. */
window.AMSan=function(h){
  var t=document.createElement('template');t.innerHTML=String(h||'');
  t.content.querySelectorAll('script,iframe,object,embed,link,meta,base,form').forEach(function(n){n.remove()});
  t.content.querySelectorAll('*').forEach(function(n){
    Array.prototype.slice.call(n.attributes).forEach(function(a){
      var v=(a.value||'').trim().toLowerCase();
      if(/^on/i.test(a.name)||((a.name==='href'||a.name==='src'||a.name==='xlink:href')&&/^(javascript|data):/.test(v)))n.removeAttribute(a.name);
    });
  });
  var d=document.createElement('div');d.appendChild(t.content);return d.innerHTML;
};
window.AMEsc=function(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')};
window.AMLoad=function(o){
  var el=document.getElementById('dstat'),shown=null,offline=false;
  function paint(k,t){if(!el)return;el.className='ds '+k;el.innerHTML='<i></i><span></span>';el.lastChild.textContent=t}
  function evaluate(){
    if(!shown)return;
    var cur=o.cur(shown),exp=expectedDay();
    if(offline){paint('ds-err','Нет связи с источником данных. Показан сохранённый снимок: выгрузка БС от '+fmtDT(cur)+' МСК');return}
    if(cur.slice(0,10)>=exp){paint('ds-ok','Данные актуальны: выгрузка БС от '+fmtDT(cur)+' МСК');return}
    if(mskNow().getUTCHours()<STALE_H)paint('ds-wait','Идёт обновление: выгрузка за '+fmtD(exp)+' ещё обрабатывается. Пока показаны данные от '+fmtDT(cur)+' МСК');
    else paint('ds-err','Новой выгрузки за '+fmtD(exp)+' нет. Показаны данные от '+fmtDT(cur)+' МСК');
  }
  function poll(){
    getJSON('meta.json',8000).then(function(m){
      var v=m&&m.files&&m.files[o.file];if(v&&shown&&(offline||v!==o.cur(shown)))location.reload();
    }).catch(function(){}).then(evaluate);
  }
  getJSON(o.file).then(function(d){shown=d;o.render(d);evaluate()},function(){
    offline=true;shown=o.embedded;o.render(o.embedded);evaluate();
  }).then(function(){setInterval(poll,POLL_MS)});
};
})();
"""


def js_safe(obj_json: str) -> str:
    """JSON → безопасно для вставки в <script> (без закрывающих тегов и U+2028/2029)."""
    return obj_json.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def loader(base: str) -> str:
    import json
    return LOADER_JS.replace('__BASE__', json.dumps(base))
