# Explanatory visuals

Generated with the built-in ImageGen tool, landscape 16:9. Visual reference:
https://github.com/MikeCodeur/killer-saas/tree/main/docs/images

## Preparation and story cycle

Use case: infographic-diagram. Generate a new 16:9 widescreen explanatory image for the software method "ZERO TO PROD", in French. Style: refined hand-drawn whiteboard on a matte near-black charcoal background (#191b1b), white chalk outlines and simple line icons, warm coral headings (#ee836d), sparse mint green success marks. Inspired by a developer teaching on a dark board: clean, flat, spacious, very legible, no photos, no gradients, no decorative tiny text. Aim for 3072 x 1728. Every label below must be spelled exactly. Big sans-serif titles, compact rounded outline boxes, no crossing connectors.

Top title: "ZERO TO PROD". Smaller subtitle: "Préparer une fois. Livrer par story."
Two horizontal bands, each with six equally spaced boxes and simple rightward arrows.
Top band caption: "1 · PRÉPARATION — UNE FOIS PAR PRODUIT"
Six boxes, exact text:
"SETUP" with small command "/ztp-setup";
"PRD" with "/ztp-prd";
"STORIES" with "/ztp-stories";
"REVUE DU PÉRIMÈTRE" with "/ztp-stories-review";
"ARCHITECTURE" with "/ztp-architect";
"DESIGN SYSTEM" with "/ztp-design-system" and a small "si UI" badge.
Icons: settings, target, cards, checklist, blueprint, palette.
Below top band, small centered caption: "Réglages · périmètre · fondation · conventions"

Bottom band caption: "2 · LIVRAISON — POUR CHAQUE STORY"
Six boxes:
"RESEARCH" "/ztp-research";
"DESIGN" "/ztp-design" with "si UI";
"PLAN" "/ztp-plan";
"EXECUTE" "/ztp-execute";
"REVIEW" "/ztp-review";
"SHIP" "/ztp-ship".
Above PLAN to EXECUTE arrow, a small coral lock caption "Plan validé".
Under EXECUTE robot icon with "implementer isolé".
Under REVIEW different robot icon with "contexte vierge" and second line "preuve par neutralisation".
Above REVIEW to SHIP arrow, green label "Ship allowed: yes".
Under SHIP small rocket with "déploiement + smoke test".
A restrained red return arc from REVIEW toward EXECUTE above bottom band, label "critique → fix".
Footer, coral outlined capsule: "1 STORY = 1 WORKTREE = 1 BRANCHE = 1 PR"
Small footer line: "/ztp-flow : cycle court, mêmes gates"
Avoid TDD, red-first labels, model names, ks commands. Render only text given; no invented steps. Large margins, no cropped text.

## Production feedback loop

Use case: infographic-diagram. Generate a NEW 16:9 widescreen French explanatory image for ZERO TO PROD. Dark hand-drawn teaching-board style: matte charcoal #191b1b, crisp slightly irregular white chalk outlines, large coral #ee836d headings, mint green success arrows, red defect-return line, simple line icons. Spacious and precise, readable at presentation size, approximately 3072 x 1728. Flat layout, no photographs or gradients.

Title at top: "ZERO TO PROD — LA BOUCLE"
Subtitle: "La production alimente le prochain changement."
One horizontal chain of five large boxes, left to right, each with simple icon, bold label, command and short caption:
1 "INTENTION" / "/ztp-intent" / "Pourquoi changer ?" / small human-check badge "Validation humaine"
2 "STORIES" / "/ztp-stories" / "Quoi livrer ?"
3 "CYCLE" / "Research → Design → Plan" then "Execute → Review" / "Mêmes gates"
4 "SHIP" / "/ztp-ship" / "Déployer + smoke test"
5 "OPS" / "/ztp-ops" / "Observer + diagnostiquer"
White forward arrows joining all five boxes.

Below, TWO separate carefully routed return paths, both starting at OPS:
- Lower long coral path runs below the chain all the way back to INTENTION. Its label is "ÉVOLUTION PRODUIT → INTENTION À VALIDER". Clear arrowhead at INTENTION.
- A shorter red path runs through a small outlined ticket card labeled "DÉFAUT → TICKET" and then back up to CYCLE, entirely ABOVE the long coral return. Text beside the short red line: "flow ou cycle complet · sans intention". Clear arrowhead at CYCLE. IT MUST NOT POINT TO INTENTION.
Place a small side callout immediately under OPS, white dotted outline: "Seuil franchi ?" then "Proposer le rollback". This callout MUST NOT imply automatic execution.

A small boxed note above the left of the chain, below the title, reads "PRD : cadrage initial". Under the long return path, a separate small note reads "Chore et Quick Fix : sans intention".
Footer separated by a thin chalk line: "QUALITÉ EN CONTINU" in coral. Four minimal small outline icons and labels: "Hooks" · "Règles de revue" · "Evals" · "CI".
Bottom-most short white caption: "Commandes déclarées · rapports dans docs/ · aucune étape inventée"
Text must be exact with French accents. Keep all connectors distinct, no crossing lines, no duplicated process boxes. No TDD or red-first, no extra phases, no ks commands. Use very clear typography with ample negative space.

## Connector correction

Edit this infographic with one precise connector correction only. Preserve all text, typography, colors, icons, dimensions, and layout exactly. The long coral "ÉVOLUTION PRODUIT → INTENTION À VALIDER" return path currently appears to originate from the dotted "Seuil franchi ? Proposer le rollback" callout. That is semantically wrong. Disconnect that long coral path from the rollback callout completely. Instead, connect its RIGHT endpoint to the existing vertical line descending from the bottom-left side of the OPS box, at a clean T-junction with the red ticket return path. Thus OPS visibly branches into TWO paths: one left through DÉFAUT → TICKET to CYCLE; a second continues downward from that same OPS stem and then turns left along the existing lower coral path to INTENTION. The rollback callout stays connected ONLY to OPS by its short dotted line above. No line may exit the rollback callout toward intention. No crossing connectors. Keep every other pixel as close as possible to the original.
