/**
 * E2E smoke test — verifies the backend is reachable and returns
 * a valid product list response.
 *
 * Run:
 *   node tests/e2e/smoke.test.js
 *
 * Requires the backend running on http://localhost:8000
 */

const BACKEND = process.env.BACKEND_URL || "http://localhost:8000";
const ENDPOINT = `${BACKEND}/api/v1/products`;

async function assert(condition, message) {
  if (!condition) {
    console.error(`  FAIL: ${message}`);
    process.exitCode = 1;
  } else {
    console.log(`  PASS: ${message}`);
  }
}

async function smokeTest() {
  console.log(`\n=== E2E Smoke Test ===`);
  console.log(`Target: ${ENDPOINT}\n`);

  // Test 1: basic fetch
  const res = await fetch(ENDPOINT);
  assert(res.ok, `GET /api/v1/products returns 200 (got ${res.status})`);

  const body = await res.json();
  assert(Array.isArray(body.items), `response.items is an array`);
  assert(typeof body.total === "number", `response.total is a number`);
  assert(typeof body.limit === "number", `response.limit is a number`);
  assert(typeof body.offset === "number", `response.offset is a number`);

  // Test 2: pagination
  const res2 = await fetch(`${ENDPOINT}?limit=1&offset=0`);
  assert(res2.ok, `GET with limit=1 returns 200`);
  const body2 = await res2.json();
  assert(body2.limit === 1, `limit=1 is respected`);

  // Test 3: search
  const res3 = await fetch(`${ENDPOINT}?q=switch`);
  assert(res3.ok, `GET with q=switch returns 200`);

  // Test 4: invalid limit
  const res4 = await fetch(`${ENDPOINT}?limit=0`);
  assert(res4.status === 422, `limit=0 returns 422 validation error`);

  console.log(`\n=== Done ===\n`);
}

smokeTest().catch((err) => {
  console.error("Smoke test crashed:", err.message);
  process.exitCode = 1;
});
