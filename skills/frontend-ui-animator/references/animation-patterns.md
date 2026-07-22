# Animation Patterns

Concrete patterns by priority area. All patterns animate only `transform`, `opacity`, and `filter`.

## 1. Hero Intro

Staggered fade-slide on load:

```css
@keyframes fade-slide-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

```tsx
<h1 className="animate-fade-slide-in" style={{ animationDelay: '0ms' }} />
<p className="animate-fade-slide-in" style={{ animationDelay: '150ms' }} />
<div className="animate-fade-slide-in" style={{ animationDelay: '300ms' }} />
```

Guidelines: 400–700ms duration, `ease-out`, stagger 100–150ms per element, max ~4 staggered elements.

## 2. Hover Interactions

```tsx
// Lift + shadow
<div className="transition-all duration-200 hover:-translate-y-1 hover:shadow-lg" />

// Scale (buttons, cards)
<button className="transition-transform duration-150 hover:scale-105 active:scale-95" />

// Underline reveal (links)
<a className="relative after:absolute after:bottom-0 after:left-0 after:h-px after:w-0 after:bg-current after:transition-all after:duration-200 hover:after:w-full" />
```

Guidelines: 150–250ms, subtle displacement (2–4px lift, 1.02–1.05 scale). Always pair `hover:` with matching `transition-*` utilities.

## 3. Content Reveal (Scroll)

Use `useScrollReveal` (see SKILL.md) with a one-time trigger — do not re-hide on scroll out:

```tsx
const { ref, isVisible } = useScrollReveal(0.15);
<section ref={ref} className={isVisible ? 'animate-fade-slide-in' : 'opacity-0'} />
```

Guidelines: threshold 0.1–0.2, reveal once, keep initial `opacity-0` on the same element so there is no flash.

## 4. Background Effects

```tsx
// Slow ambient gradient drift
@keyframes gradient-drift {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-2%, 2%); }
}
// duration: 15s+, ease-in-out, infinite
```

Guidelines: very slow (10s+), low opacity, `pointer-events-none`, never distract from content.

## 5. Navigation Transitions

- Page transitions: fade + slight translate (200–300ms out, 300–400ms in).
- Mobile menu: slide from edge with backdrop fade.
- Active-link indicator: animated with `layoutId` (Framer Motion) or transform-based sliding underline.

## Anti-Patterns

- Animating `width`, `height`, `margin`, `padding`, `top/left` (layout thrash → use transforms)
- Animations longer than 700ms on interactive elements
- Scroll-jacking or parallax that fights native scroll
- Auto-playing looping motion near body text
- Re-triggering reveal animations on every scroll pass
