These browser assets are stored locally so deployment does not require a CDN
or a JavaScript build step.

- Alpine.js 3.17.4: official `alpinejs` npm package, `dist/cdn.min.js`.
- Chart.js 4.5.1: official `chart.js` npm package, `dist/chart.umd.min.js`.

Each library's MIT license is stored alongside its asset. The Chart.js source
map comment is omitted because the map is not vendored; this also lets Django's
manifest static-file storage process the JavaScript without a missing-file error.
