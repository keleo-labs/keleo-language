#!/usr/bin/env node

/** Build the compatibility schema from the modular Practice Language schemas. */

const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const schemaDir = path.join(root, 'schemas');
const entry = JSON.parse(fs.readFileSync(path.join(schemaDir, 'language.schema.json'), 'utf8'));
const legacyPath = path.join(root, 'language.schema.json');
const legacyId = 'https://example.com/keleo-studio/language.schema.json';
const modules = fs.readdirSync(schemaDir)
  .filter(name => name.endsWith('.schema.json') && name !== 'language.schema.json')
  .sort();

if (!modules.length || entry.$defs) throw new Error('Expected a modular entry point and schema modules');

const definitions = {};
const owners = new Map();
const resources = new Map();
const moduleIds = new Map();
resources.set(entry.$id, entry);

for (const name of modules) {
  const schema = JSON.parse(fs.readFileSync(path.join(schemaDir, name), 'utf8'));
  if (!schema.$id || !schema.$defs || !Object.keys(schema.$defs).length) {
    throw new Error(`${name} needs an $id and non-empty $defs`);
  }
  if (schema.$id !== new URL(name, entry.$id).href) {
    throw new Error(`${name} has an $id inconsistent with its path`);
  }
  if (resources.has(schema.$id)) throw new Error(`Duplicate schema $id: ${schema.$id}`);
  resources.set(schema.$id, schema);
  moduleIds.set(name, schema.$id);
  for (const [key, definition] of Object.entries(schema.$defs)) {
    if (owners.has(key)) throw new Error(`Duplicate definition: ${key}`);
    owners.set(key, name);
    definitions[key] = definition;
  }
}

function resolvePointer(schema, fragment) {
  if (!fragment.startsWith('#/$defs/')) throw new Error(`Unsupported reference: ${fragment}`);
  const parts = fragment.slice(2).split('/').map(part => part.replace(/~1/g, '/').replace(/~0/g, '~'));
  let target = schema;
  for (const part of parts) {
    if (target === null || typeof target !== 'object' || !(part in target)) {
      throw new Error(`Missing reference: ${fragment}`);
    }
    target = target[part];
  }
  return parts[1];
}

function flatten(value, baseId) {
  if (Array.isArray(value)) return value.map(item => flatten(item, baseId));
  if (value === null || typeof value !== 'object') return value;
  const result = {};
  for (const [key, child] of Object.entries(value)) {
    if (key === '$ref') {
      const uri = new URL(child, baseId);
      const resource = resources.get(uri.href.split('#')[0]);
      if (!resource) throw new Error(`Unknown schema resource: ${child}`);
      const definition = resolvePointer(resource, uri.hash);
      if (!owners.has(definition)) throw new Error(`Unknown definition: ${definition}`);
      result[key] = uri.hash;
    } else {
      result[key] = flatten(child, baseId);
    }
  }
  return result;
}

const bundled = {
  ...flatten(entry, entry.$id),
  $id: legacyId,
  deprecated: true,
  $defs: Object.fromEntries(Object.entries(definitions).map(([key, value]) => {
    const owner = owners.get(key);
    return [key, flatten(value, moduleIds.get(owner))];
  })),
};
const output = `${JSON.stringify(bundled, null, 2)}\n`;

if (process.argv[2] === '--check') {
  if (fs.readFileSync(legacyPath, 'utf8') !== output) {
    throw new Error('language.schema.json differs from the modular schemas; run npm run schema:build');
  }
} else if (process.argv.length === 2) {
  fs.writeFileSync(legacyPath, output);
} else {
  throw new Error('Usage: node utils/build-language-schema.js [--check]');
}
