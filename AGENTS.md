## Repository-Wide Engineering Rules

### Instructions and Skills

- Read and follow this `AGENTS.md` before making changes.
- Identify and follow relevant project skills before implementation.
- For frontend UI implementation, refactoring, or review, follow `frontend/.claude/skills/frontend-design/SKILL.md` when applicable.

### Framework Documentation

- Before writing or modifying Next.js code, read the relevant documentation under `frontend/node_modules/next/dist/docs/`.
- Follow the documentation for the installed Next.js version rather than relying on remembered APIs or conventions.
- Pay attention to breaking changes, deprecated APIs, and recommended alternatives.
- Preserve the generated Next.js agent-rules block below. Do not manually rewrite or remove it.

### Development Workflow

- Work in small, reviewable steps rather than implementing multiple unrelated changes at once.
- After each logical change, run the relevant tests, lint checks, and type checks.
- Review `git diff` before committing.
- Use a separate, descriptive commit for each logical change.
- Do not commit unrelated changes or generated files unless required by the project.

## TypeScript and Code Quality

### Type Safety

- Use TypeScript's strict mode. Do not weaken compiler settings to bypass errors.
- Prefer explicit, meaningful types for public APIs, function parameters, return values, and shared data structures.
- Let TypeScript infer obvious local variable types instead of adding redundant annotations.
- Never use `any` to bypass type checking. Prefer `unknown` and narrow the type safely.
- Avoid unsafe type assertions (`as`) and non-null assertions (`!`). Use them only when necessary and explain why.
- Do not use `@ts-ignore`. Use `@ts-expect-error` only when an intentional, documented type error must be tested or temporarily tolerated.
- Handle `null` and `undefined` explicitly where applicable.
- Use discriminated unions for values with distinct states rather than loosely related optional properties.
- Use `satisfies` when validating an object's shape while preserving its inferred type.

### Data Modeling

- Define reusable types and interfaces for shared domain concepts.
- Prefer `type` for unions, intersections, and aliases; use `interface` when declaration merging or extensible object contracts are useful.
- Avoid duplicating types across modules. Reuse or derive them where appropriate.
- Use utility types such as `Pick`, `Omit`, `Partial`, and `Record` when they accurately represent the intended data shape.
- Do not use `Partial<T>` as a shortcut when a specific update or patch contract is required.
- Keep API request types, response types, and internal domain types distinct when their responsibilities differ.
- Treat external data, API responses, environment variables, and user input as untrusted until validated.
- Use runtime validation at external boundaries when appropriate; TypeScript types alone do not validate runtime data.

### Functions and Control Flow

- Keep functions focused on one responsibility.
- Add explicit return types to exported functions when they improve API clarity or prevent unintended type changes.
- Prefer early returns and clear control flow over deeply nested conditions.
- Avoid unnecessary type complexity, generic abstractions, and premature generalization.
- Use exhaustive checks for discriminated unions when all cases must be handled.

### Naming and Readability

- Use `PascalCase` for types, interfaces, classes, and React components.
- Use `camelCase` for variables, functions, methods, and properties.
- Use descriptive names that communicate intent; avoid unexplained abbreviations.
- Use `UPPER_SNAKE_CASE` for true module-level constants when it improves clarity, not for every variable declared with `const`.
- Avoid boolean names that obscure meaning; prefer names such as `isLoading`, `hasError`, and `canSubmit`.

### Async and Error Handling

- Use `async`/`await` for readable asynchronous control flow.
- Handle rejected promises and errors at the appropriate boundary.
- Do not silently swallow errors or use empty catch blocks.
- Avoid floating promises; await them, return them, or explicitly handle them.
- Use `Promise<T>` return types where they clarify an asynchronous public API.
- Preserve useful error context without exposing secrets or sensitive data.

### React and Next.js

- Follow the installed Next.js documentation and the project's frontend skills.
- Avoid `any` for component props, event handlers, hooks, and API data.
- Define shared component prop types when they improve clarity or reuse.
- Do not add unnecessary client components; follow the installed Next.js conventions for server and client boundaries.
- Keep server-only code and secrets out of client bundles.
- Avoid duplicating state that can be derived from existing props or state.
- Clean up effects and subscriptions when required; do not use effects for values that can be calculated during rendering.

### Code Quality Verification

- Run the relevant linter, formatter, type checker, and tests after changes.
- Fix errors introduced by the change rather than suppressing them.
- Review the diff for unsafe assertions, accidental `any`, duplicated types, and unrelated modifications.
- Do not claim checks passed unless they were actually run.
