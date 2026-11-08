# NoteMind — UX Wireframe Specification

> **Source:** Three webpage views extracted from one reference screenshot.  
> **Purpose:** Low-fidelity UX wireframe documentation. This file describes the visible structure, labels, controls, and content hierarchy; it is not a pixel-perfect specification.

## Screen overview

| Screen | Purpose | Primary action |
|---|---|---|
| 1. Sign-in | Authenticate or start access to NoteMind | Continue with a social provider or email |
| 2. Notebook workspace | Ask questions about a notebook's uploaded sources and manage notes | Ask a question, summarize sources, or extract themes |
| 3. Notebook library | Browse existing notebooks or create a new one | Open a notebook or create one |

---

# 1. Sign-in page

## Layout

- Full-page, very light gray/off-white background.
- A single authentication card is centered horizontally and vertically.
- The card has a white background, subtle border/shadow, and rounded corners.
- Content is arranged in one vertical column with consistent spacing.

## Wireframe

```text
+--------------------------------------------------------------+
|                                                              |
|                                                              |
|                  +---------------------------+               |
|                  |        [NoteMind logo]     |               |
|                  |                           |               |
|                  |      Welcome to NoteMind  |               |
|                  | Your AI-powered research  |               |
|                  |        assistant          |               |
|                  |                           |               |
|                  | [G] Continue with Google  |               |
|                  | [■] Continue with Microsoft|              |
|                  | [●] Continue with Apple   |               |
|                  |                           |               |
|                  | ---- OR CONTINUE WITH ----|               |
|                  |                           |               |
|                  | Email address              |               |
|                  | [name@company.com       ]  |               |
|                  |                           |               |
|                  | [ Continue with Email   ]  |               |
|                  |                           |               |
|                  | By continuing, you agree   |               |
|                  | to NoteMind's Terms of     |               |
|                  | Service and Privacy Policy.|              |
|                  +---------------------------+               |
|                                                              |
|                                                              |
+--------------------------------------------------------------+
```

## Components and content

1. **Brand block**
   - NoteMind app icon/logo.
   - Heading: `Welcome to NoteMind`.
   - Supporting text: `Your AI-powered research assistant`.

2. **Social authentication**
   - `Continue with Google` button, with Google icon.
   - `Continue with Microsoft` button, with Microsoft icon.
   - `Continue with Apple` button, with Apple icon.
   - Buttons appear full-width, outlined, and vertically stacked.

3. **Email authentication**
   - Divider with the label `OR CONTINUE WITH`.
   - Label: `Email address`.
   - Email input with example placeholder/value: `name@company.com`.
   - Primary dark button: `Continue with Email`.

4. **Legal notice**
   - Text: `By continuing, you agree to NoteMind's Terms of Service and Privacy Policy.`
   - `Terms of Service` and `Privacy Policy` appear as links.

## Interaction notes

- Social buttons initiate the corresponding provider sign-in flow.
- The email field accepts an email address; the primary button continues the email sign-in flow.
- Terms of Service and Privacy Policy are links.
- The screenshot does not show password entry, validation, loading, or error states. Treat those as separate states to design if required.

---

# 2. Notebook workspace page

## Layout

- Large application shell with a fixed-width left sidebar and a main workspace.
- A slim top bar runs across the main workspace.
- Main content contains a centered welcome/question prompt, suggested actions, and an answer area.
- A message composer is anchored along the bottom of the main workspace.
- The sidebar has its own bottom-aligned account/plan area.

## Wireframe

```text
+---------------------------+----------------------------------------------+
| [icon] NoteMind       [≡] | Project: Quantum Computing Basics  Auto-saved |
|                           |                                  [ Share ]    |
| SOURCES                [+]|----------------------------------------------|
| [file] Research_Paper_    |                                              |
|        v1.pdf             |            What would you like to know?      |
| [file] Meeting_Notes.txt  |    Ask a question about your uploaded sources.|
|                           |                                              |
| SAVED NOTES            [+]|  +----------------------+ +----------------------+
| [note] Key Takeaways      |  | Summarize all sources | | Extract key themes    |
| [note] Quantum Theory     |  | Get a high-level      | | Identify recurring   |
|        Summary            |  | overview of everything| | patterns and topics   |
|                           |  | you've uploaded.      | | across documents.     |
| NOTEBOOK GUIDE            |  +----------------------+ +----------------------+
| +-----------------------+ |                                              |
| | Generate summaries,   | |  [assistant marker] Based on your sources,   |
| | FAQ, or study guides  | |  quantum computing leverages superposition   |
| | from your sources.   | |  and entanglement. Research_Paper_v1.pdf     |
| | [ Generate Guide ]   | |  mentions that current error correction is   |
| +-----------------------+ |  a major bottleneck [1].                      |
|                           |  [ Page 14 ]                                  |
|                           |                                              |
|                           |                                              |
|                           |----------------------------------------------|
|                           |       [ Ask a question about your sources ]  |
|                           |                                      [Send]  |
|                           |       NoteMind can make mistakes. Verify     |
|                           |                   important info.            |
|---------------------------|----------------------------------------------|
| [avatar] Alex Researcher  |                                              |
|          Free Plan    [⋮] |                                              |
+---------------------------+----------------------------------------------+
```

## Components and content

### A. Left sidebar

- **Brand/header:** NoteMind logo and a sidebar collapse/expand control.
- **Sources section:**
  - Section heading: `SOURCES`.
  - Add control (`+`).
  - Uploaded source entries (the screenshot appears to show `Research_Paper_v1.pdf` and `Meeting_Notes.txt`).
- **Saved Notes section:**
  - Section heading: `SAVED NOTES`.
  - Add control (`+`).
  - Note entries: `Key Takeaways` and `Quantum Theory Summary`.
- **Notebook Guide panel:**
  - Heading: `NOTEBOOK GUIDE`.
  - Description: `Generate summaries, FAQ, or study guides from your sources.`
  - Button: `Generate Guide`.
- **Account area (sidebar bottom):**
  - Avatar/profile icon.
  - Account name shown in the reference: `Alex Researcher`.
  - Plan label: `Free Plan`.
  - Overflow/account menu control.

### B. Main top bar

- Current notebook/project title: `Project: Quantum Computing Basics`.
- Save status: `Auto-saved`.
- Share button: `Share`.

### C. Empty-state prompt and suggested actions

- Main heading: `What would you like to know?`
- Supporting text: `Ask a question about your uploaded sources.`
- Two suggested-action cards:
  1. **Summarize all sources** — `Get a high-level overview of everything you've uploaded.`
  2. **Extract key themes** — `Identify recurring patterns and topics across documents.`

### D. Answer area

- Assistant response with an assistant/avatar marker.
- Example response shown in the reference:
  - `Based on your sources, quantum computing leverages superposition and entanglement. Research_Paper_v1.pdf mentions that current error correction is a major bottleneck [1].`
- A source citation/page chip appears under the answer: `Page 14`.

### E. Message composer and disclaimer

- Wide, rounded text input anchored at the bottom of the main panel.
- Send button/icon at the right end of the input.
- Disclaimer below the composer: `NoteMind can make mistakes. Verify important info.`

## Interaction notes

- Sidebar source and saved-note entries should be selectable.
- The `+` controls indicate add/upload actions for their respective sections.
- `Generate Guide`, the two suggested-action cards, `Share`, and the composer are interactive controls.
- The citation chip should open or locate the referenced source page if that behavior is part of the product requirements; this is a UX interpretation of the visible citation affordance.
- The screenshot shows an answer already present, so the prompt/actions and answer can be treated as different conversation states rather than necessarily appearing together in every state.

---

# 3. Notebook library page

## Layout

- Full-width application page with a slim top navigation bar.
- Brand at the left, notebook search field centered in the header, and utility/account icons on the right.
- Main content is centered in a broad content area.
- Notebook cards are arranged horizontally in a responsive grid/row.
- Footer links sit below the main content.

## Wireframe

```text
+--------------------------------------------------------------------------+
| [book icon] NoteMind       [ Search notebooks...           ] [ ? ] [↪]   |
+--------------------------------------------------------------------------+
|                                                                          |
|        Your Notebooks                                  [ + New Notebook ]|
|        Select a project to start chatting with your sources.             |
|                                                                          |
|  +-------------------+  +-------------------+  +-------------------+    |
|  |        [+]        |  | [notebook icon] [⋮]|  | [notebook icon] [⋮]|   |
|  |                   |  | Quantum Computing |  | Genetics & CRISPR |   |
|  | Create Notebook   |  | Basics            |  | Research          |   |
|  | Upload sources to |  | [file] 3 sources  |  | [file] 12 sources |   |
|  | begin             |  | EDITED 2H AGO     |  | EDITED YESTERDAY  |   |
|  +-------------------+  |                →  |  |                →  |   |
|                         +-------------------+  +-------------------+    |
|                                                                          |
|                         +-------------------+                            |
|                         | [notebook icon] [⋮]|                           |
|                         | Legal Case Analysis|                           |
|                         | [file] 5 sources   |                           |
|                         | EDITED OCT 24      |                           |
|                         |                →  |                           |
|                         +-------------------+                            |
|                                                                          |
+--------------------------------------------------------------------------+
| Privacy   Terms   Help                         NoteMind © 2026 · Send feedback|
+--------------------------------------------------------------------------+
```

## Components and content

### A. Top navigation

- NoteMind logo/wordmark on the left.
- Search input with placeholder: `Search notebooks...`.
- Help icon (`?`).
- Account/session utility icon on the right (exact action is not legible in the reference).

### B. Page heading and primary action

- Heading: `Your Notebooks`.
- Supporting text: `Select a project to start chatting with your sources.`
- Primary button: `+ New Notebook`.

### C. Create-notebook card

- Dashed-outline card with a centered plus icon.
- Title: `Create Notebook`.
- Supporting text: `Upload sources to begin`.
- Intended as an entry point for creating a notebook and adding its first sources.

### D. Existing notebook cards

Each card contains an icon, overflow menu, notebook title, source count, last-edited metadata, and a right-arrow/open affordance.

| Notebook | Source count | Last edited |
|---|---:|---|
| Quantum Computing Basics | 3 sources | 2h ago |
| Genetics & CRISPR Research | 12 sources | Yesterday |
| Legal Case Analysis | 5 sources | Oct 24 |

### E. Footer

- Links: `Privacy`, `Terms`, `Help`.
- Copyright: `NoteMind © 2026`.
- Feedback link: `Send feedback`.

## Interaction notes

- Search field filters or finds notebooks.
- `New Notebook` and the create card start the notebook-creation flow.
- Selecting a notebook card or its arrow opens that notebook.
- Each card's overflow menu (`⋮`) exposes notebook-specific actions; exact menu options are not visible in the screenshot.
- Help, account/session, footer legal links, and feedback are separate navigation actions.

---

# 4. Shared UX and visual direction

## Visual language observed

- Minimal, monochrome interface: white/off-white surfaces, near-black primary text and buttons, and subtle light-gray borders.
- Rounded cards, inputs, and buttons.
- Thin dividers and restrained iconography.
- Generous whitespace and limited visual decoration.
- Typography uses clear hierarchy: prominent page headings, medium card titles, and small muted helper/metadata text.

## Suggested shared components

| Component | Used on | Notes |
|---|---|---|
| NoteMind logo/wordmark | Sign-in, workspace, library | Keep icon and wordmark consistent |
| Primary button | Sign-in, workspace, library | Dark fill with light text |
| Secondary/outlined button | Sign-in, workspace | White fill with subtle border |
| Text input | Sign-in, workspace, library | Rounded, light border |
| Card | Sign-in, workspace, library | White surface with subtle border and radius |
| Icon button | Workspace, library | Small actions such as add, share, help, menu |
| Metadata label | Workspace, library | Muted text for plan, source count, save state, and last-edited time |

## Suggested screen flow

```text
[Sign-in]
    |
    v
[Notebook library] ---- Create Notebook ----> [New notebook setup]
    |
    | Open an existing notebook
    v
[Notebook workspace]
    |         |             |
    |         |             +--> [Generate Notebook Guide]
    |         +----------------> [Saved notes]
    +--------------------------> [Ask questions / view cited answers]
```

> **Note:** The flow above is a UX interpretation connecting the three supplied screens. The screenshot does not specify every intermediate state or the exact behavior of each action.

---

# 5. Items not specified by the reference

The screenshot does not provide enough detail to define the following. They should be designed separately rather than inferred from this wireframe:

- Mobile/tablet breakpoints and responsive navigation behavior.
- Loading, empty, error, and validation states.
- Email verification, password, OAuth callback, and account recovery screens.
- New-notebook setup details and supported upload formats/limits.
- Exact source-preview, note-editing, and citation-navigation behavior.
- Share permissions and notebook overflow-menu actions.
- Search result presentation and filtering behavior.
