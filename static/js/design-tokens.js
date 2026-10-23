/**
 * Reads a design token out of CSS so JavaScript can use it.
 *
 * Why this is needed
 * ------------------
 * Every colour in this product is a CSS custom property, which works
 * everywhere the browser is doing the painting. A <canvas> is the exception:
 * Chart.js hands its colour strings straight to the 2D context, and
 * `ctx.fillStyle = "rgb(var(--color-success))"` is not a colour the canvas can
 * resolve. It fails silently and the shape is painted black -- which is what
 * made every chart on these three dashboards render as a black ring the first
 * time the palette was tokenised.
 *
 * So the charts resolve their tokens here instead, at the moment they are
 * configured, against the same custom properties the rest of the page uses.
 * One palette, one definition, and a theme change still moves the charts.
 *
 *   dsToken("success")        -> "rgb(3, 105, 70)"
 *   dsToken("danger", 0.15)   -> "rgba(186, 43, 46, 0.15)"
 *
 * Load it before any chart script. It has no dependencies.
 */
(function (global) {
  "use strict";

  var FALLBACK = "#808080";

  /**
   * Tokens are stored as space-separated RGB channels ("3 105 70") rather than
   * a hex, which is what lets CSS apply an opacity modifier to them. That
   * means the value read here needs assembling before a canvas will take it.
   */
  function channels(name) {
    var value = getComputedStyle(document.documentElement)
      .getPropertyValue("--color-" + name)
      .trim();
    return value || null;
  }

  function dsToken(name, alpha) {
    var raw = channels(name);
    if (!raw) {
      // A token that does not exist is a typo, and a silently black chart is
      // how that typo used to reach production. Say so, then stay visible.
      if (global.console && console.warn) {
        console.warn('dsToken: no such token "--color-' + name + '"');
      }
      return FALLBACK;
    }

    // Comma form rather than the modern space form. Both are valid CSS, but
    // canvas support for the space syntax is newer, and a chart is the one
    // place where being wrong means drawing nothing.
    var parts = raw.split(/[\s,]+/).filter(Boolean).join(", ");
    return alpha === undefined || alpha === null
      ? "rgb(" + parts + ")"
      : "rgba(" + parts + ", " + alpha + ")";
  }

  global.dsToken = dsToken;
})(window);
