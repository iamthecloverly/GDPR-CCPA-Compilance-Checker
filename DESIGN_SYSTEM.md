# GDPR/CCPA Compliance Checker - Design System

## 1. Design Philosophy

**Core Principles:**
- **Minimalist Elegance**: Clean, uncluttered interface with purposeful whitespace
- **Transparency & Trust**: Glass-morphic effects convey security and clarity
- **Progressive Disclosure**: Show what's relevant, hide complexity
- **Accessibility First**: WCAG 2.1 AA compliance throughout
- **Performance**: Smooth interactions, minimal bloat

---

## 2. Color Palette

### Primary Colors
| Color | Hex | Usage | RGB |
|-------|-----|-------|-----|
| **Cyan** | `#06b6d4` | Primary actions, links | 6, 182, 212 |
| **Sky Blue** | `#0ea5e9` | Hover states, accents | 14, 165, 233 |
| **Slate** | `#1e293b` | Text, dark elements | 30, 41, 59 |

### Secondary Colors - Status Indicators
| Status | Color | Hex | Usage |
|--------|-------|-----|-------|
| **Excellent** | Green | `#10b981` | Grade A, Pass |
| **Good** | Teal | `#06b6d4` | Grade B, Compliant |
| **Moderate** | Amber | `#f59e0b` | Grade C, Warning |
| **Poor** | Orange | `#f97316` | Grade D, Alert |
| **Critical** | Red | `#ef4444` | Grade F, Fail |

### Neutral Palette
| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| **Background** | White | `#ffffff` | Main surface |
| **Secondary BG** | Slate 50 | `#f8fafc` | Card backgrounds |
| **Tertiary BG** | Slate 100 | `#f1f5f9` | Hover, active states |
| **Border** | Slate 200 | `#e2e8f0` | Dividers, borders |
| **Text Primary** | Slate 900 | `#0f172a` | Headings, primary text |
| **Text Secondary** | Slate 600 | `#475569` | Body text, secondary |
| **Text Tertiary** | Slate 500 | `#64748b` | Hints, captions |

### Semantic Colors
```css
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-info: #3b82f6;
--color-premium: #8b5cf6; (Purple for AI features)
```

---

## 3. Typography System

### Font Stack
```css
--font-display: 'Geist Display', -apple-system, BlinkMacSystemFont, sans-serif;
--font-body: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'Geist Mono', 'JetBrains Mono', monospace;
```

### Type Scale
| Usage | Size | Weight | Line Height | Letter Spacing |
|-------|------|--------|-------------|-----------------|
| **Display** (H1) | 42px | 700 | 1.2 | -0.02em |
| **Heading 1** (H2) | 32px | 700 | 1.3 | -0.015em |
| **Heading 2** (H3) | 24px | 600 | 1.4 | -0.01em |
| **Heading 3** (H4) | 20px | 600 | 1.4 | 0 |
| **Subheading** (H5) | 16px | 600 | 1.5 | 0 |
| **Body Large** | 16px | 400 | 1.6 | 0 |
| **Body** | 14px | 400 | 1.5 | 0 |
| **Body Small** | 13px | 400 | 1.5 | 0 |
| **Caption** | 12px | 500 | 1.4 | 0.02em |
| **Code** | 13px | 400 | 1.5 | 0 |

---

## 4. Spacing System

### Modular Scale (4px base)
```css
--space-0: 0;
--space-1: 4px;   /* xs */
--space-2: 8px;   /* sm */
--space-3: 12px;  /* md */
--space-4: 16px;  /* lg */
--space-6: 24px;  /* xl */
--space-8: 32px;  /* 2xl */
--space-10: 40px; /* 3xl */
--space-12: 48px; /* 4xl */
```

### Usage Guidelines
- **Component Padding**: 16px (internal content)
- **Section Spacing**: 24-32px (between major sections)
- **Card Spacing**: 8px (card gaps)
- **Text Spacing**: 8-16px (above/below text blocks)

---

## 5. Border & Radius System

### Border Radius
| Size | Value | Usage |
|------|-------|-------|
| **None** | 0px | Sharp corners |
| **Small** | 4px | Small components, inputs |
| **Default** | 8px | Cards, buttons, modals |
| **Large** | 12px | Large cards, panels |
| **Full** | 9999px | Pills, badges, avatars |

### Border Styles
```css
--border-thin: 1px solid var(--color-border);
--border-medium: 2px solid var(--color-border);
--border-glass: 1px solid rgba(255, 255, 255, 0.2);
```

---

## 6. Shadow & Elevation System

### Elevation Levels
```css
/* Subtle depth */
--shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);

/* Default cards */
--shadow-md: 0 4px 6px rgba(15, 23, 42, 0.07),
             0 2px 4px rgba(15, 23, 42, 0.05);

/* Elevated components */
--shadow-lg: 0 10px 15px rgba(15, 23, 42, 0.1),
             0 4px 6px rgba(15, 23, 42, 0.05);

/* Modals, overlays */
--shadow-xl: 0 20px 25px rgba(15, 23, 42, 0.15),
             0 10px 10px rgba(15, 23, 42, 0.05);

/* Focus states */
--shadow-focus: 0 0 0 3px rgba(6, 182, 212, 0.1);
```

---

## 7. Component Specifications

### Buttons

**Primary Button**
```css
Background: var(--color-primary);
Text: White;
Padding: 12px 20px;
Border-radius: 8px;
Font-weight: 600;
Font-size: 14px;
Transition: all 0.2s ease;

States:
- Hover: Darker shade, shadow-lg
- Active: Darker shade, shadow-sm
- Disabled: Opacity 0.5, cursor not-allowed
- Loading: Spinner animation
```

**Secondary Button**
```css
Background: var(--color-secondary-bg);
Border: 1px solid var(--color-border);
Text: var(--color-text-primary);
Padding: 12px 20px;
Border-radius: 8px;
Font-weight: 600;
```

**Ghost Button**
```css
Background: transparent;
Text: var(--color-primary);
Border: none;
Padding: 12px 20px;
Font-weight: 500;

Hover: Background var(--color-secondary-bg);
```

### Form Inputs

**Text Input**
```css
Background: #ffffff;
Border: 1px solid var(--color-border);
Border-radius: 8px;
Padding: 12px 14px;
Font-size: 14px;
Transition: border-color 0.2s ease;

States:
- Focus: Border var(--color-primary), shadow-focus
- Error: Border var(--color-error), red text
- Disabled: Background var(--color-tertiary-bg), opacity 0.5
- Placeholder: var(--color-text-tertiary)
```

### Cards

**Standard Card**
```css
Background: #ffffff;
Border: 1px solid var(--color-border);
Border-radius: 12px;
Padding: 24px;
Box-shadow: var(--shadow-md);
Transition: shadow 0.3s ease;

Hover: shadow-lg
```

**Glass Card** (Modern Look)
```css
Background: rgba(255, 255, 255, 0.7) with backdrop-filter: blur(10px);
Border: 1px solid rgba(255, 255, 255, 0.2);
Box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
Border-radius: 12px;
```

### Badges

**Status Badge**
```
.badge {
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.badge-success: background #d1fae5; color #047857;
.badge-warning: background #fef3c7; color #d97706;
.badge-error: background #fee2e2; color #dc2626;
.badge-info: background #dbeafe; color #0284c7;
```

---

## 8. Glass Morphism Effects

**Glass Surface**
```css
Background: rgba(255, 255, 255, 0.7);
Backdrop-filter: blur(10px);
Border: 1px solid rgba(255, 255, 255, 0.2);
Box-shadow: 
  inset 0 0 0 0.5px rgba(255, 255, 255, 0.3),
  0 8px 32px rgba(31, 38, 135, 0.1);
Border-radius: 12px;
```

**Frosted Glass (Darker)**
```css
Background: rgba(248, 250, 252, 0.8);
Backdrop-filter: blur(8px);
Border: 1px solid rgba(15, 23, 42, 0.1);
```

---

## 9. Animations & Transitions

### Timing Functions
```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0.0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Standard Durations
- **Instant**: 100ms (quick feedback)
- **Fast**: 200ms (button hovers, toggles)
- **Normal**: 300ms (page transitions)
- **Slow**: 500ms (modal opens)

### Key Animations
```css
/* Fade in */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide up */
@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Pulse (loading indicator) */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Spin (progress indicator) */
@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## 10. Layout System

### Grid Layout
```css
--container-2xs: 320px;
--container-xs: 384px;
--container-sm: 448px;
--container-md: 512px;
--container-lg: 640px;
--container-xl: 768px;
--container-2xl: 896px;
--container-3xl: 1024px;
--container-4xl: 1152px;
--container-5xl: 1280px;
```

### Responsive Breakpoints
```css
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: 1024px - 1536px
Large Desktop: > 1536px
```

---

## 11. Icon System

### Icon Guidelines
- **Size**: 16px (small), 20px (default), 24px (large), 32px (extra large)
- **Stroke Width**: 2px for consistency
- **Style**: Outline style (not filled) for consistency
- **Color**: Inherit from text color or use semantic colors
- **Padding**: 4px internal padding for touch targets

### Icon Usage
```
Navigation: home, chevron, menu, x, search, settings
Status: check-circle, alert-circle, info, checkmark, x
Actions: plus, minus, trash, edit, download, share
Utilities: external-link, copy, eye, eye-off
```

---

## 12. Accessibility Standards

### Color Contrast
- **Normal Text**: 4.5:1 minimum ratio
- **Large Text**: 3:1 minimum ratio
- **Graphics**: 3:1 minimum ratio

### Touch Targets
- **Minimum Size**: 44x44px (mobile), 40x40px (desktop)
- **Spacing**: 8px minimum between targets

### Focus States
- **Visible Outline**: 3px solid `var(--color-primary)`
- **Offset**: 2px from element boundary
- **Applied to**: All interactive elements

### ARIA Labels
- All icon buttons: `aria-label`
- Form inputs: `<label>` elements
- Status updates: `aria-live` regions
- Error messages: `aria-describedby`

---

## 13. Dark Mode (Future Enhancement)

### Dark Color Palette
```css
--color-primary-dark: #06b6d4;
--color-bg-dark: #0f172a;
--color-surface-dark: #1e293b;
--color-border-dark: #334155;
--color-text-dark-primary: #f8fafc;
--color-text-dark-secondary: #cbd5e1;
```

---

## 14. Component Library Structure

```
components/
├── UI/
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   ├── Badge.tsx
│   ├── Modal.tsx
│   ├── Tabs.tsx
│   └── Spinner.tsx
├── Layout/
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── Container.tsx
│   └── Grid.tsx
├── Panels/
│   ├── ScanPanel.tsx
│   ├── ResultsPanel.tsx
│   ├── AnalyticsPanel.tsx
│   └── HistoryPanel.tsx
└── Icons/
    ├── ScanIcon.tsx
    ├── CheckIcon.tsx
    ├── etc.
```

---

## 15. Implementation Guidelines

### CSS Architecture
```
1. CSS Variables (root)
2. Base tags (html, body)
3. Utilities (spacing, text, etc.)
4. Components (cards, buttons, etc.)
5. Layouts (header, sidebar, etc.)
6. Pages (specific overrides)
```

### Best Practices
- Use CSS variables for theming
- Implement mobile-first approach
- Use semantic HTML
- Include proper ARIA labels
- Test with keyboard navigation
- Test with screen readers
- Optimize images and SVGs
- Implement lazy loading where needed

---

## 16. Branding Integration

### Logo Placement
- **Header**: 32x32px, left-aligned in top navigation
- **Favicon**: 16x16px, simplified mark

### Brand Voice
- **Professional yet approachable**
- **Technical accuracy with clear language**
- **Trustworthy and secure**
- **Efficient and helpful**

### Visual Identity
- Primary color: Cyan (#06b6d4) - Trust, clarity, security
- Modern, clean aesthetic - Professional, reliable
- Minimalist approach - Focuses on content and user goals

---

## 17. Performance Considerations

### CSS Optimization
- Minify production CSS
- Use CSS containment for isolated components
- Avoid expensive selectors
- Implement critical CSS inline

### Animation Performance
- Use `transform` and `opacity` for animations
- Leverage GPU acceleration
- Reduce motion on media query support
- Keep animations under 300ms for interactions

### Loading States
- Show skeleton screens for data loading
- Use progress indicators for long operations
- Provide visual feedback for all actions
- Disable interactions during loading

---

## 18. Browser Support

**Target Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Feature Support:**
- Modern CSS (CSS Grid, Flexbox)
- CSS Variables
- Backdrop Filter (with fallbacks)
- Transform & Transition
- SVG Support

---

## 19. Responsive Design Specifications

### Mobile (< 640px)
- Single column layout
- Full-width cards and inputs
- Larger touch targets (48px minimum)
- Reduced padding and margins
- Bottom navigation (when needed)

### Tablet (640px - 1024px)
- Two column layout
- Sidebar navigation collapsible
- Wider components
- Optimized spacing

### Desktop (1024px+)
- Full three-column layout (sidebar, main, panel)
- Rich visualizations
- Comprehensive information display
- Hover states and tooltips enabled

---

## 20. Quality Checklist

- [ ] All colors meet WCAG AAA contrast
- [ ] All interactive elements 44x44px minimum
- [ ] All icons have labels or aria-label
- [ ] All forms have associated labels
- [ ] Focus states visible on all elements
- [ ] Touch targets have minimum 8px spacing
- [ ] Animations respect prefers-reduced-motion
- [ ] Images have alt text
- [ ] External links open in new tabs with indicators
- [ ] Error messages are clear and actionable
- [ ] Success states are clearly communicated
- [ ] Loading states are visible
- [ ] No information conveyed by color alone
- [ ] Keyboard navigation fully supported
- [ ] Tested with at least one screen reader
