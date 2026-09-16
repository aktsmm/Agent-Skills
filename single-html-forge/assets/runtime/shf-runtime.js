/* single-html-forge fixed runtime v1
 *
 * Hash-pinned. Obeys the dataflow invariants in references/artifact-grammar.md:
 * it never creates elements, never writes markup, never touches CSSOM, and
 * never builds a URL. Every element it touches already exists in the artifact.
 */
(function () {
  "use strict";

  var root = document.documentElement;
  var archetype = root.getAttribute("data-shf-archetype");

  function all(sel) {
    return Array.prototype.slice.call(document.querySelectorAll(sel));
  }

  /* ---------- deck ---------- */

  function initDeck() {
    var slides = all("[data-slide-id]");
    if (slides.length === 0) return;

    var index = 0;
    var counter = document.getElementById("shf-slide-counter");
    var presenter = document.getElementById("shf-presenter");
    var pNow = document.getElementById("shf-presenter-now");
    var pNext = document.getElementById("shf-presenter-next");
    var pNotes = document.getElementById("shf-presenter-notes");
    var pClock = document.getElementById("shf-presenter-clock");
    var started = Date.now();
    var ticking = null;
    var tocLinks = all("[data-shf-goto]");
    var step = 0;
    var outline = document.getElementById("shf-outline");
    var menu = document.getElementById("shf-menu");
    var status = document.getElementById("shf-status");
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    var narrow = window.matchMedia("(max-width: 700px)");
    var motionInput = document.getElementById("shf-motion");
    var soundInput = document.getElementById("shf-sound");
    var volumeInput = document.getElementById("shf-volume");
    var context = null;
    var voices = [];
    var audioEpoch = 0;
    var soundOn = false;
    var motionOn = true;
    var beforePrint = null;

    function lastStep(slide) {
      return Array.prototype.reduce.call(slide.querySelectorAll("[data-shf-step]"), function (last, node) {
        return Math.max(last, Number(node.getAttribute("data-shf-step")));
      }, 0);
    }

    function announce(message) {
      if (status) status.textContent = message;
    }

    function cancelSound() {
      audioEpoch++;
      voices.forEach(function (voice) {
        try { voice.stop(); } catch (_) {}
        voice.disconnect();
      });
      voices = [];
    }

    function playSound(chapter) {
      cancelSound();
      if (!soundOn || document.hidden || !context) return;
      var epoch = audioEpoch;
      context.resume().then(function () {
        if (epoch !== audioEpoch || !soundOn || document.hidden) return;
        var volume = volumeInput ? Number(volumeInput.value) / 100 : 0.3;
        if (!volume) return;
        var oscillator = context.createOscillator();
        var gain = context.createGain();
        var now = context.currentTime;
        oscillator.type = "sine";
        oscillator.frequency.setValueAtTime(chapter ? 660 : 520, now);
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(volume * 0.12, now + 0.008);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
        oscillator.connect(gain);
        gain.connect(context.destination);
        voices.push(oscillator);
        oscillator.onended = function () { oscillator.disconnect(); gain.disconnect(); };
        oscillator.start(now);
        oscillator.stop(now + 0.12);
      }).catch(function () {
        if (epoch !== audioEpoch) return;
        soundOn = false;
        if (soundInput) soundInput.checked = false;
        cancelSound();
        syncControls();
        announce("Sound unavailable. Navigation remains available.");
      });
    }

    function setSound(enabled) {
      soundOn = enabled;
      cancelSound();
      if (enabled) {
        try {
          if (!context) context = new window.AudioContext();
          playSound(false);
        } catch (_) {
          soundOn = false;
          announce("Sound unavailable. Navigation remains available.");
        }
      }
      if (soundInput) soundInput.checked = soundOn;
      syncControls();
    }

    function closeMenu(restore) {
      if (!menu) return;
      menu.open = false;
      if (restore) menu.querySelector("summary").focus();
    }

    function setOutline(open, restore) {
      if (!outline) return;
      root.classList.toggle("shf-outline-off", !open);
      if (!open && (restore || outline.contains(document.activeElement))) {
        var control = document.querySelector('[data-shf-action="outline"]');
        if (control) control.focus();
      }
      syncControls();
    }

    function syncControls() {
      var isOpen = !!outline && !root.classList.contains("shf-outline-off");
      all('[data-shf-action="outline"]').forEach(function (button) {
        button.hidden = !outline;
        button.setAttribute("aria-expanded", String(isOpen));
      });
      all('[data-shf-action="mute"]').forEach(function (button) { button.hidden = !soundOn; });
      all('[data-shf-action="prev"]').forEach(function (button) { button.disabled = index === 0 && step === 0; });
      all('[data-shf-action="next"]').forEach(function (button) { button.disabled = index === slides.length - 1 && step === lastStep(slides[index]); });
      all('[data-shf-action="fullscreen"]').forEach(function (button) {
        button.setAttribute("aria-pressed", String(!!document.fullscreenElement));
      });
      var hasThumbnails = !!document.querySelector("[data-shf-thumbnail]");
      all('[data-shf-action="list-style"]').forEach(function (button) {
        button.hidden = !hasThumbnails;
        button.setAttribute("aria-pressed", String(root.classList.contains("shf-text-outline")));
      });
      root.classList.toggle("shf-motion-off", !motionOn || reduced.matches);
      if (motionInput) {
        motionInput.disabled = reduced.matches;
        motionInput.checked = motionOn && !reduced.matches;
      }
      var motionStatus = document.getElementById("shf-motion-status");
      if (motionStatus) motionStatus.hidden = !reduced.matches;
    }

    function noteFor(i) {
      var n = slides[i] ? slides[i].querySelector("[data-shf-notes]") : null;
      return n ? n.textContent : "";
    }

    function titleFor(i) {
      if (!slides[i]) return "";
      var h = slides[i].querySelector("h1, h2, h3");
      return h ? h.textContent : slides[i].getAttribute("data-slide-id");
    }

    function render() {
      root.setAttribute("data-shf-current-step", String(step));
      for (var i = 0; i < slides.length; i++) {
        var active = i === index;
        slides[i].classList.toggle("is-active", active);
        slides[i].hidden = !active;
        slides[i].setAttribute("aria-hidden", active ? "false" : "true");
        Array.prototype.forEach.call(slides[i].querySelectorAll("[data-shf-step]"), function (node) {
          var start = Number(node.getAttribute("data-shf-step"));
          var until = node.hasAttribute("data-shf-until") ? Number(node.getAttribute("data-shf-until")) : Infinity;
          node.toggleAttribute("hidden", step < start || step > until);
          node.classList.toggle("shf-emphasis", active && step === start);
        });
      }
      if (counter) {
        counter.textContent = index + 1 + " / " + slides.length;
      }
      var stepCounter = document.getElementById("shf-step-counter");
      if (stepCounter) {
        stepCounter.hidden = lastStep(slides[index]) === 0;
        stepCounter.textContent = "Step " + (step + 1) + " / " + (lastStep(slides[index]) + 1);
      }
      if (pNow) pNow.textContent = titleFor(index);
      if (pNext) {
        pNext.textContent =
          index + 1 < slides.length ? titleFor(index + 1) : "\u2014";
      }
      if (pNotes) pNotes.textContent = noteFor(index);
      var here = slides[index]
        ? slides[index].getAttribute("data-slide-id")
        : "";
      tocLinks.forEach(function (link) {
        var on = link.getAttribute("data-shf-goto") === here;
        link.classList.toggle("is-current", on);
        if (on) {
          link.setAttribute("aria-current", "true");
          var group = link.closest("details[data-shf-section]");
          if (group) group.open = true;
          if (outline && !root.classList.contains("shf-outline-off")) link.scrollIntoView({block: "nearest"});
        } else link.removeAttribute("aria-current");
      });
      all("details[data-shf-section]").forEach(function (group) {
        group.classList.toggle(
          "is-current-section",
          !!group.querySelector('[aria-current="true"]'),
        );
      });
      syncControls();
    }

    function go(next, nextStep, quiet) {
      if (next < 0) next = 0;
      if (next > slides.length - 1) next = slides.length - 1;
      nextStep = Math.max(0, Math.min(nextStep || 0, lastStep(slides[next])));
      var changed = index !== next || step !== nextStep;
      cancelSound();
      index = next;
      step = nextStep;
      render();
      if (changed && !quiet) playSound(slides[index].getAttribute("data-shf-chapter") === "true" && step === 0);
      if (changed) announce(titleFor(index) + ". Step " + (step + 1));
    }

    function advance(direction) {
      if (direction > 0) {
        if (step < lastStep(slides[index])) go(index, step + 1);
        else if (index < slides.length - 1) go(index + 1, 0);
      } else if (step > 0) go(index, step - 1);
      else if (index > 0) go(index - 1, lastStep(slides[index - 1]));
    }

    function pad(n) {
      return n < 10 ? "0" + n : "" + n;
    }

    function tick() {
      if (!pClock) return;
      var s = Math.floor((Date.now() - started) / 1000);
      pClock.textContent = pad(Math.floor(s / 60)) + ":" + pad(s % 60);
    }

    function togglePresenter() {
      if (!presenter) return;
      var on = presenter.hidden;
      closeMenu(false);
      presenter.hidden = !on;
      document.body.classList.toggle("shf-presenting", on);
      if (on) {
        started = Date.now();
        tick();
        ticking = window.setInterval(tick, 1000);
        var close = presenter.querySelector("button");
        if (close) close.focus();
      } else if (ticking !== null) {
        window.clearInterval(ticking);
        ticking = null;
        if (menu) menu.querySelector("summary").focus();
      }
    }

    document.addEventListener("keydown", function (e) {
      if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
      var k = e.key;
      if (k === "Escape") {
        if (presenter && !presenter.hidden) togglePresenter();
        else if (menu && menu.open) closeMenu(true);
        else if (narrow.matches) setOutline(false, true);
        return;
      }
      if (e.target && e.target.closest("input, textarea, select, [contenteditable]")) return;
      if (presenter && !presenter.hidden && k === "Tab") {
        var focusable = Array.prototype.slice.call(presenter.querySelectorAll("button, a[href]"));
        var position = focusable.indexOf(document.activeElement);
        if (focusable.length) focusable[(position + (e.shiftKey ? -1 : 1) + focusable.length) % focusable.length].focus();
        e.preventDefault();
        return;
      }
      if ((menu && menu.open) || (e.target && e.target.closest("button, a, summary") && (k === " " || k === "Enter"))) return;
      if (k === "ArrowRight" || k === "PageDown" || k === " ") {
        advance(1);
        e.preventDefault();
      } else if (k === "ArrowLeft" || k === "PageUp") {
        advance(-1);
        e.preventDefault();
      } else if (k === "Home") {
        go(0);
        e.preventDefault();
      } else if (k === "End") {
        go(slides.length - 1, lastStep(slides[slides.length - 1]));
        e.preventDefault();
      } else if (k === "s" || k === "S") {
        togglePresenter();
        e.preventDefault();
      } else if (k === "o" || k === "O") {
        setOutline(root.classList.contains("shf-outline-off"));
        e.preventDefault();
      } else if (k === "m" || k === "M") {
        setSound(false);
      } else if (k === "f" || k === "F") {
        toggleFullscreen();
      }
    });

    function indexOfSlide(id) {
      for (var i = 0; i < slides.length; i++) {
        if (slides[i].getAttribute("data-slide-id") === id) return i;
      }
      return -1;
    }

    tocLinks.forEach(function (link) {
      link.addEventListener("click", function (e) {
        var found = indexOfSlide(link.getAttribute("data-shf-goto"));
        if (found >= 0) {
          go(found);
          if (narrow.matches) {
            setOutline(false, false);
            slides[index].focus();
          }
          e.preventDefault();
        }
      });
    });

    all("[data-shf-action]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var action = btn.getAttribute("data-shf-action");
        if (action === "next") advance(1);
        else if (action === "prev") advance(-1);
        else if (action === "presenter") togglePresenter();
        else if (action === "outline") setOutline(root.classList.contains("shf-outline-off"));
        else if (action === "fullscreen") toggleFullscreen();
        else if (action === "mute") setSound(false);
        else if (action === "test-sound") setSound(true);
        else if (action === "list-style") {
          root.classList.toggle("shf-text-outline");
          syncControls();
        }
      });
    });

    function toggleFullscreen() {
      try {
        var request = document.fullscreenElement ? document.exitFullscreen() : root.requestFullscreen();
        request.catch(function () { announce("Fullscreen unavailable. Single-slide view is still available."); });
      } catch (_) { announce("Fullscreen unavailable. Single-slide view is still available."); }
    }

    if (soundInput) soundInput.addEventListener("change", function () { setSound(soundInput.checked); });
    if (volumeInput) volumeInput.addEventListener("input", cancelSound);
    if (motionInput) motionInput.addEventListener("change", function () { motionOn = motionInput.checked; syncControls(); });
    reduced.addEventListener("change", syncControls);
    narrow.addEventListener("change", function () { if (narrow.matches) setOutline(false, true); });
    document.addEventListener("fullscreenchange", syncControls);
    document.addEventListener("visibilitychange", cancelSound);
    document.addEventListener("click", function (event) { if (menu && !menu.contains(event.target)) closeMenu(false); });
    window.addEventListener("beforeprint", function () {
      beforePrint = {index: index, step: step};
      cancelSound();
      root.classList.add("shf-printing");
    });
    window.addEventListener("afterprint", function () {
      root.classList.remove("shf-printing");
      if (beforePrint) go(beforePrint.index, beforePrint.step, true);
      beforePrint = null;
    });
    if (narrow.matches) setOutline(false, false);
    render();
  }

  /* ---------- doc ---------- */

  function initDoc() {
    var sections = all("main section[id]");
    var links = all("[data-shf-navlink]");
    if (sections.length === 0 || links.length === 0) return;

    function activate(id) {
      links.forEach(function (a) {
        var on = a.getAttribute("data-shf-navlink") === id;
        a.classList.toggle("is-current", on);
        if (on) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
    }

    if (typeof window.IntersectionObserver !== "function") {
      activate(sections[0].id);
      return;
    }

    var seen = Object.create(null);
    var io = new window.IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          seen[entry.target.id] = entry.isIntersecting
            ? entry.intersectionRatio
            : 0;
        });
        var best = null;
        var bestRatio = 0;
        sections.forEach(function (s) {
          var r = seen[s.id] || 0;
          if (r > bestRatio) {
            bestRatio = r;
            best = s.id;
          }
        });
        if (best) activate(best);
      },
      { rootMargin: "-10% 0px -70% 0px", threshold: [0, 0.25, 0.5, 1] },
    );
    sections.forEach(function (s) {
      io.observe(s);
    });
    activate(sections[0].id);
  }

  /* ---------- print ---------- */

  function initPrint() {
    all('[data-shf-action="print"]').forEach(function (btn) {
      btn.addEventListener("click", function () {
        window.print();
      });
    });
  }

  /* ---------- boot ---------- */

  initPrint();
  if (archetype === "deck") initDeck();
  else if (archetype === "doc") initDoc();
  /* poster is static apart from the print button */
})();
