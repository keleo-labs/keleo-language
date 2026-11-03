#!/usr/bin/env node

/** Check that modular and compatibility schemas validate the same documents. */

const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const Ajv = require('ajv/dist/2020');
const addFormats = require('ajv-formats');

const root = path.join(__dirname, '..');
const schemaDir = path.join(root, 'schemas');
const fixtures = path.join(root, 'validate', 'fixtures');
const legacy = JSON.parse(fs.readFileSync(path.join(root, 'language.schema.json'), 'utf8'));
const modular = JSON.parse(fs.readFileSync(path.join(schemaDir, 'language.schema.json'), 'utf8'));

execFileSync(process.execPath, [path.join(__dirname, 'build-language-schema.js'), '--check']);

function compiler() {
  const ajv = new Ajv({ allErrors: true, strict: false });
  addFormats(ajv);
  return ajv;
}

const legacyAjv = compiler();
const modularAjv = compiler();
const names = new Set();
const moduleSchemas = [];
for (const file of fs.readdirSync(schemaDir).filter(name => name.endsWith('.schema.json') && name !== 'language.schema.json')) {
  const schema = JSON.parse(fs.readFileSync(path.join(schemaDir, file), 'utf8'));
  assert.equal(modularAjv.validateSchema(schema), true, `${file}: ${JSON.stringify(modularAjv.errors)}`);
  assert.equal(schema.$comment, modular.$comment, `${file} has a different schema version`);
  for (const name of Object.keys(schema.$defs)) {
    assert(!names.has(name), `Duplicate definition: ${name}`);
    names.add(name);
    assert(legacy.$defs[name], `Missing compatibility pointer: ${name}`);
  }
  modularAjv.addSchema(schema);
  moduleSchemas.push(schema);
}
assert.equal(names.size, Object.keys(legacy.$defs).length);
const catalogDir = path.join(schemaDir, 'catalogs');
const catalogFiles = fs.readdirSync(catalogDir).filter(name => name.endsWith('.schema.json')).sort();
assert.deepEqual(catalogFiles, ['methodology-catalog.schema.json', 'practice-catalog.schema.json',
  'project-catalog.schema.json', 'source-catalog.schema.json']);
for (const file of catalogFiles) {
  const schema = JSON.parse(fs.readFileSync(path.join(catalogDir, file), 'utf8'));
  const ajv = compiler();
  assert.equal(ajv.validateSchema(schema), true, `${file}: ${JSON.stringify(ajv.errors)}`);
  ajv.compile(schema);
}
assert.equal(modularAjv.validateSchema(modular), true, JSON.stringify(modularAjv.errors));
for (const schema of moduleSchemas) {
  for (const name of Object.keys(schema.$defs)) {
    assert(modularAjv.getSchema(`${schema.$id}#/$defs/${name}`), `Unresolved modular definition: ${name}`);
  }
}

const validateLegacy = legacyAjv.compile(legacy);
const validateModular = modularAjv.compile(modular);
let checked = 0;
for (const file of fs.readdirSync(fixtures).filter(name => name.endsWith('.json'))) {
  const data = JSON.parse(fs.readFileSync(path.join(fixtures, file), 'utf8'));
  assert.equal(!!validateModular(data), !!validateLegacy(data), `Validation mismatch: ${file}`);
  checked++;
}

const invalid = JSON.parse(fs.readFileSync(path.join(fixtures, 'fixture-baseline.json'), 'utf8'));
const alpha = invalid.alphas[0];
const modularAlpha = modularAjv.getSchema(`${new URL('practice.schema.json', modular.$id).href}#/$defs/Alpha`);
const legacyAlpha = legacyAjv.getSchema(`${legacy.$id}#/$defs/Alpha`);
assert(modularAlpha && legacyAlpha);
assert.equal(modularAlpha(alpha), legacyAlpha(alpha));
assert.equal(modularAlpha(alpha), true);
delete invalid.alphas[0].name;
assert.equal(validateLegacy(invalid), false);
assert.equal(validateModular(invalid), false);

console.log(`Schema parity: ${names.size} definitions, ${checked} fixtures, one invalid mutation`);
