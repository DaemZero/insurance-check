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
var __all = [];
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
function __match(el, sel){
  var parts = sel.match(/[.#][A-Za-z0-9_-]+|\[[^\]]+\]/g) || [];
  if (!parts.length) return false;
  for (var i = 0; i < parts.length; i++){
    var p = parts[i];
    if (p.charAt(0) === "."){
      var cls = p.slice(1);
      if ((" " + (el.className || "") + " ").indexOf(" " + cls + " ") < 0) return false;
    } else if (p.charAt(0) === "#"){
      if (el.id !== p.slice(1)) return false;
    } else {
      var inner = p.slice(1, -1), eq = inner.indexOf("=");
      if (eq < 0){ if (el[inner] === undefined) return false; }
      else {
        var name = inner.slice(0, eq);
        var want = inner.slice(eq + 1).replace(/^["']|["']$/g, "");
        if (String(el[name]) !== want) return false;
      }
    }
  }
  return true;
}
var __ids = ["income","fixed","variable","saving","premium","resultCard","basisText",
  "statusBox","deficitWarn","deficitWarnText","statusKicker","statusAmount","statusDesc","tOutflow","tRemain","tRatio",
  "donut","donutPct","legend","barBand","barMarker","barMarkerLabel","compareNote",
  "strip","stripLabel","sMonth","sYear","sDecade","basisChip","clientName","questions","toast","printHead","printMemo",
  "memoCard","insChips","insPrint","timePrint","methodPrint","questionsPrint","hourSel","sendCard",
  "printHint","printHintText","printHintClose",
  "sendName","sendContact","sendConsent","sendBtn","sendStatus","sendStatusText",
  "resetBtn","clearMemoBtn","printBtn"];
__ids.forEach(function(id){ var e = new El(id); __els[id] = e; __all.push(e); });
__els.hourSel.disabled = true;
function __mk(id, cls, attrs){
  var e = new El(id); e.className = cls;
  for (var k in attrs){ if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]); }
  __all.push(e);
  return e;
}
__els.merAM = __mk("merAM", "opt", {"data-mer": "오전"});
__els.merPM = __mk("merPM", "opt", {"data-mer": "오후"});
__els.min00 = __mk("min00", "opt", {"data-min": "00"});
__els.min30 = __mk("min30", "opt", {"data-min": "30"});
__els.mCall = __mk("mCall", "opt", {"data-method": "전화"});
__els.mSms = __mk("mSms", "opt", {"data-method": "문자"});
var document = {
  getElementById: function(id){ return __els[id] || null; },
  createElementNS: function(ns, tag){ var e = new El(tag); e.tag = tag; return e; },
  createElement: function(tag){ var e = new El(tag); e.tag = tag; return e; },
  querySelectorAll: function(sel){ return __all.filter(function(e){ return __match(e, sel); }); },
  addEventListener: function(){}
};
var localStorage = {
  _d: {},
  getItem: function(k){ return this._d[k] === undefined ? null : this._d[k]; },
  setItem: function(k,v){ this._d[k] = String(v); },
  removeItem: function(k){ delete this._d[k]; }
};
/*__PRELOAD__*/
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

  /* 적정 비율 기준은 7~12% 고정 — 기준을 바꾸는 UI가 없다 */
  out.push({tag: "fixed-basis",
    basis: __els.basisText.textContent, chip: __els.basisChip.textContent,
    band: __els.barBand.style.left + " +" + __els.barBand.style.width,
    rateControls: document.querySelectorAll("#rateMin, #rateMax").length});
  set([350,110,60,50,13]); snap("fixed-basis-sample");

  /* ---- 상담 정보 안내 문구/버튼 이름 ---- */
  out.push({tag: "memo-ui",
    saveState: !!__els.saveState,
    clearBtn: "(html에서 확인)",
    printed: __printed});

  /* ---- 03 상담 정보: 상담보험 다중 선택 ---- */
  var insChips = __els.insChips.childs;
  function pressIns(label){
    for (var i = 0; i < insChips.length; i++){
      if (insChips[i].getAttribute("data-ins") === label){ insChips[i].fire("click"); return insChips[i]; }
    }
    return null;
  }
  out.push({tag: "ins-chip-order", count: insChips.length,
    labels: insChips.map(function(b){ return b.textContent; }),
    dataIns: insChips.map(function(b){ return b.getAttribute("data-ins"); })});
  var c1 = pressIns("암보험");
  var c2 = pressIns("보장점검");
  var c3 = pressIns("치매보험");
  out.push({tag: "ins-select-3",
    pressed: [c1.getAttribute("aria-pressed"), c2.getAttribute("aria-pressed"), c3.getAttribute("aria-pressed")],
    cls: [c1.className, c2.className, c3.className],
    print: __els.insPrint.textContent,
    stored: localStorage.getItem("daemin_consult_insurance_v1")});
  pressIns("보장점검"); /* 다시 누르면 해제 */
  out.push({tag: "ins-toggle-off", print: __els.insPrint.textContent,
    stored: localStorage.getItem("daemin_consult_insurance_v1")});

  /* ---- 실손의료비보험 · 태아보험 · 운전자보험 · 화재보험 (새로 든 4종) ---- */
  var cMedi = pressIns("실손의료비보험");
  var cTae = pressIns("태아보험");
  var cDriver = pressIns("운전자보험");
  var cFire = pressIns("화재보험");
  out.push({tag: "ins-new-4",
    found: [!!cMedi, !!cTae, !!cDriver, !!cFire],
    pressed: [cMedi && cMedi.getAttribute("aria-pressed"), cTae && cTae.getAttribute("aria-pressed"),
              cDriver && cDriver.getAttribute("aria-pressed"), cFire && cFire.getAttribute("aria-pressed")],
    cls: [cMedi && cMedi.className, cTae && cTae.className, cDriver && cDriver.className, cFire && cFire.className],
    print: __els.insPrint.textContent,
    stored: localStorage.getItem("daemin_consult_insurance_v1")});
  pressIns("실손의료비보험"); pressIns("태아보험"); pressIns("운전자보험"); pressIns("화재보험");
  out.push({tag: "ins-new-4-toggle-off", print: __els.insPrint.textContent,
    stored: localStorage.getItem("daemin_consult_insurance_v1")});
  pressIns("암보험"); pressIns("실손의료비보험");

  /* ---- 궁금하신 사항 ---- */
  __els.questions.value = "5세대 실손 전환 조건과 보장 공백이 궁금합니다";
  __els.questions.fire("input");
  __els.printBtn.fire("click"); /* 입력 후 400ms 디바운스 저장 → 인쇄 버튼이 즉시 저장 */
  out.push({tag: "questions-saved", stored: localStorage.getItem("daemin_consult_questions_v1"),
    print: __els.questionsPrint.textContent, printed: __printed});

  /* ---- 연락가능시간: 오전/오후 → 시 → 00/30분 ---- */
  out.push({tag: "hour-disabled-before-meridiem", disabled: __els.hourSel.disabled});
  __els.merPM.fire("click");
  __els.hourSel.value = "3"; __els.hourSel.fire("change");
  __els.min30.fire("click");
  out.push({tag: "time-afternoon-3-30",
    mer: __els.merPM.getAttribute("aria-pressed"), hour: __els.hourSel.value,
    minute: __els.min30.getAttribute("aria-pressed"), disabled: __els.hourSel.disabled,
    print: __els.timePrint.textContent,
    stored: localStorage.getItem("daemin_consult_time_v1")});
  __els.merAM.fire("click");
  out.push({tag: "time-switch-morning-resets",
    hour: __els.hourSel.value, minute: __els.min00.getAttribute("aria-pressed"),
    print: __els.timePrint.textContent});
  __els.merAM.fire("click"); /* 토글 해제 */
  out.push({tag: "meridiem-off-clears-time", print: __els.timePrint.textContent,
    disabled: __els.hourSel.disabled, stored: localStorage.getItem("daemin_consult_time_v1")});
  __els.merPM.fire("click");
  __els.hourSel.value = "7"; __els.hourSel.fire("change");
  __els.min00.fire("click");

  /* ---- 연락방법 ---- */
  __els.mCall.fire("click");
  out.push({tag: "method-call", print: __els.methodPrint.textContent,
    pressed: __els.mCall.getAttribute("aria-pressed"),
    stored: localStorage.getItem("daemin_consult_method_v1")});
  __els.mSms.fire("click");
  out.push({tag: "method-switch-sms", print: __els.methodPrint.textContent,
    callPressed: __els.mCall.getAttribute("aria-pressed")});

  /* ---- 성함 ↔ 04번 양방향 연동 ---- */
  __els.clientName.value = "김상담";
  __els.clientName.fire("input");
  out.push({tag: "name-to-sendcard", sendName: __els.sendName.value,
    stored: localStorage.getItem("daemin_consult_client_v1")});
  __els.sendName.value = "이전송";
  __els.sendName.fire("input");
  out.push({tag: "name-from-sendcard", clientName: __els.clientName.value,
    stored: localStorage.getItem("daemin_consult_client_v1")});
  __els.clientName.value = "김상담"; __els.clientName.fire("input");

  __els.resetBtn.fire("click"); snap("reset");
  __els.printBtn.fire("click");
  out.push({tag: "print-count", printed: __printed,
    saved_name: localStorage.getItem("daemin_consult_client_v1"),
    saved_ins: localStorage.getItem("daemin_consult_insurance_v1")});

  /* ---- 내용 초기화 ---- */
  __els.clearMemoBtn.fire("click");
  out.push({tag: "clear-consult",
    name: __els.clientName.value, sendName: __els.sendName.value,
    questions: __els.questions.value, ins: __els.insPrint.textContent,
    time: __els.timePrint.textContent, method: __els.methodPrint.textContent,
    stored: [localStorage.getItem("daemin_consult_client_v1"),
             localStorage.getItem("daemin_consult_insurance_v1"),
             localStorage.getItem("daemin_consult_questions_v1"),
             localStorage.getItem("daemin_consult_time_v1"),
             localStorage.getItem("daemin_consult_method_v1")]});
  return JSON.stringify(out);
})()
"""

EXPECT_INS = ["종합보험", "실손의료비보험", "암보험", "뇌/심장보험", "수술비보험", "상해보험",
              "간병보험", "태아보험", "운전자보험", "화재보험", "치매보험", "치아보험",
              "펫보험", "종신보험", "연금보험", "보장점검", "기타"]

js = PRELUDE + code + "\n" + CHECK
res = dukpy.evaljs(js)
rows = json.loads(res)
for row in rows:
    print(json.dumps(row, ensure_ascii=False, indent=None))
    print()

# ---- 적정 비율 기준은 7~12% 고정 ----
_fixed = [r for r in rows if r["tag"] == "fixed-basis"][0]
assert _fixed["basis"] == "적정 보험료 = 월 소득의 7~12%", "기준 문구가 7~12%가 아닙니다: %s" % _fixed["basis"]
assert _fixed["chip"] == "7% ~ 12%", "기준 배지가 7%~12%가 아닙니다: %s" % _fixed["chip"]
assert _fixed["band"] == "35% +25%", "차트 기준띠가 7~12%(35%%~60%%)가 아닙니다: %s" % _fixed["band"]
assert _fixed["rateControls"] == 0, "적정 비율 기준을 바꾸는 컨트롤이 남아 있습니다"
_sample = [r for r in rows if r["tag"] == "fixed-basis-sample"][0]
assert "7% ~ 12%" in _sample["note"], "결과 문구의 기준이 7~12%가 아닙니다: " + _sample["note"]
assert "7% ~ 12%" in _sample["note"], _sample["note"]
print(json.dumps({"tag": "fixed-basis-7-12", "ok": True, "basis": _fixed["basis"],
                  "band": _fixed["band"]}, ensure_ascii=False))
print()

# ---- 상담보험 17종: 유저가 지정한 정확한 순서·라벨인지 ----
_order = [r for r in rows if r["tag"] == "ins-chip-order"][0]
assert _order["count"] == 17, "상담보험 칩이 17종이 아닙니다: %d종" % _order["count"]
assert _order["labels"] == EXPECT_INS, "상담보험 순서·라벨이 다릅니다:\n%s" % _order["labels"]
assert _order["dataIns"] == EXPECT_INS, "data-ins 값이 다릅니다: %s" % _order["dataIns"]
assert len(set(EXPECT_INS)) == 17, "기대 목록에 중복이 있습니다"
_new = [r for r in rows if r["tag"] == "ins-new-4"][0]
assert _new["found"] == [True, True, True, True], "새 4종 칩을 찾지 못했습니다: %s" % _new["found"]
assert _new["pressed"] == ["true", "true", "true", "true"], "새 4종 칩이 선택되지 않았습니다: %s" % _new["pressed"]
assert "치매재가보험" not in _order["labels"], "예전 라벨(치매재가보험)이 남아 있습니다"
print(json.dumps({"tag": "ins-17-order", "ok": True, "labels": EXPECT_INS}, ensure_ascii=False))
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
    consult_saved: localStorage.getItem("daemin_consult_client_v1") !== null
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

# ---- 저장값 복원(localStorage에 남아 있던 상담 정보가 화면에 돌아오는지) ----
PRELOAD = (
    'localStorage._d["daemin_consult_client_v1"]="박복원";'
    'localStorage._d["daemin_consult_insurance_v1"]="[\\"암보험\\",\\"보장점검\\"]";'
    'localStorage._d["daemin_consult_questions_v1"]="실손 청구 방법";'
    'localStorage._d["daemin_consult_time_v1"]="{\\"mer\\":\\"오후\\",\\"hour\\":\\"3\\",\\"minute\\":\\"30\\"}";'
    'localStorage._d["daemin_consult_method_v1"]="문자";'
)
RESTORE_CHECK = r"""
(function(){
  return JSON.stringify([{
    tag: "restore",
    clientName: __els.clientName.value,
    sendName: __els.sendName.value,
    questions: __els.questions.value,
    insPrint: __els.insPrint.textContent,
    questionsPrint: __els.questionsPrint.textContent,
    insPressed: __els.insChips.childs.filter(function(b){ return b.getAttribute("aria-pressed") === "true"; })
      .map(function(b){ return b.textContent; }),
    hour: __els.hourSel.value,
    hourDisabled: !!__els.hourSel.disabled,
    timePrint: __els.timePrint.textContent,
    methodPrint: __els.methodPrint.textContent
  }]);
})()
"""
js5 = PRELUDE.replace("__UA__", NORMAL_UA).replace("/*__PRELOAD__*/", PRELOAD) + code + "\n" + RESTORE_CHECK
for row in json.loads(dukpy.evaljs(js5)):
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
  __els.fixed.value = "150"; __els.variable.value = "80";
  __els.saving.value = "60"; __els.premium.value = "48";
  __els.questions.value = "5세대 실손 전환 상담 요청";
  for (var i = 0; i < __els.insChips.childs.length; i++){
    var lab = __els.insChips.childs[i].textContent;
    if (lab === "암보험" || lab === "보장점검" || lab === "실손의료비보험") __els.insChips.childs[i].fire("click");
  }
  __els.merPM.fire("click");
  __els.hourSel.value = "3"; __els.hourSel.fire("change");
  __els.min30.fire("click");
  __els.mSms.fire("click");

  __els.sendBtn.fire("click");
  var payload = null;
  if (__lastFetch){ try { payload = JSON.parse(__lastFetch.opts.body); } catch (e) {} }
  out.push({
    tag: "send-valid",
    url: __lastFetch && __lastFetch.url,
    method: __lastFetch && __lastFetch.opts.method,
    ctype: __lastFetch && __lastFetch.opts.headers["Content-Type"],
    keys: payload ? Object.keys(payload) : null,
    consult: payload ? {
      "상담보험": payload["상담보험"],
      "궁금하신 사항": payload["궁금하신 사항"],
      "연락가능시간": payload["연락가능시간"],
      "연락방법": payload["연락방법"]
    } : null,
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

# ---- HTML 자체 검사: 예시 프리셋·기준·문구·03번 필드·전송 필드명 ----
tpl = (ROOT / "index.template.html").read_text(encoding="utf-8")
assert 'data-p=' not in html, "01번 예시 프리셋 버튼이 남아 있습니다"
assert "30대 직장인" not in html and "60대" not in html, "예시 문구가 화면에 남아 있습니다"
for gone in ("불러옴", "이 브라우저에만", "상담 정보 지우기",
             "고객 성함", "가입보다 이해가"):
    assert gone not in tpl, "지우기로 한 문구가 남아 있습니다: %s" % gone
assert '<div class="eyebrow">1분 보험료 건강검진</div>' not in tpl, "히어로 배지 문구가 남아 있습니다"
assert "1분 보험료 건강검진" not in html.split("<body>")[1].split("<script>")[0], \
    "본문(히어로)에 '1분 보험료 건강검진' 문구가 남아 있습니다"
assert "적정 보험료 = 월 소득의 7~12%" in tpl, "02번 기준 문구가 7~12%가 아닙니다"
assert 'id="rateMin"' not in html and 'id="rateMax"' not in html, "적정 비율 기준 조절 UI가 남아 있습니다"
assert '<b id="basisChip">7% ~ 12%</b>' in tpl, "적정 비율 기준 배지가 7% ~ 12%가 아닙니다"
assert "saveState" not in html, "저장 상태 안내 배지가 남아 있습니다"
assert 'id="clearMemoBtn">내용 초기화<' in html, "03번 버튼이 '내용 초기화'가 아닙니다"
assert '<span class="f-label">성함 <em>필수' in html, "04번 라벨이 '성함'이 아닙니다"
assert 'id="resetBtn"' in html, "01번 입력값 초기화 버튼이 없습니다"
assert '[1분 보험료 건강검진]' in code, "FormSubmit 메일 제목 접두어가 사라졌습니다"
assert "1분 보험료 건강검진 결과" not in code, "인쇄 1쪽 머리말에 지우기로 한 문구가 남아 있습니다"
assert "class=\"eyebrow\"" not in html, "히어로 배지(eyebrow)가 남아 있습니다"
sentences = [
    "어려운 보험 약관은 알기 쉽게 풀어드리고, 객관적인 비교분석으로 합리적인 기준을 제시하겠습니다.",
    "과장된 권유 대신 투명한 기준과 정직한 설명으로 꼭 맞는 보장만을 안내합니다.",
    "예기치 못한 위기 앞에서도 소중한 일상이 무너지지 않도록 끝까지 곁을 지키겠습니다.",
]
for s in sentences:
    assert s in html, "명함 문구 누락 또는 오타: %s" % s
    assert s in tpl, "명함 문구 누락 또는 오타(template): %s" % s
assert 'id="clientName"' in html and '<label class="f-label" for="clientName">성함</label>' in html, \
    "03번 성함 칸(라벨 '성함')이 없습니다"
assert 'placeholder="자유롭게 기재해주세요"' in html, "궁금하신 사항 placeholder가 없습니다"
for label in EXPECT_INS:
    assert '"%s"' % label in code, "상담보험 항목 누락: %s" % label

# 상담보험 17종: 유저가 지정한 순서 그대로, 기타는 마지막, 치매재가보험은 없음
_ins = re.search(r'var INSURANCES = \[(.*?)\];', code, re.S)
assert _ins, "INSURANCES 배열을 찾을 수 없습니다"
labels17 = re.findall(r'"([^"]+)"', _ins.group(1))
assert len(labels17) == 17, "상담보험 항목이 17종이 아닙니다: %d종 %s" % (len(labels17), labels17)
assert labels17 == EXPECT_INS, "상담보험 배열 순서가 지정 순서와 다릅니다: %s" % labels17
assert labels17[-1] == "기타", "기타가 마지막 항목이 아닙니다: %s" % labels17
assert "치매재가보험" not in labels17, "예전 라벨(치매재가보험)이 남아 있습니다: %s" % labels17
for must in ("화재보험", "실손의료비보험", "태아보험", "운전자보험", "치매보험"):
    assert must in labels17, "상담보험 항목 누락: %s" % must
assert len(set(labels17)) == len(labels17), "상담보험 항목에 중복이 있습니다: %s" % labels17
for attr in ['data-mer="오전"', 'data-mer="오후"', 'data-min="00"', 'data-min="30"',
             'data-method="전화"', 'data-method="문자"', 'id="hourSel"']:
    assert attr in tpl, "연락가능시간/연락방법 컨트롤 누락: %s" % attr
for token in ['id="insPrint"', 'id="timePrint"', 'id="methodPrint"', 'id="questionsPrint"']:
    assert token in tpl, "인쇄용 요약 누락: %s" % token
for field in ['"상담보험"', '"궁금하신 사항"', '"연락가능시간"', '"연락방법"']:
    assert field in code, "전송 payload 한국어 필드 누락: %s" % field
assert '"상담 메모":' not in code, "예전 단일 메모 필드가 payload에 남아 있습니다"
assert '"성함": name' in code, "전송 payload의 성함 필드 이름이 다릅니다"
_send = [r for r in json.loads(dukpy.evaljs(js4)) if r["tag"] == "send-valid"][0]
assert _send["payload"]["성함"] == "테스트 고객", "payload 성함 값이 다릅니다: %s" % _send["payload"].get("성함")
assert "고객 성함" not in _send["keys"], "payload에 '고객 성함' 필드가 남아 있습니다"
assert _send["payload"]["적정 범위"].startswith("7% ~ 12%"), \
    "payload 적정 범위가 7~12%가 아닙니다: %s" % _send["payload"]["적정 범위"]
assert _send["payload"]["_subject"].startswith("[1분 보험료 건강검진] "), "메일 제목 접두어가 바뀌었습니다"

# ---- 페이지 소스에 개인 메일 주소가 그대로 노출되지 않는지 ----
assert "formsubmit.co/ajax/3c7935155d1f7bb34b9ca963ae2c4df6" in html, \
    "formsubmit 별칭 엔드포인트가 페이지에 없습니다"
assert "kdm320538@gmail.com" not in html, \
    "페이지 소스에 개인 메일 주소가 노출됩니다"
print(json.dumps({"tag": "no-plain-email-in-page", "ok": True, "endpoint": "formsubmit 별칭"},
                 ensure_ascii=False))
print(json.dumps({"tag": "html-checks", "ok": True, "checks": [
    "예시 프리셋 없음", "성함 라벨", "자유롭게 기재해주세요", "상담보험 17항목(순서·라벨 일치)",
    "오전/오후·시·00/30분", "전화/문자", "인쇄 요약 4종", "payload 한국어 필드",
    "7~12% 고정", "저장 안내 문구·히어로 배지 없음", "내용 초기화",
    "명함 3문장", "인쇄 머리말에서 1분 보험료 건강검진 제거"]},
    ensure_ascii=False))
