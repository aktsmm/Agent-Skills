#!/usr/bin/env python3
"""Wrap a finished deck in one file that is both the deck and its review/presenting UI.

The deck is embedded unchanged in an iframe srcdoc (the forge verifier gates that
deck, not this wrapper). The wrapper adds: a closable, resizable comment panel with
per-slide autosave (keyed by deck title + slide id, stale marker when a slide
changed), comment types, filter and search, slide overview grid, jump by number and
deep links (#s5), AI-request copy, Markdown/JSON export and import, quoting of
 selected slide text, image lightbox, a laser pointer, a presenter view in a second window (notes,
next slide, timer, synced with the audience window), and a fullscreen mode that
hides the panel. Ship this one file; it replaces a separate review copy.
It carries its own script and is NOT covered by verify_html.py.

Usage: python build_review_viewer.py deck.html review.html
       python build_review_viewer.py --extract review.html deck.html   (recover the deck)
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root { --accent: #0067b8; --line: #d7dde6; --surface: #f6f8fb; --fg: #1b1f27; --muted: #5b6472; }
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; font-family: "Segoe UI", "Yu Gothic UI", "Hiragino Sans", Meiryo, system-ui, sans-serif; color: var(--fg); background: #0d0f13; }
#app { --panel: 340px; display: grid; grid-template-columns: minmax(0, 1fr) 10px var(--panel); height: 100%; }
#split { position: relative; background: var(--line); cursor: col-resize; touch-action: none; }
#split::after { content: ""; position: absolute; inset: calc(50% - 24px) 3px; background: #9aa4b2; border-radius: 2px; }
#split:hover, #split:focus-visible, #app.dragging #split { background: var(--accent); outline: none; }
#app.dragging { user-select: none; }
#app.dragging #deck { pointer-events: none; }
#deck { width: 100%; height: 100%; border: 0; background: #0d0f13; }
#panel { background: #fff; border-left: 1px solid var(--line); display: flex; flex-direction: column; min-height: 0; font-size: 14px; }
#panel header { padding: 12px 14px 8px; border-bottom: 1px solid var(--line); }
#panel h1 { font-size: 14px; margin: 0; color: var(--accent); }
#where { font-weight: 600; line-height: 1.4; }
#summary { font-size: 12px; color: var(--muted); margin: 2px 0 6px; }
#nav { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
button { font: inherit; padding: 5px 10px; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); color: var(--fg); cursor: pointer; }
button:hover { border-color: var(--accent); color: var(--accent); }
select, input[type="search"], input[type="number"] { font: inherit; padding: 4px 6px; border: 1px solid var(--line); border-radius: 6px; background: #fff; color: var(--fg); }
#editor { padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; border-bottom: 1px solid var(--line); }
textarea { width: 100%; min-height: 150px; resize: vertical; font: inherit; padding: 8px; border: 1px solid var(--line); border-radius: 6px; }
textarea:focus { outline: 2px solid var(--accent); }
#list { flex: 1; overflow: auto; padding: 8px 14px; min-height: 80px; }
#list button { display: flex; width: 100%; text-align: left; gap: 8px; margin: 0 0 4px; border-color: transparent; background: transparent; }
#list button.has { font-weight: 600; }
#list button.current { background: var(--surface); border-color: var(--line); }
#list .mark { width: 1.2em; color: var(--accent); flex: none; }
#list .snip { display: block; font-weight: 400; color: var(--muted); font-size: 12px; }
#actions { padding: 10px 14px; border-top: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
#status { font-size: 12px; color: var(--muted); flex-basis: 100%; }
#panelhead { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; flex-wrap: wrap; }
#panelhead h1 { flex: 1; }
#panelhead button { padding: 2px 8px; }
#stale { display: none; padding: 6px 8px; border-left: 3px solid #b45309; background: #fff7ed; font-size: 12px; border-radius: 4px; }
#stale.on { display: block; }
#stale button { margin-top: 4px; }
.hint { font-size: 12px; color: var(--muted); }
#notes { padding: 6px 14px; border-bottom: 1px solid var(--line); font-size: 13px; }
#notes summary { cursor: pointer; font-weight: 600; }
#notesBody { white-space: pre-wrap; line-height: 1.6; max-height: 160px; overflow: auto; margin-top: 6px; color: #3b4452; }
#tools { display: flex; gap: 6px; padding: 6px 14px; border-bottom: 1px solid var(--line); }
#tools input { flex: 1; min-width: 0; }
#jump { width: 4.6em; }
#presextra { display: none; padding: 12px 14px; border-bottom: 1px solid var(--line); }
#clock { font-size: 32px; font-weight: 700; font-variant-numeric: tabular-nums; }
#nexttitle { margin: 6px 0; font-weight: 600; }
#app.panel-off { grid-template-columns: minmax(0, 1fr); grid-template-rows: minmax(0, 1fr); }
#app.panel-off #split, #app.panel-off #panel { display: none; }
#gridview { position: fixed; inset: 0; z-index: 50; background: rgba(13, 15, 19, 0.95); overflow: auto; padding: 56px 24px 24px; }
#gridview[hidden] { display: none; }
#gridbody { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
#gridbody button.card { display: flex; flex-direction: column; gap: 6px; padding: 8px; background: #1b1f27; color: #fff; border: 2px solid transparent; text-align: left; }
#gridbody button.card.current { border-color: var(--accent); }
#gridbody button.card:focus-visible { outline: 3px solid #fff; }
#gridbody img { width: 100%; aspect-ratio: 16 / 9; object-fit: contain; background: #fff; border-radius: 4px; }
#gridbody .ph { aspect-ratio: 16 / 9; background: #2b313c; border-radius: 4px; }
#gridclose { position: fixed; top: 12px; right: 16px; }
#lightbox { position: fixed; inset: 0; z-index: 70; display: grid; place-items: center; padding: 48px; background: rgba(13, 15, 19, 0.94); }
#lightbox[hidden] { display: none; }
#lightbox img { max-width: min(94vw, 1800px); max-height: 84vh; object-fit: contain; background: #fff; box-shadow: 0 18px 60px rgba(0, 0, 0, 0.55); }
#lightbox p { position: fixed; left: 24px; right: 24px; bottom: 12px; margin: 0; color: #fff; text-align: center; font-size: 14px; }
#lightboxclose { position: fixed; top: 12px; right: 16px; width: 42px; height: 42px; padding: 0; border-color: #fff; border-radius: 50%; background: #1b1f27; color: #fff; font-size: 28px; line-height: 1; }
body.pres #presextra { display: block; }
body.pres #editor, body.pres #tools, body.pres #list, body.pres #actions, body.pres #pv, body.pres #close, body.pres #fs, body.pres #nav .edit { display: none; }
body.pres #notes { flex: 1; overflow: auto; border-bottom: 0; }
body.pres #notesBody { font-size: 20px; max-height: none; }
body.pres #app { --panel: 46vw; }
@media (max-width: 900px) { #app { --panel: 40vh; grid-template-columns: 1fr; grid-template-rows: minmax(0, 1fr) 10px var(--panel); } #panel { border-left: 0; overflow: auto; } textarea { min-height: 90px; } #split { cursor: row-resize; } #split::after { inset: 3px calc(50% - 24px); } }
</style>
</head>
<body>
<div id="app">
<iframe id="deck" title="スライド" allowfullscreen srcdoc="__SRCDOC__"></iframe>
<div id="split" role="separator" aria-orientation="vertical" aria-label="スライドとコメント欄の境界" tabindex="0" title="ドラッグで幅を変更（ダブルクリックで初期化）"></div>
<aside id="panel">
<header>
<div id="panelhead"><h1>コメント</h1><button type="button" id="pv" title="発表者ビューを別ウィンドウで開く（メモ・次のスライド・タイマー）">発表者ビュー</button><button type="button" id="fs" title="全画面で発表（コメント欄を隠す）">発表（全画面）</button><button type="button" id="close" aria-label="コメント欄を閉じる" title="コメント欄を閉じる（Alt+C）">×</button></div>
<div id="where">読み込み中</div>
<div id="summary"></div>
<div id="nav"><button type="button" id="prev">前</button><button type="button" id="next">次</button><button type="button" id="grid" title="スライド一覧（G）">一覧</button><label>移動 <input type="number" id="jump" min="1" aria-label="スライド番号へ移動"></label></div>
</header>
<div id="presextra"><div id="clock">00:00</div><div><button type="button" id="clockToggle">一時停止</button> <button type="button" id="clockReset">リセット</button></div><div id="nexttitle"></div></div>
<div id="editor">
<div id="stale">コメント後にこのスライドの内容が変わっています。コメントが今も当てはまるか確認してください。<br><button type="button" id="confirm">今も当てはまる</button></div>
<select id="ctype" aria-label="コメントの種類"><option value="">種類なし</option><option value="fix">要修正</option><option value="q">質問</option><option value="ok">OK</option></select>
<textarea id="comment" aria-label="このスライドへのコメント" placeholder="このスライドへのコメント（自動保存）"></textarea>
<div class="hint">Alt+C コメント欄 ／ Ctrl+Enter 次へ（Shift で前）／ G 一覧 ／ L ポインター ／ スライドの文字を選ぶと引用できます</div>
</div>
<details id="notes"><summary>発表者メモ</summary><div id="notesBody"></div></details>
<div id="tools"><input type="search" id="q" placeholder="スライド内を検索" aria-label="スライド内を検索"><select id="filter" aria-label="絞り込み"><option value="all">すべて</option><option value="commented">コメントあり</option><option value="fix">要修正</option><option value="q">質問</option><option value="ok">OK</option><option value="stale">要再確認</option></select></div>
<div id="list" aria-label="スライド一覧"></div>
<div id="actions">
<button type="button" id="copy">Markdown をコピー</button>
<button type="button" id="copyai" title="チャットに貼って反映を依頼する文面">AI への依頼文をコピー</button>
<button type="button" id="save">.md で保存</button>
<button type="button" id="savejson">.json で保存</button>
<button type="button" id="import">取り込み</button><input type="file" id="importfile" accept=".md,.json,.txt" hidden>
<button type="button" id="clear">すべて消去</button>
<span id="status" role="status" aria-live="polite"></span>
</div>
</aside>
</div>
<div id="gridview" hidden role="dialog" aria-label="スライド一覧"><button type="button" id="gridclose" aria-label="一覧を閉じる">×</button><div id="gridbody"></div></div>
<div id="lightbox" hidden role="dialog" aria-modal="true" aria-label="画像の拡大表示"><button type="button" id="lightboxclose" aria-label="拡大表示を閉じる">×</button><img id="lightboximage" alt=""><p id="lightboxcaption"></p></div>
<script>
(function () {
  var KEY = "review:__KEY__";
  var LEGACY_KEY = "review:__LEGACY__";
  var PANEL_KEY = "review-panel-off:__KEY__";
  var LAST_KEY = "review-last:__KEY__";
  var SYNC_KEY = "review-sync:__KEY__";
  var TITLE = __TITLE_JS__;
  var PRES = location.hash === "#presenter";
  function $(id) { return document.getElementById(id); }
  var frame = $("deck"), where = $("where"), box = $("comment"), ctype = $("ctype"), list = $("list"), status = $("status"), app = $("app");
  var gridView = $("gridview"), gridBody = $("gridbody");
  var lightbox = $("lightbox"), lightboxImage = $("lightboximage"), lightboxCaption = $("lightboxcaption"), lightboxReturn = null;
  var data = {}, slides = [], shown = null, filterMode = "all", query = "";
  var laserOn = false, laserDot = null, laserBtn = null, toggleBtn = null, gridBtn = null, pendingQuote = "";

  if (PRES) document.body.classList.add("pres");

  try {
    data = JSON.parse(localStorage.getItem(KEY) || "null");
    if (!data) { var old = localStorage.getItem(LEGACY_KEY); data = old ? JSON.parse(old) : {}; }
  } catch (e) { data = {}; }
  Object.keys(data).forEach(function (id) {
    var e = data[id];
    if (e && e.flag && !e.t) e.t = "fix";
    if (e) delete e.flag;
  });

  function hashText(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return (h >>> 0).toString(16);
  }
  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(data)); status.textContent = "保存しました " + new Date().toLocaleTimeString(); }
    catch (e) { status.textContent = "ブラウザーに保存できません。Markdown か .json で保存してください。"; }
  }
  function entry(id) { return data[id] || { text: "", t: "" }; }
  function has(id) { var e = data[id]; return !!(e && ((e.text || "").trim() || e.t)); }
  function slideOf(id) { for (var i = 0; i < slides.length; i++) if (slides[i].id === id) return slides[i]; return null; }
  function indexOf(id) { for (var i = 0; i < slides.length; i++) if (slides[i].id === id) return i; return -1; }
  function isStale(id) { var e = data[id], s = slideOf(id); return !!(e && e.h && s && e.h !== s.hash); }
  function deckDoc() { try { return frame.contentDocument; } catch (e) { return null; } }
  var TYPE_LABEL = { fix: "要修正", q: "質問", ok: "OK" };
  var TYPE_MARK = { fix: "！", q: "？", ok: "✓", "": "●" };

  function readSlides() {
    var d = deckDoc();
    if (!d) return;
    slides = [].map.call(d.querySelectorAll("#shf-root > [data-slide-id]"), function (s) {
      var h = s.querySelector("h1, h2");
      var c = s.cloneNode(true);
      var n = c.querySelector("[data-shf-notes]");
      var notes = n ? n.textContent.trim() : "";
      [].forEach.call(c.querySelectorAll("[data-shf-notes]"), function (x) { x.remove(); });
      var id = s.getAttribute("data-slide-id");
      var th = d.querySelector('img[data-shf-thumbnail="' + id + '"]');
      var sig = c.textContent.replace(/\s+/g, "")
        + [].map.call(c.querySelectorAll("a[href]"), function (a) { return a.getAttribute("href"); }).join("|")
        + [].map.call(c.querySelectorAll("svg"), function (g) { return g.outerHTML; }).join("|")
        + [].map.call(c.querySelectorAll("img"), function (m) { return m.getAttribute("src") || ""; }).join("|");
      return { id: id, title: h ? h.textContent.trim() : id, hash: hashText(sig), notes: notes, text: c.textContent.replace(/\s+/g, " ").trim(), thumb: th ? th.getAttribute("src") : "" };
    });
    $("jump").max = String(slides.length);
    $("jump").placeholder = "1-" + slides.length;
    renderList();
  }
  function currentId() {
    var d = deckDoc();
    var s = d && d.querySelector("#shf-root > [data-slide-id].is-active");
    return s ? s.getAttribute("data-slide-id") : null;
  }

  function matches(s) {
    var e = data[s.id];
    var ok = true;
    if (filterMode === "commented") ok = has(s.id);
    else if (filterMode === "fix" || filterMode === "q" || filterMode === "ok") ok = !!(e && e.t === filterMode);
    else if (filterMode === "stale") ok = isStale(s.id);
    if (!ok) return false;
    if (!query) return true;
    var q = query.toLowerCase();
    return s.title.toLowerCase().indexOf(q) >= 0 || s.text.toLowerCase().indexOf(q) >= 0 || (s.notes || "").toLowerCase().indexOf(q) >= 0;
  }
  function snippet(s) {
    var q = query.toLowerCase();
    var src = s.text.toLowerCase().indexOf(q) >= 0 ? s.text : (s.notes || s.text);
    var i = src.toLowerCase().indexOf(q);
    if (i < 0) return "";
    return (i > 14 ? "…" : "") + src.slice(Math.max(0, i - 14), i + 34) + "…";
  }
  function renderList() {
    var ae = document.activeElement;
    var focusedIdx = ae && list.contains(ae) ? [].indexOf.call(list.children, ae) : -1;
    list.textContent = "";
    slides.forEach(function (s, i) {
      if (!matches(s)) return;
      var b = document.createElement("button");
      b.type = "button";
      b.className = (has(s.id) ? "has " : "") + (s.id === shown ? "current" : "");
      if (s.id === shown) b.setAttribute("aria-current", "true");
      var m = document.createElement("span"); m.className = "mark"; m.textContent = has(s.id) ? TYPE_MARK[entry(s.id).t || ""] : "";
      var t = document.createElement("span");
      t.textContent = (i + 1) + ". " + s.title;
      if (query) { var sn = document.createElement("span"); sn.className = "snip"; sn.textContent = snippet(s); t.appendChild(sn); }
      b.appendChild(m); b.appendChild(t);
      b.addEventListener("click", function () { go(s.id); });
      list.appendChild(b);
    });
    Object.keys(data).forEach(function (id) {
      if (indexOf(id) >= 0 || !has(id) || query || (filterMode !== "all" && filterMode !== "commented")) return;
      var o = document.createElement("button");
      o.type = "button"; o.disabled = true; o.className = "has";
      o.textContent = "● 該当スライドなし: " + id;
      list.appendChild(o);
    });
    if (focusedIdx >= 0 && list.children[focusedIdx]) list.children[focusedIdx].focus();
  }
  function updateSummary() {
    var n = 0, fix = 0, stale = 0;
    Object.keys(data).forEach(function (id) {
      if (!has(id)) return;
      n++;
      if (data[id].t === "fix") fix++;
      if (isStale(id)) stale++;
    });
    $("summary").textContent = "コメント " + n + " 件・要修正 " + fix + " 件" + (stale ? "・要再確認 " + stale + " 件" : "");
  }

  function go(id) {
    var d = deckDoc();
    var link = d && d.querySelector('[data-shf-goto="' + id + '"]');
    if (link) link.click();
    syncNow();
  }
  function step(delta) {
    var d = deckDoc();
    var btn = d && d.querySelector('[data-shf-action="' + (delta > 0 ? "next" : "prev") + '"]');
    if (btn) btn.click();
    syncNow();
  }
  function syncNow() {
    var id = currentId();
    if (id && id !== shown) show(id);
  }

  var bc = null;
  try { bc = new BroadcastChannel("shf-slide:__KEY__"); bc.onmessage = function (e) { onRemote(e.data && e.data.id); }; } catch (e) { bc = null; }
  window.addEventListener("storage", function (e) { if (e.key === SYNC_KEY && e.newValue) onRemote(e.newValue.split("|")[0]); });
  function announce(id) {
    if (bc) bc.postMessage({ id: id });
    try { localStorage.setItem(SYNC_KEY, id + "|" + Date.now()); } catch (e) {}
  }
  function onRemote(id) { if (id && id !== shown && indexOf(id) >= 0) go(id); }

  function show(id) {
    shown = id;
    var i = indexOf(id);
    where.textContent = i < 0 ? "" : "スライド " + (i + 1) + " / " + slides.length + "　" + slides[i].title;
    var e = entry(id);
    box.value = e.text || "";
    ctype.value = e.t || "";
    var cur = i < 0 ? null : slides[i];
    if (cur && e.h && e.v !== 2) { e.h = cur.hash; e.v = 2; persist(); }
    $("notesBody").textContent = cur ? cur.notes : "";
    $("stale").classList.toggle("on", isStale(id));
    var nx = slides[i + 1];
    $("nexttitle").textContent = nx ? "次: " + (i + 2) + ". " + nx.title : "最後のスライドです";
    renderList();
    updateSummary();
    try { localStorage.setItem(LAST_KEY, id); } catch (err) {}
    if (!PRES) { try { history.replaceState(null, "", "#" + id); } catch (err) {} }
    announce(id);
  }
  function store() {
    if (!shown) return;
    var text = box.value;
    var cur = slideOf(shown);
    var prev = data[shown];
    if (!text.trim() && !ctype.value) delete data[shown]; else data[shown] = { text: text, t: ctype.value, h: prev && prev.h ? prev.h : (cur ? cur.hash : ""), v: 2 };
    persist();
    renderList();
    updateSummary();
  }
  box.addEventListener("input", store);
  ctype.addEventListener("change", store);
  $("confirm").addEventListener("click", function () {
    var cur = slideOf(shown), e = data[shown];
    if (cur && e) { e.h = cur.hash; e.v = 2; persist(); }
    $("stale").classList.remove("on");
    renderList(); updateSummary();
  });
  $("prev").addEventListener("click", function () { step(-1); });
  $("next").addEventListener("click", function () { step(1); });
  $("jump").addEventListener("keydown", function (e) {
    if (e.key !== "Enter" || e.isComposing) return;
    var n = parseInt($("jump").value, 10);
    if (n >= 1 && n <= slides.length) { go(slides[n - 1].id); $("jump").value = ""; }
  });
  $("filter").addEventListener("change", function () { filterMode = $("filter").value; renderList(); });
  $("q").addEventListener("input", function () { query = $("q").value.trim(); renderList(); });

  function ordered() {
    var out = [];
    slides.forEach(function (s, i) { if (has(s.id)) out.push({ s: s, i: i, e: entry(s.id) }); });
    return out;
  }
  function badges(e, s) {
    return (e.t ? " [" + TYPE_LABEL[e.t] + "]" : "") + (e.h && s && e.h !== s.hash ? " [スライド更新後は要再確認]" : "");
  }
  function orphans() { return Object.keys(data).filter(function (id) { return indexOf(id) < 0 && has(id); }); }
  function markdown(forAI) {
    var out = [];
    if (forAI) {
      out.push("HTML スライド「" + TITLE + "」のレビューコメントです。各コメントを反映してスライドを修正してください。対象はスライド ID と見出しで指定しています。「>」で始まる行は、スライドから引用した文です。");
      out.push("");
    } else {
      out.push("# スライドレビューコメント", "", "対象: " + TITLE, "出力日時: " + new Date().toLocaleString(), "");
    }
    var n = 0;
    ordered().forEach(function (x) {
      if (forAI && x.e.t === "ok" && !(x.e.text || "").trim()) return;
      n++;
      out.push("## " + (x.i + 1) + ". " + x.s.title + "（" + x.s.id + "）" + badges(x.e, x.s));
      out.push("");
      out.push((x.e.text || "").trim() || "（コメントなし。種類のみ）");
      out.push("");
    });
    orphans().forEach(function (id) {
      n++;
      out.push("## 該当スライドなし（" + id + "）", "", (entry(id).text || "").trim() || "（コメントなし。種類のみ）", "");
    });
    if (!n) out.push("コメントはありません。");
    if (forAI) out.push("修正後は、スライドごとに変更点を一覧で報告してください。");
    return out.join("\n");
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var t = document.createElement("textarea");
      t.value = text; document.body.appendChild(t); t.select();
      var ok = false; try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(t);
      ok ? resolve() : reject(new Error("copy failed"));
    });
  }
  function copyWith(text, okMsg) {
    copyText(text).then(function () { status.textContent = okMsg; }, function () { status.textContent = "コピーできませんでした。ファイルで保存してください。"; });
  }
  function download(name, mime, text) {
    var blob = new Blob([text], { type: mime + ";charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    status.textContent = "保存しました";
  }
  $("copy").addEventListener("click", function () { copyWith(markdown(false), "Markdown をコピーしました"); });
  $("copyai").addEventListener("click", function () { copyWith(markdown(true), "AI への依頼文をコピーしました"); });
  $("save").addEventListener("click", function () { download("slide-review-comments.md", "text/markdown", markdown(false)); });
  $("savejson").addEventListener("click", function () { download("slide-review-comments.json", "application/json", JSON.stringify({ title: TITLE, exportedAt: new Date().toISOString(), data: data }, null, 1)); });
  $("clear").addEventListener("click", function () {
    if (!window.confirm("すべてのコメントを消去しますか。")) return;
    data = {}; persist(); box.value = ""; ctype.value = ""; renderList(); updateSummary();
    $("stale").classList.remove("on");
  });

  function parseMarkdown(text) {
    var out = {}, cur = null;
    text.split(/\r?\n/).forEach(function (line) {
      if (/^## /.test(line)) {
        var m = /（([A-Za-z][\w-]*)）\s*((?:\[[^\]]*\]\s*)*)$/.exec(line);
        if (!m) { cur = null; return; }
        var t = /\[要修正\]/.test(m[2]) ? "fix" : /\[質問\]/.test(m[2]) ? "q" : /\[OK\]/.test(m[2]) ? "ok" : "";
        cur = { id: m[1], t: t, lines: [] };
        out[cur.id] = cur;
      } else if (cur) { cur.lines.push(line); }
    });
    var res = {};
    Object.keys(out).forEach(function (id) {
      var body = out[id].lines.join("\n").trim();
      if (/^（コメントなし/.test(body)) body = "";
      res[id] = { text: body, t: out[id].t };
    });
    return res;
  }
  function mergeImport(map) {
    var added = 0, merged = 0;
    Object.keys(map).forEach(function (id) {
      var inc = map[id];
      if (!inc || (!(inc.text || "").trim() && !inc.t)) return;
      var cur = slideOf(id);
      var ex = data[id];
      if (!ex) {
        data[id] = { text: inc.text || "", t: inc.t || "", h: cur ? cur.hash : "", v: 2 };
        added++;
      } else if ((ex.text || "") === (inc.text || "") && (ex.t || "") === (inc.t || "")) {
        return;
      } else {
        ex.text = (ex.text ? ex.text + "\n\n" : "") + "--- 取り込み ---\n" + (inc.text || "");
        ex.t = ex.t || inc.t || "";
        merged++;
      }
    });
    persist(); renderList(); updateSummary();
    if (shown) show(shown);
    status.textContent = added + " 件を取り込み、" + merged + " 件は既存のコメントに追記しました";
  }
  $("import").addEventListener("click", function () { $("importfile").click(); });
  $("importfile").addEventListener("change", function () {
    var f = $("importfile").files[0];
    if (!f) return;
    var r = new FileReader();
    r.onload = function () {
      var text = String(r.result || "");
      try {
        if (/^\s*\{/.test(text)) {
          var j = JSON.parse(text);
          var map = {};
          Object.keys(j.data || {}).forEach(function (id) { var e = j.data[id] || {}; map[id] = { text: e.text || "", t: e.t || (e.flag ? "fix" : "") }; });
          mergeImport(map);
        } else { mergeImport(parseMarkdown(text)); }
      } catch (err) { status.textContent = "取り込めませんでした: " + err.message; }
      $("importfile").value = "";
    };
    r.readAsText(f, "utf-8");
  });

  function renderGrid() {
    gridBody.textContent = "";
    slides.forEach(function (s, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "card" + (s.id === shown ? " current" : "");
      if (s.thumb) { var im = document.createElement("img"); im.src = s.thumb; im.alt = ""; b.appendChild(im); }
      else { var ph = document.createElement("div"); ph.className = "ph"; b.appendChild(ph); }
      var t = document.createElement("span");
      t.textContent = (i + 1) + ". " + s.title + (has(s.id) ? "　" + TYPE_MARK[entry(s.id).t || ""] : "");
      b.appendChild(t);
      b.addEventListener("click", function () { closeGrid(); go(s.id); });
      gridBody.appendChild(b);
    });
  }
  function openGrid() {
    renderGrid();
    gridView.hidden = false;
    var c = gridBody.querySelector(".current") || gridBody.firstChild;
    if (c) c.focus();
  }
  function closeGrid() { gridView.hidden = true; }
  $("grid").addEventListener("click", openGrid);
  $("gridclose").addEventListener("click", closeGrid);
  gridBody.addEventListener("keydown", function (e) {
    var cards = [].slice.call(gridBody.children);
    var i = cards.indexOf(document.activeElement);
    if (i < 0) return;
    var cols = cards.filter(function (c) { return c.offsetTop === cards[0].offsetTop; }).length || 1;
    var d = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: cols, ArrowUp: -cols }[e.key];
    if (!d) return;
    var n = cards[Math.max(0, Math.min(cards.length - 1, i + d))];
    if (n) n.focus();
    e.preventDefault();
  });

  function openLightbox(image, focusTarget) {
    if (!image || !image.getAttribute("src")) return;
    setLaser(false);
    lightboxReturn = focusTarget || image;
    lightboxImage.src = image.getAttribute("src");
    lightboxImage.alt = image.alt || "拡大画像";
    lightboxCaption.textContent = image.alt || "";
    lightbox.hidden = false;
    $("lightboxclose").focus();
  }
  function closeLightbox() {
    if (lightbox.hidden) return;
    lightbox.hidden = true;
    lightboxImage.removeAttribute("src");
    var target = lightboxReturn;
    lightboxReturn = null;
    try { if (target) target.focus(); } catch (e) {}
  }
  $("lightboxclose").addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", function (e) { if (e.target === lightbox) closeLightbox(); });

  function typing(e) {
    var t = e.target;
    return !!(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable));
  }
  function hotkeys(e) {
    if (e.isComposing || e.ctrlKey || e.metaKey) return;
    if (e.altKey) {
      if (e.key === "c" || e.key === "C") { setPanelOff(!app.classList.contains("panel-off")); e.preventDefault(); }
      return;
    }
    if (e.key === "Escape" && !lightbox.hidden) { closeLightbox(); e.preventDefault(); return; }
    if (e.key === "Escape" && !gridView.hidden) { closeGrid(); return; }
    if (typing(e)) return;
    if (e.key === "g" || e.key === "G") { gridView.hidden ? openGrid() : closeGrid(); e.preventDefault(); }
    else if (e.key === "l" || e.key === "L") { setLaser(!laserOn); e.preventDefault(); }
  }
  document.addEventListener("keydown", hotkeys);
  box.addEventListener("keydown", function (e) {
    if (e.isComposing || !e.ctrlKey || e.key !== "Enter") return;
    step(e.shiftKey ? -1 : 1);
    e.preventDefault();
  });

  function quoteText(t) {
    if (app.classList.contains("panel-off")) setPanelOff(false);
    var q = "> " + t.replace(/\s+/g, " ").slice(0, 240) + "\n";
    box.value = box.value ? box.value.replace(/\s*$/, "\n") + q : q;
    store();
    box.focus();
    box.setSelectionRange(box.value.length, box.value.length);
  }
  function setLaser(on) {
    laserOn = on;
    var d = deckDoc();
    if (d) d.documentElement.classList.toggle("review-laser", on);
    if (!on && laserDot) laserDot.style.display = "none";
    if (laserBtn) laserBtn.setAttribute("aria-pressed", String(on));
  }

  var split = $("split");
  var stackedQuery = window.matchMedia("(max-width: 900px)");
  function splitKey() { return stackedQuery.matches ? "review-split-h" : "review-split-w"; }
  function setPanel(px) {
    var stacked = stackedQuery.matches;
    var total = stacked ? app.clientHeight : app.clientWidth;
    var lo = stacked ? 160 : 260;
    var hi = Math.max(lo, total - (stacked ? 160 : 360));
    px = Math.round(Math.max(lo, Math.min(hi, px)));
    app.style.setProperty("--panel", px + "px");
    return px;
  }
  function panelSize() {
    var r = $("panel").getBoundingClientRect();
    return stackedQuery.matches ? r.height : r.width;
  }
  function restoreSplit() {
    split.setAttribute("aria-orientation", stackedQuery.matches ? "horizontal" : "vertical");
    app.style.removeProperty("--panel");
    if (PRES) return;
    var saved = 0;
    try { saved = parseInt(localStorage.getItem(splitKey()), 10) || 0; } catch (e) { saved = 0; }
    if (saved) setPanel(saved);
  }
  function saveSplit() { if (!PRES) { try { localStorage.setItem(splitKey(), String(Math.round(panelSize()))); } catch (e) {} } }
  split.addEventListener("pointerdown", function (e) { split.setPointerCapture(e.pointerId); app.classList.add("dragging"); });
  split.addEventListener("pointermove", function (e) {
    if (!app.classList.contains("dragging")) return;
    var r = app.getBoundingClientRect();
    setPanel(stackedQuery.matches ? r.bottom - e.clientY - 5 : r.right - e.clientX - 5);
  });
  function endDrag() {
    if (!app.classList.contains("dragging")) return;
    app.classList.remove("dragging");
    saveSplit();
  }
  split.addEventListener("pointerup", endDrag);
  split.addEventListener("pointercancel", endDrag);
  split.addEventListener("dblclick", function () {
    app.style.removeProperty("--panel");
    try { localStorage.removeItem(splitKey()); } catch (e) {}
  });
  split.addEventListener("keydown", function (e) {
    var grow = stackedQuery.matches ? "ArrowUp" : "ArrowLeft";
    var shrink = stackedQuery.matches ? "ArrowDown" : "ArrowRight";
    if (e.key !== grow && e.key !== shrink) return;
    setPanel(panelSize() + (e.key === grow ? 24 : -24));
    saveSplit();
    e.preventDefault();
  });
  window.addEventListener("resize", restoreSplit);
  stackedQuery.addEventListener("change", restoreSplit);
  restoreSplit();

  function savedOff() { try { return localStorage.getItem(PANEL_KEY); } catch (e) { return null; } }
  function syncToggle() { if (toggleBtn) toggleBtn.setAttribute("aria-pressed", String(!app.classList.contains("panel-off"))); }
  function setPanelOff(off) {
    if (PRES) return;
    app.classList.toggle("panel-off", off);
    try { localStorage.setItem(PANEL_KEY, off ? "1" : "0"); } catch (e) {}
    if (!off) restoreSplit();
    syncToggle();
    if (off) { if (toggleBtn) toggleBtn.focus(); } else box.focus();
  }
  if (!PRES && savedOff() === "1") app.classList.add("panel-off");
  var fsHid = false;
  $("close").addEventListener("click", function () { setPanelOff(true); });
  $("fs").addEventListener("click", function () {
    if (document.fullscreenElement) { document.exitFullscreen(); return; }
    app.classList.add("panel-off");
    fsHid = true;
    try { frame.contentWindow.focus(); } catch (e) {}
    var p = document.documentElement.requestFullscreen();
    if (p && p.catch) p.catch(function () { fsHid = false; if (savedOff() !== "1") app.classList.remove("panel-off"); });
  });
  document.addEventListener("fullscreenchange", function () {
    if (!document.fullscreenElement && fsHid) {
      fsHid = false;
      if (savedOff() !== "1") { app.classList.remove("panel-off"); $("fs").focus(); }
    }
  });
  $("pv").addEventListener("click", function () {
    window.open(location.href.split("#")[0] + "#presenter", "shf-presenter", "popup,width=1100,height=720");
  });

  var clockOn = true, clockStart = Date.now(), clockBase = 0;
  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  function tickClock() {
    var s = Math.floor((clockBase + (clockOn ? Date.now() - clockStart : 0)) / 1000);
    $("clock").textContent = pad(Math.floor(s / 60)) + ":" + pad(s % 60);
  }
  window.setInterval(tickClock, 500);
  $("clockToggle").addEventListener("click", function () {
    if (clockOn) { clockBase += Date.now() - clockStart; clockOn = false; $("clockToggle").textContent = "再開"; }
    else { clockStart = Date.now(); clockOn = true; $("clockToggle").textContent = "一時停止"; }
    tickClock();
  });
  $("clockReset").addEventListener("click", function () { clockBase = 0; clockStart = Date.now(); tickClock(); });
  if (PRES) $("notes").open = true;

  var OW_KEY = "review-outline-w";
  function installOutlineSplitter(d) {
    if (!d || !d.body || d.getElementById("shf-ow-handle")) return;
    var st = d.createElement("style");
    st.textContent = "@media (min-width: 701px) { html[data-shf-layout=\"outline\"] #shf-outline { flex-basis: var(--shf-ow, 264px); } html[data-shf-layout=\"outline\"]:not(.shf-outline-off) #shf-root { width: calc(100vw - var(--shf-ow, 264px)); height: calc((100vw - var(--shf-ow, 264px)) * 0.5625); } #shf-ow-handle { position: fixed; top: 0; bottom: 60px; left: calc(var(--shf-ow, 264px) - 4px); width: 8px; cursor: col-resize; z-index: 8; touch-action: none; } #shf-ow-handle:hover, #shf-ow-handle.drag { background: rgba(0, 103, 184, 0.55); } html.shf-outline-off #shf-ow-handle { display: none; } } @media (max-width: 700px) { #shf-ow-handle { display: none; } }";
    d.head.appendChild(st);
    var h = d.createElement("div");
    h.id = "shf-ow-handle";
    h.title = "ドラッグで一覧の幅を変更（ダブルクリックで初期化）";
    h.tabIndex = 0;
    h.setAttribute("role", "separator");
    h.setAttribute("aria-orientation", "vertical");
    h.setAttribute("aria-label", "スライド一覧の幅");
    d.body.appendChild(h);
    var root = d.documentElement;
    function apply(px) { root.style.setProperty("--shf-ow", Math.round(px) + "px"); }
    var saved = 0;
    try { saved = parseInt(localStorage.getItem(OW_KEY), 10) || 0; } catch (e) { saved = 0; }
    if (saved) apply(saved);
    h.addEventListener("pointerdown", function (e) { h.setPointerCapture(e.pointerId); h.classList.add("drag"); });
    h.addEventListener("pointermove", function (e) {
      if (!h.classList.contains("drag")) return;
      apply(Math.max(160, Math.min(d.defaultView.innerWidth * 0.5, e.clientX)));
    });
    function end() {
      if (!h.classList.contains("drag")) return;
      h.classList.remove("drag");
      try { localStorage.setItem(OW_KEY, String(parseInt(root.style.getPropertyValue("--shf-ow"), 10))); } catch (e) {}
    }
    h.addEventListener("pointerup", end);
    h.addEventListener("pointercancel", end);
    h.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      var cur = d.getElementById("shf-outline").getBoundingClientRect().width;
      apply(Math.max(160, Math.min(d.defaultView.innerWidth * 0.5, cur + (e.key === "ArrowRight" ? 24 : -24))));
      try { localStorage.setItem(OW_KEY, String(parseInt(root.style.getPropertyValue("--shf-ow"), 10))); } catch (err) {}
      e.preventDefault();
    });
    h.addEventListener("dblclick", function () {
      root.style.removeProperty("--shf-ow");
      try { localStorage.removeItem(OW_KEY); } catch (e) {}
    });
  }

  var ICONS = {
    comment: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    grid: '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
    laser: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>'
  };
  function chromeButton(d, bar, attr, title, icon, after) {
    var b = d.createElement("button");
    b.type = "button";
    b.setAttribute(attr, "");
    b.title = title;
    b.setAttribute("aria-label", title.replace(/（.*$/, ""));
    b.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS[icon] + '</svg>';
    if (after) after.after(b); else bar.appendChild(b);
    return b;
  }
  function installDeckTools(d) {
    var bar = d && d.getElementById("shf-chrome");
    if (!d || !d.body || !bar || bar.querySelector("[data-review-toggle]")) return;
    var st = d.createElement("style");
    st.textContent = "#review-laser{position:fixed;width:18px;height:18px;margin:-9px 0 0 -9px;border-radius:50%;background:rgba(230,30,30,.9);box-shadow:0 0 14px 6px rgba(230,30,30,.45);pointer-events:none;z-index:9999;display:none}html.review-laser,html.review-laser *{cursor:none!important}#review-quote{position:fixed;z-index:9999;display:none;padding:4px 10px;font:14px/1.4 system-ui,sans-serif;background:#0067b8;color:#fff;border:0;border-radius:14px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.35)}#shf-root>[data-slide-id] img{cursor:zoom-in}";
    d.head.appendChild(st);
    laserDot = d.createElement("div"); laserDot.id = "review-laser"; d.body.appendChild(laserDot);
    var q = d.createElement("button"); q.type = "button"; q.id = "review-quote"; q.textContent = "コメントに引用"; d.body.appendChild(q);
    var fsBtn = bar.querySelector('[data-shf-action="fullscreen"]');
    gridBtn = chromeButton(d, bar, "data-review-grid", "スライド一覧（G）", "grid", fsBtn);
    laserBtn = chromeButton(d, bar, "data-review-laser", "レーザーポインター（L）", "laser", gridBtn);
    toggleBtn = PRES ? null : chromeButton(d, bar, "data-review-toggle", "コメント欄の開閉（Alt+C）", "comment", laserBtn);
    gridBtn.addEventListener("click", openGrid);
    laserBtn.addEventListener("click", function () { setLaser(!laserOn); });
    if (toggleBtn) toggleBtn.addEventListener("click", function () { setPanelOff(!app.classList.contains("panel-off")); });
    laserBtn.setAttribute("aria-pressed", "false");
    syncToggle();
    d.addEventListener("mousemove", function (e) {
      if (!laserOn) return;
      laserDot.style.display = "block";
      laserDot.style.left = e.clientX + "px";
      laserDot.style.top = e.clientY + "px";
    });
    d.documentElement.addEventListener("mouseleave", function () { laserDot.style.display = "none"; });
    function showQuote() {
      var sel = d.getSelection();
      var t = sel ? sel.toString().trim() : "";
      if (!t || !sel.rangeCount) { q.style.display = "none"; return; }
      var r = sel.getRangeAt(0).getBoundingClientRect();
      pendingQuote = t;
      q.style.display = "block";
      q.style.left = Math.max(4, Math.min(d.defaultView.innerWidth - 130, r.left)) + "px";
      q.style.top = Math.max(4, r.top - 34) + "px";
    }
    d.addEventListener("mouseup", function () { setTimeout(showQuote, 0); });
    d.addEventListener("mousedown", function (e) { if (e.target !== q) q.style.display = "none"; });
    q.addEventListener("mousedown", function (e) { e.preventDefault(); });
    q.addEventListener("click", function () { quoteText(pendingQuote); q.style.display = "none"; d.getSelection().removeAllRanges(); });
    [].forEach.call(d.querySelectorAll("#shf-root > [data-slide-id] img"), function (image) {
      var interactive = image.closest("a,button");
      var target = interactive || image;
      if (!interactive) {
        image.tabIndex = 0;
        image.setAttribute("role", "button");
        image.setAttribute("aria-label", (image.alt || "画像") + "を拡大表示");
      }
      target.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        openLightbox(image, target);
      }, true);
      if (!interactive) image.addEventListener("keydown", function (e) {
        if (e.key !== "Enter" && e.key !== " ") return;
        openLightbox(image, image);
        e.preventDefault();
      });
    });
  }

  function openLinksInNewTab(d) {
    // A link followed inside the iframe replaces the deck, and most sites refuse to be framed.
    [].forEach.call(d.querySelectorAll('a[href^="http"]'), function (a) {
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener noreferrer");
    });
  }

  frame.addEventListener("load", function () {
    var d = deckDoc();
    installOutlineSplitter(d);
    if (d) {
      installDeckTools(d);
      openLinksInNewTab(d);
      d.addEventListener("keydown", hotkeys);
    }
    var side = d && d.querySelector('[data-shf-action="outline"]');
    if (side && side.getAttribute("aria-expanded") === "true") side.click();
    readSlides();
    var rootEl = d && d.getElementById("shf-root");
    if (rootEl && window.MutationObserver) new MutationObserver(syncNow).observe(rootEl, { subtree: true, attributes: true, attributeFilter: ["class", "hidden"] });
    var want = null;
    var h = location.hash.replace(/^#/, "");
    if (h && h !== "presenter") want = /^\d+$/.test(h) ? (slides[parseInt(h, 10) - 1] || {}).id : h;
    if (!want) {
      try { want = PRES ? (localStorage.getItem(SYNC_KEY) || "").split("|")[0] : localStorage.getItem(LAST_KEY); } catch (e) { want = null; }
    }
    if (want && indexOf(want) >= 0 && want !== currentId()) go(want);
    var id = currentId(); if (id) show(id);
    try { frame.contentWindow.focus(); } catch (e) {}
  });
  window.setInterval(function () {
    var id = currentId();
    if (id && id !== shown) show(id);
  }, 250);
})();
</script>
</body>
</html>
"""


def build(deck_path: Path, out_path: Path) -> None:
    text = deck_path.read_text(encoding="utf-8")
    match = re.search(r"<title>(.*?)</title>", text, flags=re.S)
    title = html.unescape(match.group(1)).strip() if match else deck_path.stem
    if 'data-shf-archetype="deck"' not in text:
        raise SystemExit("STOP: input is not a single-html-forge deck")
    key = hashlib.sha256(title.encode("utf-8")).hexdigest()[:16]
    legacy = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    srcdoc = text.replace("&", "&amp;").replace('"', "&quot;")
    page = (
        TEMPLATE.replace("__SRCDOC__", srcdoc)
        .replace("__TITLE_JS__", json.dumps(title, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__TITLE__", html.escape(title))
        .replace("__LEGACY__", legacy)
        .replace("__KEY__", key)
    )
    out_path.write_text(page, encoding="utf-8", newline="\n")


def extract(viewer_path: Path, out_path: Path) -> None:
    """Recover the embedded deck so it can be edited and re-finalized."""
    page = viewer_path.read_text(encoding="utf-8")
    match = re.search(r'<iframe id="deck"[^>]*? srcdoc="([^"]*)"', page)
    if not match:
        raise SystemExit("STOP: no embedded deck found")
    out_path.write_text(html.unescape(match.group(1)), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path, help="deck.html (or the review viewer with --extract)")
    parser.add_argument("output", type=Path)
    parser.add_argument("--extract", action="store_true", help="recover the deck from a review viewer")
    args = parser.parse_args()
    if args.deck.resolve() == args.output.resolve():
        raise SystemExit("STOP: output must differ from the input")
    (extract if args.extract else build)(args.deck, args.output)
    print(f"wrote {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
