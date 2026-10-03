---
name: Format Dehergne observation
description: Format selected ls$dehergne observation entries as multiline event blocks
---
Format the selected Kleio text according to these rules.

Input may contain one or more consecutive entries with this pattern:
`ls$dehergne/NNN/obs=TEXT`

1. Preserve the `ls$dehergne/NNN` identifier, indentation, wording, accents,
   citations, punctuation, and all content.
2. Replace each entry with this form:
   `ls$dehergne/NNN/obs="""`
   followed by the observation text and a closing `"""` on its own line.
3. Put each event on its own line. Event markers include `N.`, `E.`, `Emb.`,
   `A.`, `Arr.`, `V.`, `P.`, `M.`, `v.`, and year/date-led events.
4. Reflow prose to approximately 80 characters per line. Do not rewrite,
   translate, correct, summarize, or add content.
5. If consecutive entries have the same `ls$dehergne/NNN` identifier, merge
   their text into one triple-quoted entry in their original order.
Selected text:
${selection}

Return only formatted Kleio text. Do not include an explanation or Markdown fence.
