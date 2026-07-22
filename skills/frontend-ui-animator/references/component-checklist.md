# Component Checklist — Animation Audit Template

Output of Phase 1 (Analyze). Fill one row per animation candidate.

## Audit Table

| Component | Page/Route | Priority Area | Current State | Proposed Animation | Trigger | Effort |
|---|---|---|---|---|---|---|
| Hero | `/` | 1 Hero Intro | none | staggered fade-slide-in | load | Low |
| FeatureCard | `/` | 2 Hover | none | lift + shadow | hover | Low |
| TestimonialSection | `/` | 3 Content Reveal | none | scroll fade-in | scroll | Medium |

Legend:
- **Priority Area**: 1 Hero Intro, 2 Hover, 3 Content Reveal, 4 Background, 5 Navigation
- **Effort**: Low (CSS/Tailwind only), Medium (hook needed), High (library required)

## Pre-Implementation Checklist

- [ ] `tailwind.config.ts` reviewed for existing keyframes/animations
- [ ] Animation libraries inventoried (framer-motion, GSAP, react-intersection-observer)
- [ ] Reduced-motion global CSS present or planned
- [ ] Candidates sorted by priority area, quick wins first

## Verification Checklist (Phase 4)

- [ ] All animations visually QA'd in browser
- [ ] `prefers-reduced-motion: reduce` tested (DevTools → Rendering → Emulate)
- [ ] No CLS introduced (Lighthouse or DevTools performance panel)
- [ ] No jank on scroll (60fps during reveal animations)
- [ ] No animation on layout properties (width/height/margin)
