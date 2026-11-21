// Framed Worlds — charge models.json et construit la galerie.
// Tout le contenu est inséré via textContent (aucun HTML injecté depuis le JSON).
(function () {
  "use strict";

  var grid = document.getElementById("grid");
  document.getElementById("year").textContent = new Date().getFullYear();

  function safeUrl(u) {
    return typeof u === "string" && /^https?:\/\//i.test(u) ? u : null;
  }

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }

  function status(msg, hint) {
    grid.textContent = "";
    var p = el("p", { class: "status" }, msg);
    if (hint) { p.appendChild(document.createElement("br")); p.appendChild(el("code", null, hint)); }
    grid.appendChild(p);
  }

  function setProfileLinks(profile) {
    ["makerworld", "instagram"].forEach(function (key) {
      var url = safeUrl(profile && profile[key]);
      document.querySelectorAll('[data-link="' + key + '"]').forEach(function (a) {
        if (url) a.href = url; else a.hidden = true;
      });
    });
  }

  var catLabel = {};          // id -> label
  var filters = document.getElementById("filters");

  function catsOf(m) {
    return Array.isArray(m.categories) ? m.categories.filter(function (c) { return catLabel[c]; }) : [];
  }

  function card(m) {
    var mw = safeUrl(m.makerworld);
    var ig = safeUrl(m.instagram);
    var c = el("article", { class: "card" });

    var media = el(mw ? "a" : "div", mw ? { class: "card-media", href: mw, target: "_blank", rel: "noopener", tabindex: "-1", "aria-hidden": "true" } : { class: "card-media" });
    var img = el("img", { src: m.image || "", alt: m.alt || m.title || "", loading: "lazy", decoding: "async", width: "1200", height: "1200" });
    img.addEventListener("error", function () { media.classList.add("missing"); });
    if (!m.image) media.classList.add("missing");
    media.appendChild(img);
    c.appendChild(media);

    var body = el("div", { class: "card-body" });
    body.appendChild(el("h3", null, m.title || "Untitled"));
    if (m.description) body.appendChild(el("p", null, m.description));
    var cats = catsOf(m);
    var tags = Array.isArray(m.tags) ? m.tags : [];
    if (cats.length || tags.length) {
      var ul = el("ul", { class: "tags" });
      cats.forEach(function (c) { ul.appendChild(el("li", { class: "cat" }, catLabel[c])); });
      tags.forEach(function (t) { ul.appendChild(el("li", null, String(t))); });
      body.appendChild(ul);
    }
    var actions = el("div", { class: "card-actions" });
    var t = m.title || "this model";
    if (mw) actions.appendChild(el("a", { class: "btn btn-primary btn-sm", href: mw, target: "_blank", rel: "noopener", "aria-label": "Download " + t + " on MakerWorld" }, "MakerWorld ↗"));
    if (ig) actions.appendChild(el("a", { class: "btn btn-ghost btn-sm", href: ig, target: "_blank", rel: "noopener", "aria-label": t + " on Instagram" }, "Instagram ↗"));
    body.appendChild(actions);
    c.appendChild(body);
    return c;
  }

  fetch("models.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (data) {
      setProfileLinks(data.profile || {});
      var models = (data.models || []).slice();
      // plus récents d'abord (si "date" renseignée), sinon ordre du fichier
      models.sort(function (a, b) { return (b.date || "").localeCompare(a.date || ""); });
      if (!models.length) { status("New worlds are on their way — follow along on Instagram."); return; }

      (data.categories || []).forEach(function (c) {
        if (c && c.id && c.label) catLabel[c.id] = c.label;
      });
      // catégories effectivement utilisées, dans l'ordre du fichier (les vides sont masquées)
      var used = (data.categories || []).filter(function (c) {
        return catLabel[c.id] && models.some(function (m) { return catsOf(m).indexOf(c.id) !== -1; });
      });

      var params = new URLSearchParams(location.search);
      var active = params.get("category");
      if (!used.some(function (c) { return c.id === active; })) active = "all";

      function render() {
        grid.textContent = "";
        models
          .filter(function (m) { return active === "all" || catsOf(m).indexOf(active) !== -1; })
          .forEach(function (m) { grid.appendChild(card(m)); });
      }

      if (used.length) {
        var chips = [{ id: "all", label: "All" }].concat(used);
        chips.forEach(function (c) {
          var n = c.id === "all" ? models.length
            : models.filter(function (m) { return catsOf(m).indexOf(c.id) !== -1; }).length;
          var b = el("button", { type: "button", class: "chip", "data-cat": c.id, "aria-pressed": String(c.id === active) }, c.label);
          b.appendChild(el("span", { class: "count", "aria-hidden": "true" }, String(n)));
          b.addEventListener("click", function () {
            active = c.id;
            filters.querySelectorAll(".chip").forEach(function (x) {
              x.setAttribute("aria-pressed", String(x.getAttribute("data-cat") === active));
            });
            var u = new URL(location.href);
            if (active === "all") u.searchParams.delete("category"); else u.searchParams.set("category", active);
            history.replaceState(null, "", u);
            render();
          });
          filters.appendChild(b);
        });
        filters.hidden = false;
      }
      render();
    })
    .catch(function (err) {
      console.error("models.json:", err);
      if (location.protocol === "file:") {
        status("Aperçu local : ouvre le site via un petit serveur, pas en double-cliquant.", "python -m http.server  →  http://localhost:8000");
      } else {
        status("The gallery could not be loaded right now.");
      }
    });
})();
