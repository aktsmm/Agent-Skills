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
      for (var i = 0; i < slides.length; i++) {
        var active = i === index;
        slides[i].classList.toggle("is-active", active);
        slides[i].hidden = !active;
        slides[i].setAttribute("aria-hidden", active ? "false" : "true");
      }
      if (counter) {
        counter.textContent = index + 1 + " / " + slides.length;
      }
      if (pNow) pNow.textContent = titleFor(index);
      if (pNext) {
        pNext.textContent =
          index + 1 < slides.length ? titleFor(index + 1) : "\u2014";
      }
      if (pNotes) pNotes.textContent = noteFor(index);
      var here = slides[index] ? slides[index].getAttribute("data-slide-id") : "";
      tocLinks.forEach(function (link) {
        var on = link.getAttribute("data-shf-goto") === here;
        link.classList.toggle("is-current", on);
        if (on) link.setAttribute("aria-current", "true");
        else link.removeAttribute("aria-current");
      });
    }

    function go(next) {
      if (next < 0) next = 0;
      if (next > slides.length - 1) next = slides.length - 1;
      index = next;
      render();
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
      presenter.hidden = !on;
      document.body.classList.toggle("shf-presenting", on);
      if (on) {
        started = Date.now();
        tick();
        ticking = window.setInterval(tick, 1000);
      } else if (ticking !== null) {
        window.clearInterval(ticking);
        ticking = null;
      }
    }

    document.addEventListener("keydown", function (e) {
      if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
      var k = e.key;
      if (k === "ArrowRight" || k === "PageDown" || k === " ") {
        go(index + 1);
        e.preventDefault();
      } else if (k === "ArrowLeft" || k === "PageUp") {
        go(index - 1);
        e.preventDefault();
      } else if (k === "Home") {
        go(0);
        e.preventDefault();
      } else if (k === "End") {
        go(slides.length - 1);
        e.preventDefault();
      } else if (k === "s" || k === "S") {
        togglePresenter();
        e.preventDefault();
      } else if (k === "o" || k === "O") {
        root.classList.toggle("shf-outline-off");
        e.preventDefault();
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
          e.preventDefault();
        }
      });
    });

    all("[data-shf-action]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var action = btn.getAttribute("data-shf-action");
        if (action === "next") go(index + 1);
        else if (action === "prev") go(index - 1);
        else if (action === "presenter") togglePresenter();
        else if (action === "outline") root.classList.toggle("shf-outline-off");
      });
    });

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
