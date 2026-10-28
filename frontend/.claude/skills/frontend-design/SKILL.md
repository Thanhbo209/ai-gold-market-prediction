---
name: frontend-design
description: Enforces a consistent, sharp-edged, minimal frontend design system. Use whenever creating, implementing, refactoring, or reviewing frontend pages, components, layouts, forms, tables, cards, dashboards, or responsive UI.
---

# Frontend Design Skill

## 1. Design Philosophy

Build clean, professional, information-dense interfaces with a clear visual hierarchy.

Priorities:

1. Clarity and usability.
2. Consistent spacing and alignment.
3. Readable typography.
4. Strong hierarchy through layout, borders, and contrast.
5. Minimal decoration.
6. Reusable components and design tokens.

The UI should look like a carefully designed software product, not a generic template generated from a component library.

Do not add visual elements merely to make a page look more elaborate.

## 2. Strict Visual Rules

### Sharp corners only

- Never use rounded corners on UI elements.
- No `rounded`, `rounded-sm`, `rounded-md`, `rounded-lg`,
  `rounded-xl`, `rounded-full`, or equivalent border-radius utilities.
- Use `border-radius: 0` for cards, panels, buttons, inputs,
  dialogs, dropdowns, badges, tooltips, and images.
- Override third-party component defaults when necessary.
- Do not use pill-shaped buttons or badges.
- Circular elements are allowed only when functionally necessary,
  such as a chart marker or avatar.

### Minimal icons

- Prefer text labels over icons.
- Use icons only when they improve recognition or usability.
- Never add icons purely for decoration.
- Avoid placing an icon beside every heading, label, navigation item,
  table row, button, or statistic.
- Do not use emoji as UI icons.
- If an icon is necessary, use the project's existing icon library.
- Prefer simple, consistent, monochrome icons.
- Do not install an icon library just for one or two icons.

### No unnecessary decoration

Avoid:

- Decorative gradients.
- Glassmorphism and excessive blur.
- Neon effects and glowing borders.
- Excessive shadows.
- Large decorative background shapes.
- Unnecessary animations.
- Multiple competing accent colors.
- Cards nested inside other cards without a clear reason.
- Borders around every individual element.

Use whitespace, typography, alignment, and subtle borders to create hierarchy.

## 3. Layout and Containers

- Use a consistent spacing scale.
- Align page titles, content sections, tables, and charts to a shared grid.
- Prefer simple rectangular containers.
- Use borders to distinguish meaningful sections.
- Use background color changes sparingly to separate content areas.
- Avoid excessive nesting of `div`, `section`, and card components.
- Use semantic HTML where appropriate.
- Keep related content together and unrelated content separate.
- Use a consistent maximum content width where the page benefits from one.
- Do not add a card around content that already has sufficient hierarchy.

## 4. Cards and Panels

Cards and panels must have:

- Square corners.
- Consistent padding.
- Clear, concise headings when necessary.
- Minimal borders or subtle background separation.
- No decorative shadows by default.

Do not turn every piece of information into a separate card.

For dashboards, use cards only for information that benefits from independent grouping, such as key metrics or the latest prediction.

Avoid excessive whitespace inside compact data panels.

## 5. Typography

- Establish a clear hierarchy between page titles, section headings,
  labels, body text, and supporting metadata.
- Use a small, consistent type scale.
- Prefer readable text over decorative typography.
- Use font weight and size to establish hierarchy instead of adding icons
  or colorful labels.
- Use tabular numerals for prices, metrics, and aligned numeric data
  when supported by the chosen font.
- Keep labels concise.
- Avoid oversized headings that consume excessive dashboard space.
- Do not introduce additional fonts without a clear reason.

## 6. Colors and Theme

- Use design tokens or CSS variables for shared colors.
- Keep the palette restrained and consistent.
- Use neutral surfaces for the main layout.
- Reserve accent colors for primary actions and important information.
- Maintain sufficient text and border contrast.
- Do not communicate status through color alone; include a text label.
- Avoid hardcoding slightly different shades throughout individual components.
- Respect the existing theme if one has already been established.

For the gold-market dashboard, a restrained palette may use:

- Dark charcoal or neutral light surfaces.
- White or near-white content areas.
- Muted gray borders and secondary text.
- A restrained gold accent for market-specific emphasis.
- Green and red for upward and downward market direction.

Do not use all accent colors at once. Green and red should represent
meaningful market direction or status, not general decoration.

## 7. Buttons, Inputs, and Interactive Elements

- All buttons and inputs have square corners.
- Primary actions must be visually distinct without oversized styling.
- Secondary actions should be visually quieter.
- Destructive actions must be clearly identifiable.
- Inputs need visible labels, clear focus states, and useful validation messages.
- Never remove keyboard focus indicators without providing an accessible replacement.
- Use hover effects sparingly and consistently.
- Disabled states must be visibly distinguishable.
- Interactive elements must have appropriate accessible names.

## 8. Tables and Data-Dense UI

- Prefer semantic tables for genuinely tabular information.
- Align numeric values consistently.
- Use clear column headings.
- Keep row heights compact but readable.
- Use subtle horizontal dividers when they improve scanning.
- Avoid unnecessary vertical borders and decorative table backgrounds.
- Do not wrap every row or cell in a separate card.
- Provide loading, empty, error, and pagination states where applicable.
- Preserve legibility on smaller screens with appropriate overflow handling
  or an alternative responsive layout.

For prediction history, make dates, model names, directions, and numeric
values easy to scan.

## 9. Charts and Financial Data

- Charts must prioritize data readability.
- Avoid unnecessary chart backgrounds, borders, gradients, and shadows.
- Label axes and units where appropriate.
- Use consistent formatting for dates, prices, and percentages.
- Distinguish actual historical data from model predictions.
- Never fabricate market prices, confidence scores, accuracy metrics,
  or historical prediction results.
- Use green and red consistently for upward and downward directions.
- Provide text summaries or labels where color alone is insufficient.
- Include loading, error, and no-data states.

## 10. Responsive Design

- Design for mobile, tablet, and desktop.
- Do not simply shrink the desktop layout.
- Keep navigation usable at smaller widths.
- Allow data tables to scroll horizontally when appropriate.
- Prevent charts and panels from overflowing their containers.
- Preserve readable typography and adequate interactive target sizes.
- Avoid fixed widths that break common viewport sizes.

## 11. Component Architecture

- Reuse existing components and design tokens before creating alternatives.
- Keep components focused on a clear responsibility.
- Avoid duplicating styling across equivalent components.
- Do not introduce abstractions for one-off elements without a clear benefit.
- Follow the existing framework, folder structure, naming conventions,
  and package manager.
- Prefer the existing UI library if one has already been adopted.
- Do not install new dependencies without a concrete need.
- Keep data fetching and presentation responsibilities clear.
- Handle loading, errors, and empty states explicitly.

## 12. Accessibility

- Use semantic HTML.
- Associate form controls with labels.
- Maintain sufficient color contrast.
- Support keyboard navigation.
- Provide visible focus states.
- Give meaningful alternative text to informative images.
- Hide purely decorative visuals from assistive technology.
- Do not rely exclusively on color, hover, or icons to convey meaning.

## 13. Implementation Workflow

Before changing the UI:

1. Inspect the existing page, components, styles, and dependencies.
2. Identify existing design tokens and conventions.
3. Determine the smallest logical implementation step.
4. Reuse existing components when appropriate.

While implementing:

1. Make focused changes.
2. Follow the strict sharp-corner and minimal-icon rules.
3. Keep responsive behavior in mind.
4. Avoid unrelated refactoring.
5. Do not add placeholder metrics that could be mistaken for real data.

After implementing:

1. Run the relevant lint, type-check, and test commands.
2. Review the rendered UI when browser access is available.
3. Check spacing, alignment, responsiveness, and accessibility.
4. Search for accidental rounded-corner utilities.
5. Review the diff for unrelated changes.
6. Summarize what changed and list the checks performed.

## 14. Final Review Checklist

Before considering a UI task complete, verify:

- [ ] No unnecessary rounded corners.
- [ ] Icons are minimal and functional.
- [ ] No unnecessary gradients, shadows, or decoration.
- [ ] Spacing and typography are consistent.
- [ ] Cards and containers have a clear purpose.
- [ ] Colors follow the shared palette.
- [ ] Loading, error, and empty states are handled where relevant.
- [ ] Responsive behavior is considered.
- [ ] Accessibility basics are covered.
- [ ] No fabricated financial data or model metrics.
- [ ] Existing project conventions are respected.
- [ ] Relevant checks pass.
