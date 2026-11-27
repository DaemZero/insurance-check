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
  "strip","stripLabel","sMonth","sYear","sDecade","basisChip","rateMin","rateMax",
  "rateMinVal","rateMaxVal","clientName","questions","saveState","toast","printHead","printMemo",
  "memoCard","insChips","insPrint","timePrint","methodPrint","hourSel","sendCard",
  "printHint","printHintText","printHintClose",
  "sendName","sendContact","sendConsent","sendBtn","sendStatus","sendStatusText",
  "resetBtn","clearMemoBtn","printBtn"];
__ids.forEach(function(id){ var e = new El(id); __els[id] = e; __all.push(e); });
__els.rateMin.value = "7"; __els.rateMax.value = "10";
__els.hourSel.disabled = true;
var __chips = [];
[["30대 직장인","350,110,60,50,13"],["40대 외벌이","450,150,80,60,48"],
 ["50대 자영업","380,120,70,30,32"],["60대","220,90,50,20,18"]].forEach(function(row){
  var c = new El("chip-" + row[0]);
  c.className = "chip"; c["data-p"] = row[1];
  __chips.push(c); __all.push(c);
});
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
  function chipByLabel(label){
    for (var i = 0; i < __chips.length; i++){ if (__chips[i]["data-p"] === label) return __chips[i]; }
    return null;
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

  /* 60대 예시 칩 */
  var c60 = null;
  for (var j = 0; j < __chips.length; j++){
    if (__chips[j].id === "chip-60대") c60 = __chips[j];
  }
  c60.fire("click");
  snap("60대 예시 클릭");

  __els.rateMin.value = "5"; __els.rateMin.fire("input");
  __els.rateMax.value = "13"; __els.rateMax.fire("input");
  set([350,110,60,50,13]); snap("custom-rate 5-13%");

  /* ---- 03 상담 정보: 상담보험 다중 선택 ---- */
  var insChips = __els.insChips.childs;
  function pressIns(label){
    for (var i = 0; i < insChips.length; i++){
      if (insChips[i].getAttribute("data-ins") === label){ insChips[i].fire("click"); return insChips[i]; }
    }
    return null;
  }
  out.push({tag: "ins-chip-count", count: insChips.length,
    labels: insChips.map(function(b){ return b.textContent; })});
  var c1 = pressIns("암보험");
  var c2 = pressIns("보장점검");
  var c3 = pressIns("치매재가보험");
  out.push({tag: "ins-select-3",
    pressed: [c1.getAttribute("aria-pressed"), c2.getAttribute("aria-pressed"), c3.getAttribute("aria-pressed")],
    cls: [c1.className, c2.className, c3.className],
    print: __els.insPrint.textContent,
    stored: localStorage.getItem("daemin_consult_insurance_v1")});
  pressIns("보장점검"); /* 다시 누르면 해제 */
  out.push({tag: "ins-toggle-off", print: __els.insPrint.textContent,
    stored: localStorage.getItem("daemin_consult_insurance_v1")});

  /* ---- 궁금하신 사항 ---- */
  __els.questions.value = "5세대 실손 전환 조건과 보장 공백이 궁금합니다";
  __els.questions.fire("input");
  __els.printBtn.fire("click"); /* 입력 후 400ms 디바운스 저장 → 인쇄 버튼이 즉시 저장 */
  out.push({tag: "questions-saved", stored: localStorage.getItem("daemin_consult_questions_v1"),
    printed: __printed});

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

  /* ---- 상담 정보 지우기 ---- */
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
    insPressed: __els.insChips.childs.filter(function(b){ return b.getAttribute("aria-pressed") === "true"; })
      .map(function(b){ return b.textContent; }),
    hour: __els.hourSel.value,
    hourDisabled: !!__els.hourSel.disabled,
    timePrint: __els.timePrint.textContent,
    methodPrint: __els.methodPrint.textContent,
    saveState: __els.saveState.textContent
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
    if (lab === "암보험" || lab === "보장점검") __els.insChips.childs[i].fire("click");
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

# ---- HTML 자체 검사: 60대 예시·03번 필드·인쇄 요약·전송 필드명 ----
tpl = (ROOT / "index.template.html").read_text(encoding="utf-8")
assert re.search(r'data-p="220,90,50,20,18">60대<', html), "01번 예시에 60대 칩이 없습니다"
assert 'id="clientName"' in html and '<label class="f-label" for="clientName">성함</label>' in html, \
    "03번 성함 칸(라벨 '성함')이 없습니다"
assert 'placeholder="자유롭게 기재해주세요"' in html, "궁금하신 사항 placeholder가 없습니다"
for label in ["종합보험", "암보험", "뇌/심장보험", "수술비보험", "상해보험", "간병보험",
              "치매재가보험", "치아보험", "펫보험", "종신보험", "연금보험", "보장점검", "기타"]:
    assert '"%s"' % label in code, "상담보험 항목 누락: %s" % label
for attr in ['data-mer="오전"', 'data-mer="오후"', 'data-min="00"', 'data-min="30"',
             'data-method="전화"', 'data-method="문자"', 'id="hourSel"']:
    assert attr in tpl, "연락가능시간/연락방법 컨트롤 누락: %s" % attr
for token in ['id="insPrint"', 'id="timePrint"', 'id="methodPrint"']:
    assert token in tpl, "인쇄용 요약 누락: %s" % token
for field in ['"상담보험"', '"궁금하신 사항"', '"연락가능시간"', '"연락방법"']:
    assert field in code, "전송 payload 한국어 필드 누락: %s" % field
assert '"상담 메모":' not in code, "예전 단일 메모 필드가 payload에 남아 있습니다"

# ---- 페이지 소스에 개인 메일 주소가 그대로 노출되지 않는지 ----
assert "formsubmit.co/ajax/3c7935155d1f7bb34b9ca963ae2c4df6" in html, \
    "formsubmit 별칭 엔드포인트가 페이지에 없습니다"
assert "kdm320538@gmail.com" not in html, \
    "페이지 소스에 개인 메일 주소가 노출됩니다"
print(json.dumps({"tag": "no-plain-email-in-page", "ok": True, "endpoint": "formsubmit 별칭"},
                 ensure_ascii=False))
print(json.dumps({"tag": "html-checks", "ok": True, "checks": [
    "60대 예시 칩", "성함 라벨", "자유롭게 기재해주세요", "상담보험 13항목",
    "오전/오후·시·00/30분", "전화/문자", "인쇄 요약 3종", "payload 4개 한국어 필드"]},
    ensure_ascii=False))
