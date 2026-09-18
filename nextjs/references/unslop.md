# Unslop: Writing and Technical Documentation Discipline

Remove AI patterns, filler, and corporate jargon from technical documentation, commit messages, code comments, and pull requests.

---

## Content Discipline

1. **Superficial -ing phrases.** Delete phrases like "highlighting", "ensuring", "reflecting", "showcasing", "fostering". Replace with concrete mechanisms or facts.
2. **Vague attributions.** Do not write "Experts recommend" or "Industry reports suggest". Name the specific RFC, specification, or author, or state the technical requirement directly.

---

## Language and Vocabulary

3. **Banned AI vocabulary.** Replace these words with plain English:
   - "crucial", "pivotal" -> "important", "required"
   - "utilize", "leverage" -> "use"
   - "delve" -> "examine", "read"
   - "enhance" -> "improve"
   - "intricate" -> "complex"
   - "testament", "tapestry", "landscape" (abstract) -> state the specific state or fact
   - "fostering", "garner" -> cut or replace with plain action verbs
4. **Fancy ways to say "is".** Avoid "serves as", "stands as", "boasts", "features". Say "is" or "has".
5. **Rule of three.** Avoid forcing ideas into artificial triplets. Use the exact number that exists.
6. **Synonym cycling.** Do not switch between terms for the same concept in one paragraph. Pick one clear name and keep it.

---

## Style and Typography

7. **No em dashes.** Avoid em dashes. Use periods or commas.
8. **No mid-sentence colon connectors.** Write complete sentences.
9. **No decorative emojis.** Do not use emojis in headings, titles, or technical lists.
10. **Sentence case headings.** Use sentence case for section titles, not title case.
11. **Straight quotes.** Use straight quotes (`"` and `'`), never curly quotes.

---

## Plain Speech in Code and Architecture

12. **Say what it does, not how it feels.**
    - Don't: "types that follow your schema effortlessly"
    - Do: "`z.infer<typeof Schema>` derives the exact TypeScript interface"
13. **Active voice.** "the compiler validates queries" instead of "queries are validated".
14. **Cut adverbs.** Use concrete numbers or strong verbs. "runs in 12ms" instead of "runs extremely quickly".
15. **Plain words over jargon.** "use" instead of "utilize", "add" instead of "wedge in", "move" instead of "evacuate".
