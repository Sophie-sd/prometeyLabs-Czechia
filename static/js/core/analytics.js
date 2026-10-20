/**
 * ANALYTICS.JS — Deferred analytics initialization.
 * Loaded with `defer` to reduce TBT and improve LCP/FCP.
 *
 * Meta (Facebook) Pixel and all other ad tags are managed exclusively via
 * Google Tag Manager (GTM-MQBJTH87, templates/partials/gtm_head.html). This file only activates any CSS that
 * was loaded non-blocking via the media="print" swap trick.
 */

document.querySelectorAll('link[data-async-css]').forEach((link) => {
    link.media = 'all';
});
