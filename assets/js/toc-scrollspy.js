(function () {
  function initTocScrollspy() {
    var toc = document.querySelector(".sidebar .toc--sidebar, .sidebar .toc, nav.toc");
    if (!toc) {
      return;
    }

    var links = Array.prototype.slice.call(
      toc.querySelectorAll('a[href^="#"]')
    );
    if (!links.length) {
      return;
    }

    var sections = links
      .map(function (link) {
        var id = decodeURIComponent(link.getAttribute("href").slice(1));
        var el = document.getElementById(id);
        return el ? { id: id, link: link, el: el } : null;
      })
      .filter(Boolean);

    if (!sections.length) {
      return;
    }

    function setActive(id) {
      links.forEach(function (link) {
        var isActive =
          decodeURIComponent(link.getAttribute("href").slice(1)) === id;
        link.classList.toggle("is-active", isActive);
        if (link.parentElement) {
          link.parentElement.classList.toggle("is-active", isActive);
        }
      });
    }

    function updateActiveFromScroll() {
      var offset = 120;
      var current = sections[0].id;

      for (var i = 0; i < sections.length; i++) {
        var rect = sections[i].el.getBoundingClientRect();
        if (rect.top - offset <= 0) {
          current = sections[i].id;
        } else {
          break;
        }
      }

      setActive(current);
    }

    links.forEach(function (link) {
      link.addEventListener("click", function () {
        var id = decodeURIComponent(link.getAttribute("href").slice(1));
        setActive(id);
      });
    });

    window.addEventListener("scroll", updateActiveFromScroll, { passive: true });
    window.addEventListener("resize", updateActiveFromScroll);
    updateActiveFromScroll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTocScrollspy);
  } else {
    initTocScrollspy();
  }
})();
