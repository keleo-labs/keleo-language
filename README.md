# Keleo Practice Language

The Practice Language JSON Schema is a meta-model for describing practices, methods, baselines and projects, translating abstract engineering and methodology concepts into machine-readable, operational constructs. Influenced by the [SEMAT Essence](https://www.omg.org/spec/Essence/) language and adapted for JSON, it defines a structural hierarchy of elements — alphas, states, work products, activities, personas and patterns — held together by ontological constraints that keep the parts semantically coherent and composable. Evidence-based state progression, hierarchical alpha dependencies, orthogonal tagging taxonomies and narrative frameworks make the schema a prescriptive operational engine rather than a descriptive taxonomy, and it drives methodology enactment in any domain.

## Schema

The schema is defined in [`language.schema.json`](language.schema.json) using JSON Schema Draft 2020-12. Semantic guidance and operational architecture are documented in [`references/semantics.md`](references/semantics.md).

Schema **4.0.0** requires persistent UUID project identity and adds explicit project
ownership, reporting, delegation templates and inherited reporting requirements.
Read the [migration guide](references/semantics/project-hierarchy.md#migration-from-schema-3)
before upgrading consumers. The project validator accepts catalogue snapshots,
report results and creation previews without applying writes.

## What the language is

An ontology, in the sense Tom Gruber gave the word, is [a formal specification of a shared conceptualization](https://tomgruber.org/writing/ontolingua-kaj-1993/). That is what this schema is for working practice. A domain agrees on what it cares about, and the language writes that agreement down in a form software can check.

The shape is the familiar one of entities, relationships and properties. **Alphas** are the entities — the things a domain is concerned about, like a platform, a requirement or a customer relationship. `contributesTo`, `mapsTo` and `relatesTo` are the relationships between them. **States**, and the checklists that make each state assessable, are the properties that say where an alpha has got to.

The consequence is that methodology stops being documentation and becomes data. A practice expressed this way can be validated, merged with another practice, compared against a rival approach, and composed into a method — by software, without a human rereading the prose each time.

## Constraints and inference

A graph of entities and relationships does not, on its own, tell you when something is wrong. In the semantic web stack that job falls to vocabularies that sit beside the graph: [RDF Schema](https://www.w3.org/TR/rdf-schema/) supplies domain and range, and [OWL 2](https://www.w3.org/TR/owl2-primer/) supplies cardinality, disjointness and transitivity. The Practice Language does the equivalent work inside one document, through the schema and the rules in [`references/semantics/`](references/semantics).

The parallels are close enough to be worth naming, though this is an analogy rather than an RDF implementation:

| Semantic web construct | Practice Language equivalent |
|---|---|
| Domain and range on a property | `direction` is required on every `relatesTo` entry — `outgoing`, `incoming` or `mutual` |
| Functional property (at most one value) | `partOf` and `mapsTo` are each 0..1 on a work product; a practice has one primary alpha |
| Disjoint classes | An alpha is a concern, a work product is information *about* a concern, and the two never collapse into each other; the same separation holds between competencies and personas |
| Irreflexivity | `partOf` and `mapsTo` may coexist on one work product, but they must point at different targets |
| Value constraints on a property | States are enumerated per alpha, and every symbolic reference is an exact, case-sensitive match against a declared name |
| Cycles in a transitive relation | `contributesTo`, `partOf` and persona group membership must form a directed acyclic graph — see [`references/semantics/acyclicity.md`](references/semantics/acyclicity.md) |

These constraints are what make a generated practice falsifiable. A document can be schema-valid and still semantically wrong, which is why the validators below check both layers.

## Using the language with agents

Large language models are probabilistic. They produce plausible text, and plausible is not the same as admissible — hallucination is a property of how the models work rather than a defect waiting to be patched, so the correction has to come from outside the model. Frank Coyle makes this case for agentic systems generally in [Why agentic systems need ontologies](https://www.youtube.com/watch?v=Sir59K8ZDPU), and the pairing of neural generation with symbolic knowledge is an active research direction in its own right ([Garcez & Lamb, 2023](https://doi.org/10.1007/s10462-023-10448-w)). Grounding generated output in a structured knowledge representation is one of the better-studied mitigations ([Agrawal et al., 2024](https://aclanthology.org/2024.naacl-long.219/)).

If you are generating practice content with an agent, check it in two layers. Validate the structure at the door, against the JSON Schema, and then validate the meaning at the ledger, against the semantic rules the schema cannot express. Withhold the side effect — writing the file, packaging the bundle, publishing to a library — until both pass, and hand control back to a person when the second layer fails.

[keleo-pgen-llm](https://github.com/keleo-labs/keleo-pgen-llm) implements exactly this. Its generation pipeline ends every phase with mechanical validation, then a verification gate whose agents reread the source material and establish that the output traces back to it, then a human review gate. The protocol is written up in [`VERIFY-FOUNDATION.md`](https://github.com/keleo-labs/keleo-pgen-llm/blob/main/.claude/skills/verification-foundation/VERIFY-FOUNDATION.md).

## Tooling

- **[keleo-pgen-llm](https://github.com/keleo-labs/keleo-pgen-llm)** — Generate new practices using LLM-driven Claude skills
- **[keleo-studio](https://github.com/keleo-labs/keleo-studio)** — Manage, update and visualise practices

## Validation

### Schema validation (Node.js)

```bash
npm install
node validate/validate-schema.js <file.json>
```

### Practice and baseline validation (Python)

Run the validator that matches the document kind:

```bash
python3 validate/validate-practice.py <practice.json> <baseline.json> language.schema.json
python3 validate/validate-baseline.py <baseline.json> language.schema.json
python3 validate/validate-project.py <project.json> language.schema.json
python3 validate/validate-integration-mapping.py <mapping.json> language.schema.json
```

No install step is needed. The validators import `jsonschema`, and on first run they build a virtual environment for it and re-exec into it. There is nothing to activate and no interpreter path to remember.

This matters because the obvious instruction no longer works: Debian, Ubuntu, Fedora and Homebrew all mark their Python externally managed under [PEP 668](https://peps.python.org/pep-0668/), so a bare `pip install jsonschema` fails with `externally-managed-environment`. The escapes from that error — `--break-system-packages`, `--user`, `sudo pip` — work by damaging the interpreter other software depends on.

The environment is created at `${XDG_DATA_HOME:-~/.local/share}/agent-skills/keleo-validate/venv`, outside this repository, so a clean checkout does not destroy it. Delete that directory to force a rebuild.

On Debian and Ubuntu, `python3 -m venv` lives in a separate `python3-venv` package; its absence is the most common first-run failure, and the validators name it if the environment cannot be created.

## References

- Coyle, F. (n.d.). *Why agentic systems need ontologies* [Video]. https://www.youtube.com/watch?v=Sir59K8ZDPU
- Gruber, T. R. (1993). A translation approach to portable ontology specifications. *Knowledge Acquisition, 5*(2), 199–220. https://doi.org/10.1006/knac.1993.1008
- Garcez, A. d'Avila, & Lamb, L. C. (2023). Neurosymbolic AI: the 3rd wave. *Artificial Intelligence Review, 56*, 12387–12406. https://doi.org/10.1007/s10462-023-10448-w
- Agrawal, G., Kumarage, T., Alghamdi, Z., & Liu, H. (2024). Can knowledge graphs reduce hallucinations in LLMs? A survey. *NAACL 2024*, 3947–3960. https://aclanthology.org/2024.naacl-long.219/
- Object Management Group. (n.d.). *Essence — kernel and language for software engineering methods*. https://www.omg.org/spec/Essence/
- W3C. (2014). *RDF Schema 1.1*. https://www.w3.org/TR/rdf-schema/
- W3C. (2012). *OWL 2 web ontology language primer*. https://www.w3.org/TR/owl2-primer/

## License

This work is licensed under [CC BY 4.0](LICENSE).
