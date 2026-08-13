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

function detectChainCycles(getParent, startNodes) {
  const cycles = [];
  const reported = new Set();
  for (const start of startNodes) {
    const visited = [];
    const visitedSet = new Set();
    let current = start;
    while (getParent(current) != null) {
      if (visitedSet.has(current)) {
        const idx = visited.indexOf(current);
        const cycle = visited.slice(idx).concat(current);
        const key = [...new Set(cycle)].sort().join('\0');
        if (!reported.has(key)) {
          reported.add(key);
          cycles.push(cycle);
        }
        break;
      }
      visited.push(current);
      visitedSet.add(current);
      current = getParent(current);
    }
  }
  return cycles;
}

function detectDAGCycles(nodes, edges) {
  const cycles = [];
  const reported = new Set();
  const WHITE = 0, GREY = 1, BLACK = 2;
  const colour = new Map();

  for (const start of nodes) {
    if ((colour.get(start) || WHITE) !== WHITE) continue;

    const stack = [[start, [...(edges.get(start) || [])], 0]];
    colour.set(start, GREY);
    const path = [start];

    while (stack.length > 0) {
      const frame = stack[stack.length - 1];
      const [node, children] = frame;
      const idx = frame[2];

      if (idx < children.length) {
        frame[2]++;
        const child = children[idx];
        const cc = colour.get(child) || WHITE;
        if (cc === GREY) {
          const ci = path.indexOf(child);
          if (ci >= 0) {
            const cycle = path.slice(ci).concat(child);
            const key = [...new Set(cycle)].sort().join('\0');
            if (!reported.has(key)) {
              reported.add(key);
              cycles.push(cycle);
            }
          }
        } else if (cc === WHITE) {
          colour.set(child, GREY);
          path.push(child);
          stack.push([child, [...(edges.get(child) || [])], 0]);
        }
      } else {
        stack.pop();
        path.pop();
        colour.set(node, BLACK);
      }
    }
  }
  return cycles;
}

function validateAcyclicity(data) {
  const errors = [];
  const practices = data.practices || [data];

  // Alpha contributesTo/mapsTo hierarchy
  const alphaParent = {};
  for (const p of practices) {
    for (const a of (p.alphas || [])) {
      const parent = a.contributesTo || a.mapsTo;
      if (parent) alphaParent[a.name] = parent;
    }
  }
  for (const cycle of detectChainCycles(k => alphaParent[k], Object.keys(alphaParent))) {
    errors.push(`Circular reference in Alpha hierarchy (contributesTo/mapsTo): ${cycle.join(' → ')}`);
  }

  // WorkProduct partOf
  const wpParent = {};
  for (const p of practices) {
    for (const wp of (p.workProducts || [])) {
      if (wp.partOf) wpParent[wp.name] = wp.partOf;
    }
  }
  for (const cycle of detectChainCycles(k => wpParent[k], Object.keys(wpParent))) {
    errors.push(`Circular reference in WorkProduct.partOf: ${cycle.join(' → ')}`);
  }

  // State.contributesToState
  const stateParent = new Map();
  for (const p of practices) {
    for (const a of (p.alphas || [])) {
      for (const s of (a.states || [])) {
        const cts = s.contributesToState;
        if (cts && cts.alphaName && cts.stateName) {
          stateParent.set(`${a.name}.${s.name}`, `${cts.alphaName}.${cts.stateName}`);
        }
      }
    }
  }
  for (const cycle of detectChainCycles(k => stateParent.get(k), stateParent.keys())) {
    errors.push(`Circular reference in State.contributesToState: ${cycle.join(' → ')}`);
  }

  // Background prerequisite graph
  const bgEdges = new Map();
  const bgNodes = new Set();

  function addBg(sourceKey, bg) {
    bgNodes.add(sourceKey);
    if (!bgEdges.has(sourceKey)) bgEdges.set(sourceKey, []);
    const targets = bgEdges.get(sourceKey);
    for (const r of (bg.alphaStates || [])) {
      if (r.alphaName && r.stateName) {
        const t = `alpha:${r.alphaName}.${r.stateName}`;
        targets.push(t);
        bgNodes.add(t);
      }
    }
    for (const r of (bg.workProductLevels || [])) {
      if (r.workProductName && r.levelOfDetailName) {
        const t = `wp:${r.workProductName}.${r.levelOfDetailName}`;
        targets.push(t);
        bgNodes.add(t);
      }
    }
  }

  for (const p of practices) {
    for (const a of (p.alphas || [])) {
      for (const s of (a.states || [])) {
        if (s.background) addBg(`alpha:${a.name}.${s.name}`, s.background);
      }
    }
    for (const wp of (p.workProducts || [])) {
      for (const lod of (wp.levelsOfDetail || [])) {
        if (lod.background) addBg(`wp:${wp.name}.${lod.name}`, lod.background);
      }
    }
  }

  for (const cycle of detectDAGCycles(bgNodes, bgEdges)) {
    errors.push(`Circular prerequisite dependency: ${cycle.join(' → ')}`);
  }

  // ChangeRequest.supersedes (Project documents)
  for (const projCycle of (data.cycles || [])) {
    const crParent = {};
    for (const cr of (projCycle.changeRequests || [])) {
      if (cr.supersedes) crParent[cr.name] = cr.supersedes;
    }
    for (const cycle of detectChainCycles(k => crParent[k], Object.keys(crParent))) {
      errors.push(`Circular reference in ChangeRequest.supersedes: ${cycle.join(' → ')}`);
    }
  }

  return errors;
}

let validate;
try {
  validate = ajv.compile(schema);
} catch (err) {
  console.error('Schema compilation error:', err.message);
  process.exit(1);
}

const valid = validate(data);
const acyclicityErrors = validateAcyclicity(data);

if (valid && acyclicityErrors.length === 0) {
  console.log('✓ JSON is valid against schema');
  process.exit(0);
} else {
  console.log('✗ JSON validation failed\n');

  let errorCount = 0;

  if (!valid) {
    console.log('SCHEMA ERRORS:');
    console.log('==============\n');

    validate.errors.forEach((err) => {
      errorCount++;
      console.log(`${errorCount}. ${err.instancePath || '(root)'}`);
      console.log(`   Issue: ${err.message}`);
      if (err.params) {
        console.log(`   Details: ${JSON.stringify(err.params)}`);
      }
      if (err.schemaPath) {
        console.log(`   Schema: ${err.schemaPath}`);
      }
      console.log();
    });
  }

  if (acyclicityErrors.length > 0) {
    console.log('ACYCLICITY ERRORS:');
    console.log('==================\n');

    acyclicityErrors.forEach((msg) => {
      errorCount++;
      console.log(`${errorCount}. ${msg}`);
      console.log();
    });
  }

  console.log(`Total errors: ${errorCount}`);
  process.exit(1);
}
