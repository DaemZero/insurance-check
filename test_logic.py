#!/usr/bin/env python3
"""index.html 안의 스크립트를 DOM 스텁 위에서 실행해 계산·표시 로직을 검증한다."""
import json, pathlib, re, sys
import dukpy

ROOT = pathlib.Path(__file__).resolve().parent
html = (ROOT / "index.html").read_text(encoding="utf-8")
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
assert scripts, "no script found"
code = scripts[-1]

PRELUDE = r"""
var __els = {};
function El(id){
  this.id = id; this.value = ""; this.textContent = ""; this.innerHTML = "";
  this.className = ""; this.style = {}; this.firstChild = null; this.childs = [];
  this._lis = {};
  this.classList = { add: function(){}, remove: function(){} };
  this.setAttribute = function(k,v){ this[k]=v; };
  this.getAttribute = function(k){ return this[k]; };
  var self = this;
  Object.defineProperty(this, "firstChild", { get: function(){ return self.childs.length ? self.childs[0] : null; } });
  this.appendChild = function(c){ this.childs.push(c); };
  this.removeChild = function(c){ var i = this.childs.indexOf(c); if (i >= 0) this.childs.splice(i,1); };
  this.addEventListener = function(t,fn){ (this._lis[t]=this._lis[t]||[]).push(fn); };
  this.focus = function(){};
  this.scrollIntoView = function(){};
  this.fire = function(t){ (this._lis[t]||[]).forEach(function(f){ f.call(this); }, this); };
}
var __ids = ["income","fixed","variable","saving","premium","resultCard","basisText",
  "statusBox","deficitWarn","deficitWarnText","statusKicker","statusAmount","statusDesc","tOutflow","tRemain","tRatio",
  "donut","donutPct","legend","barBand","barMarker","barMarkerLabel","compareNote",
  "strip","stripLabel","sMonth","sYear","sDecade","basisChip","rateMin","rateMax",
  "rateMinVal","rateMaxVal","memo","clientName","saveState","toast","printHead","printMemo",
  "memoCard","printHint","printHintText","printHintClose",
  "resetBtn","clearMemoBtn","printBtn"];
__ids.forEach(function(id){ __els[id] = new El(id); });
__els.rateMin.value = "7"; __els.rateMax.value = "10";
var __chips = [];
["350,110,60,50,13","450,150,80,60,48","380,120,70,30,32"].forEach(function(p){
  var c = new El("chip");
  c["data-p"] = p;
  c.getAttribute = function(k){ return this[k]; };
  __chips.push(c);
});
var document = {
  getElementById: function(id){ return __els[id]; },
  createElementNS: function(ns, tag){ var e = new El(tag); e.tag = tag; return e; },
  createElement: function(tag){ return new El(tag); },
  querySelectorAll: function(sel){ return __chips; },
  addEventListener: function(){}
};
var localStorage = {
  _d: {},
  getItem: function(k){ return this._d[k] === undefined ? null : this._d[k]; },
  setItem: function(k,v){ this._d[k] = String(v); },
  removeItem: function(k){ delete this._d[k]; }
};
var window = { print: function(){ __printed = (__printed||0)+1; },
  addEventListener: function(){}, _h: {} };
var __printed = 0;
var confirm = function(){ return true; };
var setTimeout = function(fn,ms){ return 1; };
var clearTimeout = function(){};
var navigator = { userAgent: "__UA__", clipboard: { writeText: function(){ return { then: function(){} }; } } };
"""

CHECK = r"""
(function(){
  var out = [];
  function snap(tag){
    out.push({
      tag: tag,
      status: __els.statusKicker.textContent + " | " + __els.statusAmount.textContent,
      desc: __els.statusDesc.textContent,
      cls: __els.statusBox.className,
      outflow: __els.tOutflow.textContent,
      remain: __els.tRemain.textContent,
      ratio: __els.tRatio.textContent,
      donut: __els.donutPct.textContent,
      legend: __els.legend.innerHTML,
      segments: __els.donut.childs.length,
      marker: __els.barMarker.style.left + " " + __els.barMarkerLabel.textContent,
      band: __els.barBand.style.left + " +" + __els.barBand.style.width,
      note: __els.compareNote.innerHTML,
      warn: (__els.deficitWarn.hidden ? "hidden" : "SHOWN") + " " + __els.deficitWarnText.innerHTML,
      strip: __els.stripLabel.textContent + " | " + __els.sMonth.textContent + " | " + __els.sYear.textContent + " | " + __els.sDecade.textContent,
      basis: __els.basisText.textContent
    });
  }
  function set(vals){
    ["income","fixed","variable","saving","premium"].forEach(function(k,i){
      __els[k].value = String(vals[i]); __els[k].fire("input");
    });
  }
  snap("initial(empty)");
  set([350,110,60,50,13]); snap("preset1");
  set([450,150,80,60,48]); snap("preset2");
  set([380,120,70,30,32]); snap("preset3");
  set([300,120,60,30,0]);  snap("no-premium");
  set([300,150,80,60,30]); snap("deficit");
  set([0,100,50,0,20]);    snap("no-income");
  set([1000,100,50,50,150]); snap("big-income");
  set([250,100,50,20,45]); snap("edge-20pct-band");
  __els.rateMin.value = "5"; __els.rateMin.fire("input");
  __els.rateMax.value = "13"; __els.rateMax.fire("input");
  set([350,110,60,50,13]); snap("custom-rate 5-13%");
  __els.resetBtn.fire("click"); snap("reset");
  __els.memo.value = "테스트 메모"; __els.memo.fire("input");
  __els.printBtn.fire("click");
  out.push({tag:"print-count", printed: __printed, saved: localStorage.getItem("daemin_consult_memo_v1")});
  return JSON.stringify(out);
})()
"""

js = PRELUDE + code + "\n" + CHECK
res = dukpy.evaljs(js)
for row in json.loads(res):
    print(json.dumps(row, ensure_ascii=False, indent=None))
    print()

# ---- 인앱 브라우저(카톡 웹뷰)에서 인쇄 버튼을 누르면 안내가 즉시 뜨는지 ----
INAPP_UA = "Mozilla/5.0 (Linux; Android 13; SM-S918N Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.0.0 Mobile Safari/537.36 KAKAOTALK 10.4.3"
INAPP_CHECK = r"""
(function(){
  __els.printHint.hidden = true;
  __els.income.value = "350"; __els.income.fire("input");
  __els.printBtn.fire("click");
  return JSON.stringify([{
    tag: "inapp-print",
    ua_matched: true,
    hint_hidden: !!__els.printHint.hidden,
    hint_text: __els.printHintText.innerHTML.replace(/\s+/g, " ").trim(),
    toast: __els.toast.textContent,
    printed: __printed,
    memo_saved: localStorage.getItem("daemin_consult_memo_v1") !== null
  }]);
})()
"""
js2 = PRELUDE.replace("__UA__", INAPP_UA) + code + "\n" + INAPP_CHECK
for row in json.loads(dukpy.evaljs(js2)):
    print(json.dumps(row, ensure_ascii=False, indent=None))
    print()

# 일반 브라우저(안드로이드 크롬)에서는 안내 없이 인쇄만 호출되는지
NORMAL_UA = "Mozilla/5.0 (Linux; Android 13; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
NORMAL_CHECK = r"""
(function(){
  __els.printHint.hidden = true;
  __els.income.value = "350"; __els.income.fire("input");
  __els.printBtn.fire("click");
  return JSON.stringify([{
    tag: "chrome-android-print",
    hint_hidden: !!__els.printHint.hidden,
    printed: __printed
  }]);
})()
"""
js3 = PRELUDE.replace("__UA__", NORMAL_UA) + code + "\n" + NORMAL_CHECK
for row in json.loads(dukpy.evaljs(js3)):
    print(json.dumps(row, ensure_ascii=False, indent=None))
    print()
