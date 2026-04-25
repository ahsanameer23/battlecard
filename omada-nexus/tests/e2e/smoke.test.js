/**
 * E2E Smoke Tests
 * Uses Node's native fetch to validate the FastAPI backend.
 */

const API_URL = process.env.API_URL || 'http://localhost:8000/api/v1';

async function runSmokeTests() {
  console.log('Running E2E Smoke Tests...');
  let hasErrors = false;

  const assert = (condition, message) => {
    if (!condition) {
      console.error(`❌ FAIL: ${message}`);
      hasErrors = true;
    } else {
      console.log(`✅ PASS: ${message}`);
    }
  };

  try {
    // 1. Test standard fetch and response shape
    const res = await fetch(`${API_URL}/products`);
    assert(res.status === 200, `Products endpoint returned ${res.status}`);
    
    const data = await res.json();
    assert(Array.isArray(data), 'Response should be an array');
    
    if (data.length > 0) {
      const item = data[0];
      assert(item.id !== undefined, 'Item has id');
      assert(item.vendor !== undefined, 'Item has vendor');
      assert(item.model !== undefined, 'Item has model');
      assert(typeof item.specs_json === 'object', 'specs_json is parsed into an object');
    } else {
      console.log('⚠️  WARN: DB is empty, skipping shape validation.');
    }

    // 2. Test pagination
    const limitRes = await fetch(`${API_URL}/products?limit=1`);
    const limitData = await limitRes.json();
    assert(limitData.length <= 1, 'Pagination limit is respected');

    // 3. Test search
    const searchRes = await fetch(`${API_URL}/products?q=nonexistent_xyz_123`);
    const searchData = await searchRes.json();
    assert(searchData.length === 0, 'Search returns correct results for non-existent query');

    // 4. Test validation
    const invalidRes = await fetch(`${API_URL}/products?limit=2000`);
    assert(invalidRes.status === 422, 'Validation rejects limits > 1000');

  } catch (error) {
    console.error('❌ FAIL: Exception occurred during testing:', error.message);
    hasErrors = true;
  }

  if (hasErrors) {
    console.error('\nSmoke tests failed.');
    process.exit(1);
  } else {
    console.log('\nAll smoke tests passed successfully!');
    process.exit(0);
  }
}

runSmokeTests();
