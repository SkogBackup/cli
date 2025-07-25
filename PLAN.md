# skogai config system architectural design

## understanding: this is a live computational ontology where:
  - [@action:param] executes actual code/scripts  
  - $ definitions create dependency resolution chains
  - the config system stores the executable semantics of your type theory
  - actions can be parameterized, chained, and execute external scripts
  - the system is self-hosting - definitions define themselves

## core design decision: should the semantic universe support compositional structure?

### current state: 
  - $.claude.hello = atomic definition (resolves to action)
  - setting $.claude.hello.greeting crashes because parent is string, not object
  - need to decide: atomic definitions vs. compositional namespaces

## plan:
  1. design compositional semantics: define when definitions can have sub-structure
  2. implement hybrid entity support: allow entities to be both terminal values and structural containers
  3. create path-type resolution: support $.parent.child as dependent type paths
  4. preserve execution chains: ensure action resolution still works through nested structures
  5. update parsing stages: handle nested keys across the 4-stage architecture
  6. test with live actions: verify [@hello:claude] and script execution work with new structure

## desired result: a config system that supports your dependent type theory while maintaining the live execution environment for skogai notation.
