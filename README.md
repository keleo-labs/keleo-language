# Keleo Practice Language

The Practice Language JSON Schema is a meta-model for describing practices, methods, and baselines, translating abstract engineering and methodology concepts into machine-readable, operational constructs. Influenced by the [SEMAT Essence](https://www.omg.org/spec/Essence/) language and adapted for JSON, it defines a structural hierarchy of elements — alphas, states, work products, activities, personas, and patterns — grounded in rigorous ontological principles to ensure semantic coherence and composability. By enforcing evidence-based state progression, hierarchical alpha dependencies, orthogonal tagging taxonomies, and narrative storytelling frameworks, the schema functions as a prescriptive operational engine capable of driving methodology enactment across any domain.

## Schema

The schema is defined in [`language.schema.json`](language.schema.json) using JSON Schema Draft 2020-12. Semantic guidance and operational architecture are documented in [`references/semantics.md`](references/semantics.md).

## Tooling

- **[keleo-pgen-llm](https://github.com/keleo/keleo-pgen-llm)** — Generate new practices using LLM-driven Claude skills
- **[keleo-studio](https://github.com/keleo/keleo-studio)** — Manage, update, and visualize practices

## Validation

### Schema validation (Node.js)

```bash
npm install
node validate/validate-schema.js <file.json>
```

### Practice validation (Python)

```bash
pip install jsonschema
python3 validate/validate-practice.py <practice.json> <baseline.json> language.schema.json
```

### Baseline validation (Python)

```bash
python3 validate/validate-baseline.py <baseline.json> language.schema.json
```

## License

This work is licensed under [CC BY 4.0](LICENSE).
