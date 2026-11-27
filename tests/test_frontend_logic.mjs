import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
function between(start, end) {
  const a = html.indexOf(start);
  const b = html.indexOf(end, a + start.length);
  assert.notEqual(a, -1, `Could not find ${start}`);
  assert.notEqual(b, -1, `Could not find end marker ${end}`);
  return html.slice(a, b);
}

const functions = [
  between('function effectivePrice(', 'function getCheapestOption('),
  between('function sastCalendarBoundary(', 'function getExpiryInfo('),
  between('function getExpiryInfo(', '// Hide only the expired STORE offers'),
  between('function findOfferRaw(', 'function decorateCatalog('),
  between('function decorateCatalog(', 'function perUnit('),
  between('function applyCachedFeed(', 'function openFeedDatabase('),
  between('function isTrustedFeedUrl(', 'function makeTrustedFeedCachePayload('),
  between('function makeTrustedFeedCachePayload(', 'function formatTimeShort('),
  between('let offerBoundaryTimer = null;', '// --- Navigation & Auto-Sync Engine'),
].join('\n');

function harness(overrides = {}) {
  const context = {
    state: { province: 'Mpumalanga', showExpired: false, activeCards: { xtra: false, smart: false, boxer: false, spar: false }, ...overrides.state },
    REMOTE_CATALOG: [],
    feedMeta: {},
    window: { location: { href: 'https://basket.example/index.html', origin: 'https://basket.example', protocol: 'https:' } },
    Date, Number, String, Array, Math, Object, JSON, RegExp, URL, Infinity,
    console,
    clearTimeout() {},
    setTimeout(fn, ms) { context.__scheduledDelay = ms; context.__scheduledCallback = fn; return 1; },
  };
  vm.createContext(context);
  vm.runInContext(functions, context);
  return context;
}

// Date-only offer boundaries are fixed to South African Standard Time, not device timezone.
{
  const h = harness();
  const start = h.sastCalendarBoundary('2026-12-01');
  const next = h.sastCalendarBoundary('2026-12-01', 1);
  assert.equal(start, Date.UTC(2026, 11, 1) - 2 * 60 * 60 * 1000);
  assert.equal(next, Date.UTC(2026, 11, 2) - 2 * 60 * 60 * 1000);
  assert.equal(h.sastCalendarBoundary('2026-02-30'), NaN);
  assert.equal(h.sastCalendarBoundary('not-a-date'), NaN);
}

// Date-only offers show an honest label and use the Johannesburg calendar date.
{
  const h = harness();
  const _d = new Date(Date.now() + 2 * 60 * 60 * 1000);
  const today = _d.getUTCFullYear() + '-' + String(_d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(_d.getUTCDate()).padStart(2, '0');
  const info = h.getExpiryInfo(today, today, '', '');
  assert.equal(info.expired, false);
  assert.match(info.label, /Ends today · exact time not stated/);
}

// Refresh scheduling includes future boundaries for every alternate offer.
{
  const h = harness();
  const today = (() => { const d = new Date(Date.now() + 2 * 60 * 60 * 1000); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); })();
  const parts = today.split('-').map(Number);
  const tomorrow = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2] + 1)).toISOString().slice(0, 10);
  h.REMOTE_CATALOG = [{
    id: 'test', validUntil: '2099-12-31', validFromAt: '2099-01-01T00:00:00+02:00', validUntilAt: '2099-12-31T23:59:00+02:00', stores: [{
      store: 'Shoprite', validUntil: '2099-12-31', validFromAt: '2099-01-01T00:00:00+02:00', validUntilAt: '2099-12-31T23:59:00+02:00', moreOffers: [{ validFrom: tomorrow, validUntil: '2099-12-31' }]
    }]
  }];
  h.scheduleOfferBoundaryRefresh();
  const expected = h.sastCalendarBoundary(tomorrow);
  const expectedDelay = Math.max(250, Math.min(2147480000, expected - Date.now() + 100));
  assert.ok(Math.abs(h.__scheduledDelay - expectedDelay) <= 2, `scheduled ${h.__scheduledDelay}, expected approximately ${expectedDelay}`);
}

// Expired primary offers must not suppress a still-valid alternate pamphlet offer.
{
  const h = harness();
  const out = h.decorateCatalog([{
    id: 'chicken', name: 'Chicken Portions', provinces: ['All'],
    stores: [{
      store: 'Shoprite', price: 5, rewardPrice: 5, validFrom: '2020-01-01', validUntil: '2020-01-02',
      moreOffers: [
        { price: 59.99, rewardPrice: 59.99, validFrom: '2026-01-01', validUntil: '2099-12-31', provinces: ['Mpumalanga'], pamphletTitle: 'Regional Butchery' },
        { price: 1, rewardPrice: 1, validFrom: '2026-01-01', validUntil: '2099-12-31', provinces: ['Gauteng'] },
        { price: 2, rewardPrice: 2, validFrom: '2020-01-01', validUntil: '2020-01-02', provinces: ['Mpumalanga'] },
      ],
    }],
  }]);
  assert.equal(out.length, 1);
  assert.equal(out[0].stores[0].price, 59.99);
  assert.equal(out[0].stores[0].moreOffers.length, 0);
}

// An alternate date-only offer must not inherit the primary offer's exact expiry instant.
{
  const h = harness();
  const today = (() => { const d = new Date(Date.now() + 2 * 60 * 60 * 1000); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); })();
  const parts = today.split('-').map(Number);
  const tomorrow = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2] + 1)).toISOString().slice(0, 10);
  h.REMOTE_CATALOG = [{ id: 'regional-oil', name: 'Regional Oil', provinces: ['Mpumalanga'], stores: [{
    store: 'Boxer', price: 80, rewardPrice: 80, validFrom: today, validUntil: today,
    validFromAt: '2020-01-01T00:00:00+02:00', validUntilAt: '2020-01-01T23:59:00+02:00',
    moreOffers: [{ price: 70, rewardPrice: 70, validFrom: today, validUntil: tomorrow, provinces: ['Mpumalanga'] }]
  }] }];
  const out = h.decorateCatalog(h.REMOTE_CATALOG);
  assert.equal(out.length, 1);
  assert.equal(out[0].stores[0].price, 70);
  assert.equal(out[0].stores[0].validUntil, tomorrow);
  assert.equal(out[0].stores[0].validUntilAt, '');
}

// Current offers rank above cheaper offers that have not started yet.
{
  const h = harness();
  const out = h.decorateCatalog([{
    id: 'milk', name: 'Milk', provinces: ['All'],
    stores: [{
      store: 'Boxer', price: 30, rewardPrice: 30, validFrom: '2026-01-01', validUntil: '2099-12-31',
      moreOffers: [{ price: 10, rewardPrice: 10, validFrom: '2099-01-01', validUntil: '2099-12-31' }],
    }],
  }]);
  assert.equal(out[0].stores[0].price, 30);
  assert.equal(out[0].stores[0].moreOffers[0]._info.upcoming, true);
}

// Regional alternatives are not shown outside their own province.
{
  const h = harness({ state: { province: 'Mpumalanga' } });
  const out = h.decorateCatalog([{
    id: 'beef', name: 'Beef', provinces: ['Gauteng', 'Mpumalanga'],
    stores: [{
      store: 'Shoprite', price: 99, rewardPrice: 99, validFrom: '2026-01-01', validUntil: '2099-12-31', provinces: ['Gauteng'],
      moreOffers: [{ price: 89, rewardPrice: 89, validFrom: '2026-01-01', validUntil: '2099-12-31', provinces: ['Mpumalanga'] }],
    }],
  }]);
  assert.equal(out[0].stores[0].price, 89);
  assert.deepEqual(Array.from(out[0].stores[0].provinces), ['Mpumalanga']);
}

// An imported JSON file cannot grant itself the verified badge.
{
  const h = harness();
  const applied = h.applyCachedFeed({
    cacheSchemaVersion: 3, imported: true, approvalStatus: 'verified', verifiedAt: '2026-11-25T10:00:00Z',
    products: [{ id: 'x', name: 'X', stores: [{ store: 'Shoprite', price: 1 }] }],
  });
  assert.equal(applied, true);
  assert.equal(h.feedMeta.verified, false);
}

// An external feed's self-asserted verified flag is removed before caching.
{
  const h = harness();
  const external = h.makeTrustedFeedCachePayload({ approvalStatus: 'verified', verifiedAt: '2026-11-25T10:00:00Z', products: [] }, 'https://other.example/deals.json', '2026-11-25T12:00:00Z');
  assert.equal(external.approvalStatus, 'unverified');
  assert.equal(external.verifiedAt, '');
  assert.equal(external.imported, false);
  const local = h.makeTrustedFeedCachePayload({ approvalStatus: 'verified', verifiedAt: '2026-11-25T10:00:00Z', products: [] }, './deals.json', '2026-11-25T12:00:00Z');
  assert.equal(local.approvalStatus, 'verified');
  assert.equal(local.verifiedAt, '2026-11-25T10:00:00Z');
}

// Only the app's own origin can use its reviewed-feed verification metadata.
{
  const h = harness();
  assert.equal(h.isTrustedFeedUrl('./deals.json'), true);
  assert.equal(h.isTrustedFeedUrl('https://basket.example/feeds/deals.json'), true);
  assert.equal(h.isTrustedFeedUrl('https://other.example/deals.json'), false);
}

// Basket history looks up the exact alternate offer's own dates when possible.
{
  const h = harness();
  h.REMOTE_CATALOG = [{
    id: 'oil', name: 'Oil', validUntil: '2099-12-31',
    stores: [{
      store: 'Boxer', price: 70, rewardPrice: 70, validUntil: '2099-12-31',
      moreOffers: [{ price: 65, rewardPrice: 65, validFrom: '2026-11-25', validUntil: '2026-11-26' }],
    }],
  }];
  const found = h.findOfferRaw({ productId: 'oil', store: 'Boxer', price: 65, rewardPrice: 65 });
  assert.equal(found.validUntil, '2026-11-26');
}

console.log('Frontend logic tests passed: SAST date boundaries, date-only expiry labels, alternate-offer boundary scheduling, alternate date/time precedence, per-offer expiry, regional scope, offer timing, import trust, feed trust and basket provenance.');
