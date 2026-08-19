---
name: SickleSense
description: Evidence-backed answers for sickle cell disease, clearly cited.
colors:
  ink: "#19303a"
  muted: "#62747d"
  content-surface: "#ffffff"
  navigation-surface: "#f5f8fa"
  primary-teal: "#0f7d77"
  primary-deep: "#075d5a"
  pale-teal: "#e7f3f1"
  divider: "#dbe5e8"
typography:
  display:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "clamp(2.7rem, 6.5vw, 4.875rem)"
    fontWeight: 600
    lineHeight: 0.99
    letterSpacing: "-0.065em"
  body:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.67
  label:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 700
rounded:
  sm: "8px"
  md: "11px"
  lg: "17px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary-teal}"
    textColor: "{colors.content-surface}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
  input:
    backgroundColor: "{colors.content-surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "18px 19px"
---

# Design System: SickleSense

## 1. Overview

**Creative North Star: "The Clinical Margin Note"**

SickleSense is a calm, evidence-first product interface for reading under time pressure. It borrows the trust of a clinical reference sheet, but uses generous spacing and a single cool teal accent to keep the experience approachable. The answer is the primary object; the source trail is always nearby and never hidden behind decorative complexity.

It explicitly rejects generic chatbot behavior, dense research dashboards as the first experience, and any implication that population-level evidence is personalized medical advice.

**Key Characteristics:**
- Calm clinical surfaces with crisp slate text.
- Teal used for action, provenance, and safe system status.
- Serif used sparingly for the human-facing hero phrase; DM Sans carries the product UI.
- Evidence is structured as readable source notes, not chat bubbles.

## 2. Colors

The palette is restrained: true white content, cool blue-gray navigation, and muted teal for meaningful action and trust.

### Primary
- **Clinical Teal** (#0f7d77): Primary action, active navigation, evidence iconography, and safe status.
- **Deep Teal** (#075d5a): Hover and high-emphasis teal text.

### Neutral
- **Slate Ink** (#19303a): Headings and primary text.
- **Muted Slate** (#62747d): Supporting copy and metadata.
- **Content White** (#ffffff): Answer cards and form surfaces.
- **Cool Mist** (#f5f8fa): Page and navigation background.
- **Divider Blue-Gray** (#dbe5e8): Borders and structural rules.

### Named Rules
**The Evidence Accent Rule.** Teal should signal action, provenance, or safety. It is not decorative background color.

## 3. Typography

**Display Font:** Fraunces (with Georgia fallback)

**Body Font:** DM Sans (with system-ui fallback)

**Character:** Fraunces adds a restrained editorial warmth to the opening thesis. DM Sans keeps the clinical workflow legible, familiar, and compact.

### Hierarchy
- **Display** (600, clamp(2.7rem, 6.5vw, 4.875rem), 0.99): Home hero only.
- **Headline** (600, 20px, 1.2): Answer section headings.
- **Title** (700, 13px, 1.35): Product labels and source names.
- **Body** (400, 14px, 1.67): Evidence and supporting explanations, capped near 68ch.
- **Label** (700, 11px, normal): Metadata, utility labels, and compact controls.

## 4. Elevation

SickleSense uses tonal layering first and soft ambient shadows second. Content cards and the question composer sit above the cool mist page surface without looking glossy or floating.

### Shadow Vocabulary
- **Surface lift** (`0 13px 35px #19303a0a`): Answer cards and primary composer.
- **Focus lift** (`0 0 0 4px #0f7d7712`): Focused input state.

### Named Rules
**The Quiet Surface Rule.** Shadows should be low-opacity and structural; never use glassmorphism or decorative glow as the primary surface treatment.

## 5. Components

### Buttons
- **Shape:** Soft compact radius (11px).
- **Primary:** Clinical Teal with white icon, 35px icon button for submit.
- **Hover / Focus:** Deep Teal hover, visible 3px teal focus outline.
- **Secondary / Ghost:** Transparent or pale surface with a thin divider border.

### Chips
- **Style:** White or near-white background, #d5e1e3 border, muted slate text, 8px radius.
- **State:** Hover shifts border and text toward Deep Teal.

### Cards / Containers
- **Corner Style:** 17px for primary surfaces, 8-11px for compact controls.
- **Background:** Content White on Cool Mist.
- **Shadow Strategy:** Quiet Surface Rule.
- **Border:** #dbe5e8, never a colored side stripe.
- **Internal Padding:** 20-28px depending on content density.

### Inputs / Fields
- **Style:** White field, #cfdde0 border, 17px radius, generous 18px internal padding.
- **Focus:** Clinical Teal border with a subtle teal focus halo.
- **Error / Disabled:** Use explicit copy and muted state colors; never rely on color alone.

### Navigation
- **Style:** Compact 78px top bar with brand mark, text navigation, and evidence-mode status.
- **States:** Muted slate default, Deep Teal active/hover, visible focus.
- **Mobile:** Collapsible menu with a white full-width dropdown below the header.

### Evidence Panel
The signature component turns citations into readable clinical source notes: document, section, page, and chunk ID are visible together, with progressive disclosure for retrieved passages.

## 6. Do's and Don'ts

### Do:
- **Do** put the answer before the evidence details, while keeping the evidence one action away.
- **Do** use teal only for action, provenance, current selection, and safety states.
- **Do** keep clinical prose readable with 1.67 line-height and a 68ch maximum measure.
- **Do** show unsupported questions as clear source-boundary states.
- **Do** support keyboard interaction and reduced motion.

### Don't:
- **Don't** make the product feel like a generic chatbot with playful chat bubbles or casual assistant language.
- **Don't** turn the first experience into a dense research dashboard full of metrics and technical controls.
- **Don't** present population-level evidence as personalized diagnosis, dosage, or treatment advice.
- **Don't** use gradient text, decorative glass cards, or colored side-stripe borders.
