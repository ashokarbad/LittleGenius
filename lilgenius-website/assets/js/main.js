/* Li'l Genius Pre-School - progressive enhancement only.
   Every page works with JS disabled; this file adds convenience. */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------- mobile menu */
  var burger = document.getElementById("burger");
  var nav = document.getElementById("nav");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      document.body.style.overflow = open ? "hidden" : "";
      if (open) { var f = nav.querySelector("a"); if (f) f.focus(); }
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A" && nav.classList.contains("is-open")) burger.click();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) { burger.click(); burger.focus(); }
    });
  }

  /* --------------------------------------------------------- sticky header */
  var head = document.getElementById("head");
  if (head) {
    var onScroll = function () { head.classList.toggle("is-stuck", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ------------------------------------------------------- scroll reveals */
  var revealables = document.querySelectorAll(".reveal");
  if (revealables.length) {
    if (reduce || !("IntersectionObserver" in window)) {
      revealables.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry, i) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var delay = Number(el.dataset.delay || 0) + i * 60;
          setTimeout(function () { el.classList.add("in"); }, delay);
          io.unobserve(el);
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      revealables.forEach(function (el) { io.observe(el); });
    }
  }

  /* -------------------------------------------------------------- lightbox */
  var galItems = Array.prototype.slice.call(document.querySelectorAll(".gal-item"));
  if (galItems.length) {
    var lb = document.createElement("div");
    lb.className = "lightbox";
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-modal", "true");
    lb.setAttribute("aria-label", "Photo viewer");
    lb.innerHTML =
      '<button class="lb-btn lb-close" aria-label="Close photo viewer">&times;</button>' +
      '<button class="lb-btn lb-prev" aria-label="Previous photo">&#8249;</button>' +
      '<button class="lb-btn lb-next" aria-label="Next photo">&#8250;</button>' +
      '<div><img alt=""><p class="lightbox-cap"></p></div>';
    document.body.appendChild(lb);

    var lbImg = lb.querySelector("img");
    var lbCap = lb.querySelector(".lightbox-cap");
    var index = 0;
    var lastFocus = null;

    function show(i) {
      index = (i + galItems.length) % galItems.length;
      var src = galItems[index].dataset.full || galItems[index].querySelector("img").src;
      var cap = galItems[index].dataset.caption || galItems[index].querySelector("img").alt || "";
      lbImg.src = src;
      lbImg.alt = cap;
      lbCap.textContent = cap;
    }
    function open(i) {
      lastFocus = document.activeElement;
      show(i);
      lb.classList.add("is-open");
      document.body.style.overflow = "hidden";
      lb.querySelector(".lb-close").focus();
    }
    function close() {
      lb.classList.remove("is-open");
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    }

    galItems.forEach(function (item, i) {
      item.addEventListener("click", function () { open(i); });
    });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(index - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(index + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(index - 1);
      if (e.key === "ArrowRight") show(index + 1);
    });
  }

  /* ------------------------------------------------------------ enquiry form
     Two delivery modes, chosen in content/site.json:
       form_endpoint = ""      -> opens a pre-filled WhatsApp message (no backend)
       form_endpoint = "https://formspree.io/f/xxxx" -> posts by email      */
  var form = document.getElementById("enquiry-form");
  if (form) {
    var status = document.getElementById("form-status");
    var endpoint = form.dataset.endpoint || "";
    var waNumber = form.dataset.whatsapp || "";

    function setStatus(msg, ok) {
      if (!status) return;
      status.textContent = msg;
      status.className = "form-status " + (ok ? "ok" : "bad");
      status.focus();
    }

    function validate() {
      var valid = true;
      form.querySelectorAll("[required]").forEach(function (input) {
        var slot = form.querySelector('[data-err="' + input.name + '"]');
        var msg = "";
        if (!input.value.trim()) msg = "This field is needed.";
        else if (input.type === "tel" && !/^[0-9+\s-]{10,15}$/.test(input.value.trim())) msg = "Enter a 10-digit mobile number.";
        else if (input.type === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(input.value.trim())) msg = "Enter a valid email address.";
        if (slot) slot.textContent = msg;
        if (msg) {
          valid = false;
          input.setAttribute("aria-invalid", "true");
        } else {
          input.removeAttribute("aria-invalid");
        }
      });
      return valid;
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) {
        setStatus("Please check the highlighted fields and try again.", false);
        var bad = form.querySelector('[aria-invalid="true"]');
        if (bad) bad.focus();
        return;
      }

      var data = new FormData(form);
      if (data.get("company")) return; // honeypot: silently drop bots

      if (!endpoint) {
        var lines = [
          "Enquiry from the Li'l Genius website",
          "Parent: " + (data.get("parent") || ""),
          "Child: " + (data.get("child") || "") + " (" + (data.get("age") || "") + ")",
          "Programme: " + (data.get("programme") || ""),
          "Phone: " + (data.get("phone") || ""),
          "Email: " + (data.get("email") || "-"),
          "Message: " + (data.get("message") || "-")
        ];
        window.open("https://wa.me/" + waNumber + "?text=" + encodeURIComponent(lines.join("\n")), "_blank", "noopener");
        setStatus("WhatsApp is opening with your details. Press send there and we will reply the same working day.", true);
        form.reset();
        return;
      }

      var btn = form.querySelector('button[type="submit"]');
      var label = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sending\u2026"; }

      fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (res) {
          if (!res.ok) throw new Error("Request failed");
          setStatus("Thank you. Your enquiry has reached us and we will call you back on the number you shared.", true);
          form.reset();
        })
        .catch(function () {
          setStatus("The form could not be sent. Please call " + (form.dataset.phone || "us") + " or message us on WhatsApp instead.", false);
        })
        .finally(function () {
          if (btn) { btn.disabled = false; btn.textContent = label; }
        });
    });
  }
})();
