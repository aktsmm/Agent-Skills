# Archetype: doc

A vertical-scroll explainer with a sticky sidebar and numbered citations. Start from `assets/skeletons/doc-skeleton.html`.

This is the shape to reach for when the reader will study the material rather than watch it: comparisons, decision write-ups, customer-facing explainers.

## Structure

```html
<nav>
  <p class="shf-brand">Title<span>subtitle</span></p>
  <ol>
    <li><a href="#overview" data-shf-navlink="overview">概要</a></li>
  </ol>
</nav>
<main>
  <header class="shf-hero">...</header>
  <section id="overview">...</section>
  <section id="sources">...</section>
</main>
```

Every nav link's `data-shf-navlink` must equal the `id` of the section it points at, and its `href` is the matching fragment. The runtime observes the sections and marks the active link with `aria-current` and `.is-current`. A mismatch is silent — the highlight just never moves — so check the pairs when you add a section.

Section `id` values are the edit handles. Keep them stable.

## Citations

Two halves that must agree.

In the body:

```html
<a class="shf-refmark" href="#ref-1" data-citation-id="c1">1</a>
```

In the sources section:

```html
<ol class="shf-cites">
  <li id="ref-1">
    <span class="shf-cite-title">Title</span
    ><span class="shf-cite-url">https://example.com/</span>
  </li>
</ol>
```

The list numbers itself with a CSS counter, so the visible number comes from document order. Keep the refmark text matching that order, or the reader sees `[3]` jump to the first entry.

`:target` highlights the entry after a jump, which is what tells the reader they landed in the right place.

Give each citation its own `data-citation-id` even when two point at the same URL, so a later edit can tell them apart.

## Responsive behaviour

Below 850px the sidebar stops being sticky and the nav becomes a two-column list, and the multi-column blocks collapse to one. Nothing is hidden. Check this width if the document will be read on a phone.

## Printing

The sidebar is dropped and sections avoid breaking across pages. This is the archetype that prints well; a deck does not.

## Common mistakes

- A nav entry whose `data-shf-navlink` does not match any section `id`.
- Citations in the body that have no entry in the list, or entries nobody cites. Both pass Tier 1 today, so read them.
- Walls of text. The component blocks in `component-patterns.md` exist so the eye has somewhere to rest.
