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
  "sendCard","sendName","sendContact","sendConsent","sendBtn","sendStatus","sendStatusText",
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
/* --- 동기 thenable 스텁(fetch) --- */
function __promise(v, isErr, e){
  var p = {
    then: function(f){
      if (isErr) return p;
      var r; try { r = f(v); } catch (x) { return __promise(null, true, x); }
      return (r && typeof r.then === "function") ? r : __promise(r, false, null);
    },
    "catch": function(f){
      if (!isErr) return p;
      var r; try { r = f(e); } catch (x) { return __promise(null, true, x); }
      return (r && typeof r.then === "function") ? r : __promise(r, false, null);
    }
  };
  return p;
}
var __lastFetch = null;
var __fetchMode = "ok";
var fetch = function(url, opts){
  __lastFetch = { url: url, opts: opts };
  if (__fetchMode === "fail") return __promise(null, true, { message: "network" });
  var body = __fetchMode === "false"
    ? '{"success":"false","message":"테스트 실패 강제"}'
    : '{"success":"true","message":"전송되었습니다"}';
  var resp = { ok: true, status: 200, text: function(){ return __promise(body, false, null); } };
  return __promise(resp, false, null);
};
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

# ---- 진단 결과 보내기: 필수값 검증 → 전송 payload → 성공/실패 표시 ----
SEND_CHECK = r"""
(function(){
  var out = [];
  function st(){
    return {
      hidden: !!__els.sendStatus.hidden,
      cls: __els.sendStatus.className,
      text: (__els.sendStatusText.innerHTML || "").replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim()
    };
  }
  __els.sendName.value = "테스트 고객";
  __els.sendContact.value = "010-0000-0000";
  __els.sendConsent.checked = true;

  __els.sendBtn.fire("click");
  out.push({tag: "send-no-income", called: !!__lastFetch, status: st()});

  __els.income.value = "450"; __els.income.fire("input");
  __els.sendName.value = "";
  __els.sendBtn.fire("click");
  out.push({tag: "send-no-name", called: !!__lastFetch, status: st()});

  __els.sendName.value = "테스트 고객"; __els.sendContact.value = "   ";
  __els.sendBtn.fire("click");
  out.push({tag: "send-no-contact", called: !!__lastFetch, status: st()});

  __els.sendContact.value = "123";
  __els.sendBtn.fire("click");
  out.push({tag: "send-short-contact", called: !!__lastFetch, status: st()});

  __els.sendContact.value = "010-0000-0000"; __els.sendConsent.checked = false;
  __els.sendBtn.fire("click");
  out.push({tag: "send-no-consent", called: !!__lastFetch, status: st()});

  __els.sendConsent.checked = true;
  __els.memo.value = "5세대 실손 전환 상담 요청";
  __els.fixed.value = "150"; __els.variable.value = "80";
  __els.saving.value = "60"; __els.premium.value = "48";
  __els.sendBtn.fire("click");
  var payload = null;
  if (__lastFetch){ try { payload = JSON.parse(__lastFetch.opts.body); } catch (e) {} }
  out.push({
    tag: "send-valid",
    url: __lastFetch && __lastFetch.url,
    method: __lastFetch && __lastFetch.opts.method,
    ctype: __lastFetch && __lastFetch.opts.headers["Content-Type"],
    keys: payload ? Object.keys(payload) : null,
    payload: payload,
    status: st()
  });

  __fetchMode = "false";
  __els.sendBtn.fire("click");
  out.push({tag: "send-server-refused", status: st(), disabled: !!__els.sendBtn.disabled});

  __fetchMode = "fail";
  __els.sendBtn.fire("click");
  out.push({tag: "send-network-fail", status: st(), disabled: !!__els.sendBtn.disabled});

  return JSON.stringify(out);
})()
"""
js4 = PRELUDE.replace("__UA__", NORMAL_UA) + code + "\n" + SEND_CHECK
for row in json.loads(dukpy.evaljs(js4)):
    print(json.dumps(row, ensure_ascii=False, indent=None))
    print()
