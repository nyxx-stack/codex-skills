# Tailwind Presets

Drop-in keyframes and animation utilities for `tailwind.config.ts`.

```ts
// tailwind.config.ts
export default {
  theme: {
    extend: {
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'fade-slide-in': {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-slide-in-left': {
          from: { opacity: '0', transform: 'translateX(-20px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        'blur-in': {
          from: { opacity: '0', filter: 'blur(4px)' },
          to: { opacity: '1', filter: 'blur(0)' },
        },
        'gradient-drift': {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '50%': { transform: 'translate(-2%, 2%)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out both',
        'fade-slide-in': 'fade-slide-in 0.6s ease-out both',
        'fade-slide-in-left': 'fade-slide-in-left 0.6s ease-out both',
        'scale-in': 'scale-in 0.4s ease-out both',
        'blur-in': 'blur-in 0.6s ease-out both',
        'gradient-drift': 'gradient-drift 18s ease-in-out infinite',
      },
    },
  },
}
```

Notes:

- `both` fill mode keeps elements hidden before delayed animations start (pairs with `animationDelay` stagger).
- For CSS-first Tailwind v4 setups, declare the same keyframes in `@theme` inside your global CSS instead.

Global reduced-motion override (required, in global CSS):

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
```
