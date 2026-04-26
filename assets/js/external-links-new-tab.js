function updateLinkTarget(link) {
  var href = link.getAttribute("href");

  if (!href || href.startsWith("#") || href.startsWith("javascript:")) {
    return;
  }

  var url;

  try {
    url = new URL(href, window.location.href);
  } catch (error) {
    return;
  }

  var isExternalHttpLink =
    (url.protocol === "http:" || url.protocol === "https:") &&
    url.hostname !== window.location.hostname &&
    url.hostname !== "zanejobe.github.io";

  if (isExternalHttpLink) {
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener noreferrer");
  } else {
    link.setAttribute("target", "_self");

    if (link.getAttribute("rel") === "noopener noreferrer") {
      link.removeAttribute("rel");
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("a[href]").forEach(updateLinkTarget);
});

document.addEventListener(
  "click",
  function (event) {
    var link = event.target.closest && event.target.closest("a[href]");

    if (link) {
      updateLinkTarget(link);
    }
  },
  true
);
