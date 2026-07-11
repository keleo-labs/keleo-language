#!/usr/bin/env node

/**
 * JSON Schema validator for Practice Language JSON
 * Usage: node validate/validate-schema.js <path-to-json-file>
 */

const fs = require('fs');
const path = require('path');
const Ajv = require('ajv/dist/2020');
const addFormats = require('ajv-formats');

const jsonFile = process.argv[2];
if (!jsonFile) {
  console.error('Usage: node validate/validate-schema.js <path-to-json-file>');
  process.exit(1);
}

const schemaPath = path.join(__dirname, '..', 'language.schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
const data = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));

const ajv = new Ajv({
  allErrors: true,
  verbose: true,
  strict: false
});
addFormats(ajv);

let validate;
try {
  validate = ajv.compile(schema);
} catch (err) {
  console.error('Schema compilation error:', err.message);
  process.exit(1);
}

const valid = validate(data);

if (valid) {
  console.log('✓ JSON is valid against schema');
  process.exit(0);
} else {
  console.log('✗ JSON validation failed\n');
  console.log('ERRORS FOUND:');
  console.log('=============\n');

  validate.errors.forEach((err, idx) => {
    console.log(`${idx + 1}. ${err.instancePath || '(root)'}`);
    console.log(`   Issue: ${err.message}`);
    if (err.params) {
      console.log(`   Details: ${JSON.stringify(err.params)}`);
    }
    if (err.schemaPath) {
      console.log(`   Schema: ${err.schemaPath}`);
    }
    console.log();
  });

  console.log(`Total errors: ${validate.errors.length}`);
  process.exit(1);
}
