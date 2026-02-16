"""
These prompt elements are designed for testing different levels of specification
for WCAG guidelines:
  1. Zero-shot baseline: no guidelines at all, rely on model's training data.
  2. Principle-level: high-level WCAG principles.
  3. Full guidelines: markdown-formatted version of docs provided by Aishwwarya.
"""

zero_shot_wcag = ""  # Intentionally empty - relies on model's pre-training knowledge of WCAG

principle_wcag = """# WCAG 2.1 Accessibility Guidelines - Principle Level

When evaluating accessibility, reference these core principles and success criteria:

## Four Core Principles (POUR)

1. **Perceivable**: Information and user interface components must be presentable to users in ways they can perceive
2. **Operable**: User interface components and navigation must be operable
3. **Understandable**: Information and the operation of user interface must be understandable
4. **Robust**: Content must be robust enough to be interpreted by a wide variety of user agents, including assistive technologies

## Key Success Criteria Categories

### Level A (Minimum)
- **1.1.1** Non-text Content: Provide text alternatives
- **1.3.1** Info and Relationships: Semantic structure
- **1.3.2** Meaningful Sequence: Correct reading order
- **2.1.1** Keyboard: All functionality available via keyboard
- **2.4.1** Bypass Blocks: Skip navigation mechanisms
- **2.4.2** Page Titled: Descriptive page titles
- **3.1.1** Language of Page: Programmatically determined language
- **3.3.1** Error Identification: Identify input errors
- **3.3.2** Labels or Instructions: Provide labels for inputs
- **4.1.1** Parsing: Valid markup
- **4.1.2** Name, Role, Value: Accessible names and roles

### Level AA (Recommended)
- **1.4.3** Contrast (Minimum): 4.5:1 contrast ratio
- **2.4.6** Headings and Labels: Descriptive headings
- **2.4.7** Focus Visible: Visible keyboard focus
- **3.2.3** Consistent Navigation: Consistent navigation order
- **3.2.4** Consistent Identification: Consistent component identification
- **3.3.3** Error Suggestion: Provide error suggestions
- **3.3.4** Error Prevention: Prevent errors in legal/financial transactions

### Level AAA (Enhanced)
- **1.4.6** Contrast (Enhanced): 7:1 contrast ratio
- **2.4.8** Location: Information about user's location
- **2.4.10** Section Headings: Organize content with headings

When reporting issues, cite the relevant success criterion number (e.g., "WCAG 1.4.3")."""

full_wcag = """# Complete Web Content Accessibility Guidelines (WCAG) Checklist

## Summary and Checklist: Semantic Structure and Navigation 

### Summary

Screen readers and other assistive technologies rely on the underlying semantic markup to convey meaningful information about the structure and content of web pages. The following is a list of all of the main principles covered in this module:

---

### Checklist


#### Page Title 

**Title for Every Page** 

* The page `<title>` MUST be present and MUST contain text.
* The page `<title>` MUST be updated when the web address changes.

**Meaningful Page Title** 

* The page `<title>` MUST be accurate and informative.
* If a page is the result of a user action or scripted change of context, the text of the `<title>` SHOULD describe the result or change of context to the user.
* The `<title>` SHOULD be concise.
* The page `<title>` SHOULD be unique, if possible.
* Unique information SHOULD come first in the `<title>`.
* The page `<title>` SHOULD match (or be very similar to) the top heading in the main content.


#### Language 

**Primary Language of Page** 

* The primary language of the page MUST be identified accurately on the `<html>` element.
* The primary language of the page MUST be identified with a valid value on the `<html>` element.

**Language of Parts within the Page**

* Inline language changes MUST be identified with a valid `lang` attribute.

**Language Codes** 

* The language code MUST be valid.


#### Landmarks 

**Creating Landmarks (HTML 5, ARIA)** 

* Landmarks SHOULD be used to designate pre-defined parts of the layout (`<header>`, `<nav>`, `<main>`, `<footer>`, etc.).

**Best Practices for Landmarks** 

* All text SHOULD be contained within a landmark region.
* Multiple instances of the same type of landmark SHOULD be distinguishable by different discernible labels (`aria-label` or `aria-labelledby`).
* A page SHOULD NOT contain more than one instance of each of the following landmarks: banner, main, and contentinfo.
* The total number of landmarks SHOULD be minimized to the extent appropriate for the content.

**Backward Compatibility**

* Landmarks SHOULD be made backward compatible.


#### Headings 

**Real Headings** 

* Text that acts as a heading visually or structurally SHOULD be designated as a true heading in the markup.
* Text that does not act as a heading visually or structurally SHOULD NOT be marked as a heading.

**Meaningful Text** 

* Headings MUST be accurate and informative.
* Heading text SHOULD be concise and relatively brief.

**Outline/Hierarchy of Content**

* Headings SHOULD convey a clear and accurate structural outline of the sections of content of a web page.
* Headings SHOULD NOT skip hierarchical levels.

**Heading Level 1 Best Practices**

* The beginning of the main content SHOULD start with `<h1>`.
* Most web pages SHOULD have only one `<h1>`.


#### Links 

**Designate Links Correctly** 

* Links MUST be semantically designated as such.
* Links and buttons SHOULD be designated semantically according to their functions.

**Link Text** 

* A link MUST have programmatically-discernible text, as determined by the accessible name calculation algorithm.
* The purpose of each link SHOULD be able to be determined from the link text alone.
* The link text SHOULD NOT repeat the role ("link").
* Features such as labels, names, and text alternatives for content that has the same functionality across multiple web pages MUST be consistently identified.

**Links to External Sites, New Windows, Files** 

* A link that opens in a new window or tab SHOULD indicate that it opens in a new window or tab.
* A link to a file or destination in an alternative or non-web format SHOULD indicate the file or destination type.
* A link to an external site MAY indicate that it leads to an external site.

**Visually Distinguishable from Text** 

* Links MUST be visually distinguishable from surrounding text.

**Visual focus indicator** 

* All focusable elements MUST have a visual focus indicator when in focus.
* Focusable elements SHOULD have enhanced visual focus indicator styles.


#### Navigation Between Pages 

**Navigation Lists** 

* A navigation list SHOULD be designated with the `<nav>` element or `role="navigation"`.
* A navigation list SHOULD include a visible method of informing users which page within the navigation list is the currently active/visible page.
* A navigation list SHOULD include a method of informing blind users which page within the navigation list is the currently active/visible page.

**Consistency** 

* Navigation patterns that are repeated on web pages MUST be presented in the same relative order each time they appear and MUST NOT change order when navigating through the site.


#### Navigation Within Pages 

**Skip Navigation Links** 

* A keyboard-functional "skip" link SHOULD be provided to allow keyboard users to navigate directly to the main content.
* The "skip link" should be the first focusable element on the page.
* A skip link MUST be either visible at all times or visible on keyboard focus.

**Table of Contents** 

* A table of contents for the page MAY be included at the top of the content or in the header.
* If a table of contents for the page is included, it SHOULD reflect the heading structure of the page.

**Reading Order and Tab/Focus Order** 

* The reading order MUST be logical and intuitive.
* The navigation order of focusable elements MUST be logical and intuitive.
* `tabindex` of positive values SHOULD NOT be used.

**Paginated Views**

* A paginated view SHOULD include a visible method of informing users which view is the currently active/visible view.
* A paginated view SHOULD include a method of informing blind users which view is the currently active/visible view.


#### Tables 

**Semantic Markup for Tabular Data** 

* Tabular data SHOULD be represented in a `<table>`.

**Table caption/name**

* Data tables SHOULD have a programmatically-associated caption or name.
* The name/caption of a data table SHOULD describe the identity or purpose of the table accurately, meaningfully, and succinctly.
* The name/caption of each data table SHOULD be unique within the context of other tables on the same page.

**Table Headers** 

* Table headers MUST be designated with `<th>`.
* Data table header text MUST accurately describe the category of the corresponding data cells.

**Simple Header Associations** 

* Table data cells MUST be associated with their corresponding header cells.

**Grouped Header Associations** 

* Table data group headers MUST be associated with their corresponding data cell groups.

**Complex Header Associations** 

* Header/data associations that cannot be designated with `<th>` and `scope` MUST be designated with `headers` plus `id`.

**Nested or Split Tables** 

* Data table headers and data associations MUST NOT be referenced across nested, merged, or separate tables.

**Table Summary** 

* A summary MAY be provided for data tables.
* A data table summary, if provided, SHOULD make the table more understandable to screen reader users.


**Layout Tables** 

* Tables SHOULD NOT be used for the purpose of purely visual (non-data) layout.
* Layout tables MUST NOT contain data table markup.


#### Lists 

**Semantic Markup for Lists** 

* Lists MUST be constructed using the appropriate semantic markup.


#### Iframes 

**Frame titles** 

* Iframes that convey content to users MUST have a non-empty `title` attribute.
* The iframe title MUST be accurate and descriptive.
* Frames MUST have a unique title (in the context of the page).

**Page Title Within an Iframe** 

* The source page of an iframe MUST have a valid, meaningful `<title>`.

**Semantic structure across iframes** 

* The heading hierarchy of an iframe SHOULD be designed to fit within the heading hierarchy of the parent document, if possible.

**Hiding iframes that don't contain meaningful content** 

* Hidden frames or frames that do not convey content to users SHOULD be hidden from assistive technologies using `aria-hidden="true"`.

#### Other Semantic Elements 

**`<strong>` and `<em>`** 

* Critical emphasis in the text SHOULD be conveyed through visual styling.
* Critical emphasis in the text SHOULD be conveyed in a text-based format.

**`<blockquote>` and `<q>`** 

* The `<blockquote>` element SHOULD be used to designate long (block level) quotations.
* The `<blockquote>` element SHOULD NOT be used for visual styling alone.
* The `<q>` element (for inline quotations) SHOULD NOT be used as the only way to designate quotations.

**`<code>`, `<pre>`**

* Code SHOULD be marked with the `<code>` element and styled to look different from non-code text.
* Blocks of code SHOULD be formatted with the `<pre>` element.

**Strikethrough/Delete and Insert** 

* Strikethrough text SHOULD be marked with the `<del>` element.
* Critical strikethrough text MUST be supplemented with a text-based method to convey the meaning of the strikethrough.
* Text designated for insertion SHOULD be marked with the `<ins>` element.
* Critical text designated for insertion MUST be supplemented with a text-based method to convey the meaning of the insertion.

**Highlighting (`<mark>`)** 

* Highlighted text SHOULD be marked with the `<mark>` element.
* Critical highlighted text SHOULD be supplemented with a text-based method to convey the meaning of the highlighting.


#### Parsing and Validity 

**Complete Start and End Tags** 

* In content implemented using markup languages, elements MUST have complete start and end tags.

**Conflicts and duplicates**

* IDs MUST be unique within a web page.
* Names, when provided, of block level elements (e.g. landmarks, tables, iframes, etc.) SHOULD be unique within a web page.

**Parent-child relationships** 

* Markup SHOULD adhere to required parent-child relationships of elements and attributes.

**Deprecated Markup** 

* Deprecated markup SHOULD NOT be used.

---

## Summary and Checklist: Form Labels, Instructions, and Validation 

### Summary

In order for users to know how to fill out a form, the form has to be accessible.
Key concepts include:

* Labels for form inputs 
* Labels for groups of inputs 
* Instructions and hints, where necessary 
* Error prevention 
* Form validation 

Information must be visible on the screen, accurate and meaningful, programmatically discernible, and programmatically associated with the appropriate form element or group.
Highly interactive elements require additional attention regarding focus management, ARIA names/roles/values, and ARIA live announcements.

---

### Checklist

#### Labels

**Semantic Labels**

* Labels MUST be programmatically associated with their corresponding elements.
* Labels MUST be programmatically-discernible.

**Meaningful Label Text**

* Labels MUST be meaningful.
* Labels MUST NOT rely solely on references to sensory characteristics.

**Icons as Labels**

* Icons MAY be used as visual labels (without visual text) if the meaning of the icon is visually self-evident AND if there is a programmatically-associated semantic label available to assistive technologies.

**Placeholder Text as Labels**

* Placeholder text MUST NOT be used as the only method of providing a label for a text input.

**Visibility of Labels**

* Labels MUST be visible.

**Proximity of Labels to Controls**

* A label SHOULD be visually adjacent to its corresponding element.
* A label SHOULD be adjacent in the DOM to its corresponding element.

**Multiple Labels for One Field**

* When multiple labels are used for one element, each label MUST be programmatically associated with the corresponding element.

**One Label for Multiple Fields**

* When one label is used for multiple elements, the label MUST be programmatically associated with each of the corresponding elements.
#### Group Labels

**Semantic Group Labels**

* Group labels MUST be programmatically-associated with the group if the individual labels for each element in the group are insufficient on their own.
* Group labels MUST be programmatically-discernible.

**Meaningful Group Labels**

* Group labels MUST be meaningful.
* Group labels MUST NOT rely solely on references to sensory characteristics.

**Proximity of Group Labels**

* Group labels SHOULD be visually adjacent to the grouped elements.
* Group labels SHOULD be adjacent in the DOM to the grouped elements.

**Visibility of Group Labels**

* Group labels MUST be visible.


#### Instructions & Other Helpful Info

**Instructions for Forms, Groups, and Sections**

* Instructions for groups or sections SHOULD be programmatically-associated with the group.
* Instructions for groups or sections MUST be programmatically-discernible.
* Instructions for groups or sections MUST be meaningful.
* Instructions for groups or sections MUST be visible.
* Instructions for groups or sections SHOULD be visually adjacent to the grouped elements.
* Instructions for groups or sections SHOULD be adjacent in the DOM to the grouped elements.
* If the instructions for groups or sections are not critical, the instructions MAY be hidden until the user requests them.
* Instructions for groups or sections MUST NOT rely solely on references to sensory characteristics.

**Instructions for Inputs**

* Instructions for an element MUST be programmatically-associated with the element.
* Instructions for an element MUST be available as programmatically-discernible text.
* Instructions for an element MUST be meaningful.
* Instructions for an element MUST be visible.
* Instructions for an element SHOULD be visually adjacent to the element.
* Instructions for an element SHOULD be adjacent in the DOM to the element.
* If the instructions for an element are not critical, the instructions MAY be hidden until the user requests them.
* Instructions for an element MUST NOT rely solely on references to sensory characteristics.

**Required Fields**

* Required fields SHOULD be programmatically designated as such.
* Required fields SHOULD have a visual indicator that the field is required.
* The form validation process MUST include an error message explaining that a field is required if the field isn't identified as required both visually and programmatically in the form's initial state.


#### Dynamic Forms & Custom Widgets

**Changes in Context**

* Focusing on an element MUST NOT automatically trigger a change of context, unless the user has been adequately advised ahead of time.
* Changing an element's value MUST NOT automatically trigger a change of context, unless the user is adequately advised ahead of time.
* Hovering over an element with the mouse MUST NOT automatically trigger a change of context, unless the user has been adequately advised ahead of time.

**Custom Form Inputs**

* Native HTML form elements SHOULD be used whenever possible.
* Custom form elements SHOULD act like native HTML form elements, to the extent possible.
* Custom form elements SHOULD have appropriate names, roles, and values.
* Updates and state changes that cannot be communicated through HTML or ARIA methods SHOULD be communicated via ARIA live messages.


#### Form Validation

**Error Identification Considerations**

* Error feedback SHOULD be made available immediately after form submission (or after an equivalent event if there is no form submission event).
* Error feedback MUST be programmatically-associated with the appropriate element.
* Error feedback MUST be programmatically-discernible.
* Error feedback MUST be meaningful.
* Error feedback MUST be visible.

**Success Confirmation Considerations**

* Success confirmation feedback SHOULD be programmatically-discernible.
* Success confirmation feedback SHOULD be meaningful.
* Success confirmation feedback MUST be visible.

---

## Summary and Checklist: Images, Canvas, SVG, and Other Non-Text Content

### Summary

All non-text content must be represented in a text format in one way or another, whether in the form of an alt attribute for an image, an alternative representation of non-HTML objects, or within the accessibility API methods of non-HTML objects.

---

### Checklist

#### Image Alt Text

**Informative Images**

* Images that convey content MUST have programmatically-discernible alternative text.
* The alternative text for informative images MUST be meaningful, accurately conveying the purpose of the image and the author's intent.
* Alternative text SHOULD NOT include words that identify the element as a graphic or image.
* The length of the alternative text for informative images SHOULD be concise (no more than about 150 characters).

**Decorative or Redundant Images**

* Images that do not convey content, are decorative, or are redundant to content already conveyed in text MUST be given null alternative text (`alt=""`), `ARIA role="presentation"`, or implemented as CSS backgrounds.

**Actionable Images**

* All actionable images (e.g., links, buttons, controls) MUST have alternative text.
* The alternative text for actionable images MUST be meaningful, accurately conveying the purpose or result of the action.
* Alternative text SHOULD NOT include words that identify the element as a link, graphic, or image.
* The length of the alternative text for actionable images SHOULD be concise (no more than about 150 characters).

**Form Inputs `type="image"`**

* Form inputs with `type="image"` MUST have alternative text.
* The alternative text MUST accurately convey the purpose or result of the input action.
* The length SHOULD be concise (no more than about 150 characters).

**Animated Images**

* A method MUST be provided to pause, stop, or hide any prerecorded video-only content that begins playing automatically and lasts more than 5 seconds.
* Animated images MUST NOT flash or flicker more than 3 times per second.

**Complex Images - Extended Descriptions**

* Complex images MUST be briefly described using alt text AND MUST have a more complete long description.
* The long description (or a link/button to access it) SHOULD be visible to sighted users.
* The long description SHOULD be programmatically associated with the image.

**Images of Text**

* An image MUST NOT include informative text if an equivalent visual presentation can be rendered using real text.
* Images MUST NOT include informative text unless the text is essential (like a logo) or the presentation is fully customizable.

**CSS Background Images**

* Purely decorative or redundant CSS images SHOULD NOT have a text alternative in the HTML content.
* The alternative text for informative or actionable CSS images MUST be available as programmatically-discernible text in the HTML content.
* This text MUST adequately and accurately describe the purpose of the image.

**Image Maps**

* The alternative text for the `<img>` of a client-side image map MUST be programmatically-discernible, meaningful, and concise.
* The alternative text for the `<area>` of a client-side image map MUST be programmatically-discernible, meaningful, and concise.
* Server-side image maps SHOULD NOT be used when a client-side map can accomplish the same functionality.


#### SVG

**SVG as img src**

* All SVG `<img>` elements SHOULD be set to `role="img"`.
* Informative or actionable SVG `<img>` elements MUST have meaningful, concise alternative text via `alt`, `aria-label`, or `aria-labelledby`.

**Inline SVGs**

* All `<svg>` elements MUST be set to `role="img"`.
* Informative or actionable `<svg>` elements MUST have meaningful alternative text via the `<title>` element.
* The `<title>` MUST be programmatically associated with the `<svg>` via `aria-labelledby`.
* Text within the image that needs to be spoken MUST be associated with the `<svg>` using `aria-labelledby`.
* Total alt text characters SHOULD NOT exceed 150.

**Embedded SVGs**

* SVG SHOULD NOT be embedded via `<object>` or `<iframe>`.

**Complex Alternative Text (SVG)**

* Complex `<svg>` images MUST have meaningful, concise alternative text AND a more complete long description.
* A `<desc>` element MUST be used for detailed description if not provided otherwise.
* The `<desc>` MUST be programmatically associated via `aria-labelledby`.

**Text in SVGs**

* Text within `<svg>` elements SHOULD be eliminated or kept to a minimum.
* Informative `<text>` elements MUST be referenced in the alternative text or long description.

**SVG Color Contrast and Animation**

* SVG images SHOULD include a base background color and be styled for Windows High Contrast Mode.
* SVG animations SHOULD use JavaScript instead of the `<animate>` element.
* Animations MUST NOT flash/blink more than 3 times per second, MUST NOT auto-play for more than 5 seconds, and MUST allow users to pause.

**Interactive SVGs**

* Interactive `<svg>` objects MUST be fully keyboard and touchscreen accessible.
* They MUST communicate the applicable name, role, and value of controls and elements.


#### Icon Fonts

* Informative icon fonts without visible text SHOULD be assigned `role="img"`.
* Informative and actionable icon fonts MUST have a meaningful text alternative.
* Decorative or redundant icon fonts SHOULD be set to `aria-hidden="true"`.


#### HTML 5 `<canvas>`

* When used for graphics, `<canvas>` elements MUST be assigned `role="img"`.
* All `<canvas>` elements MUST have meaningful text alternatives.
* Complex images in `<canvas>` MUST have detailed text alternatives.
* Elements operable with a mouse MUST also be keyboard accessible.


#### Multimedia

* All prerecorded video MUST have synchronized captions.
* All live video/audio with dialog/narration MUST or SHOULD have synchronized captions.
* All prerecorded video and audio MUST have text transcripts.
* Videos MUST include audio descriptions of important visual content not conveyed through audio.


#### Plug-ins and Documents

* All `<object>` elements MUST have alternative text.
* Accessible Silverlight and Flash objects MUST use the accessibility API and adhere to basic accessibility principles.
* Non-HTML documents MUST adhere to basic accessibility principles.
* PDF files MUST be in tagged PDF format.
* EPUB files SHOULD be in EPUB 3 format and MUST adhere to HTML accessibility principles.
"""