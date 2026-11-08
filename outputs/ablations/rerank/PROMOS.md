# Kuku Promo Finder - Ranked Promos
**Show:** I Married a Broken Soldier. He was a Duke  
**Generated:** 2026-11-07T14:14:47Z (commit 9223301)  
**Extractor:** openai / gpt-6-luna  
**Auditor:** openai / gpt-6-luna (LLM reads the clip screenplay)  
**Stages:** extraction, audit, rerank  
**Promos listed:** 15 of 42 candidates (23 passed audit, 19 failed, 0 unaudited)

---

## Hard rules enforced in code (see `src/validation.py`)
- Total duration 20-60s
- Hook beat starts within 3s of the opening cut; stakes legible in 3s
- Every cut is on a real beat edge; hook and cliffhanger quotes exist verbatim in the screenplay
- Audit-passing promos rank above audit-failing ones; repeated hook types/episodes are penalised

---

## Ranked Promos

### Rank 1: new:weaponized_grief (single episode)
- **Episode(s):** Episode 31
- **Segments:** [02:13.20 → 02:35.20] (22.0s) | **Total:** 22.0s
- **Score:** 8.35 / 10 (raw 8.35)
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 7.0
- **Hook (new:weaponized_grief):** `02:14.50` - *"This pathetic book is the only thing you still have from your mother."*
- **Cliffhanger (new:imminent_torture_cut):** `02:35.20` - *"Juliana recoils back against the hard dungeon wall, gasping for breath in raw terror as the searing iron stops inches from her eyes."*
  - *Withheld:* Whether Catherine will carry out the threat against Juliana or her mother's book.
- **Why it works:** Catherine targets Juliana's only treasured link to her mother, then the scene cuts with a red-hot iron poised inches from her eyes.

> **Audit (llm): PASS.** The book is threatened and burned immediately, making the grief hook legible without prior context; Catherine’s line explains why it matters. The clip ends on a clear threat of imminent injury, though the impact depends on the hot iron and Juliana’s fear reading clearly on screen.
>
> **Risks:** The burning book and glowing iron need to read convincingly on screen; Viewers do not learn who Catherine is, but that does not obscure the immediate conflict

---

### Rank 2: Class & Status Contempt (single episode)
- **Episode(s):** Episode 12
- **Segments:** [00:14.30 → 01:09.20] (54.9s) | **Total:** 54.9s
- **Score:** 7.95 / 10 (raw 7.95)
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Hook (class_status_contempt):** `00:14.30` - *"The proof is in his coat, Juliana. A valuable pocket watch doesn't just walk into a beggar's pocket."*
- **Cliffhanger (mortal_ultimatum):** `01:09.20` - *"Fail, or refuse, and your husband hangs from the gallows."*
  - *Withheld:* Whether Juliana will risk the frozen, razor-sharp briars to retrieve the ring—and whether she can save Alexander from the threatened hanging.
- **Why it works:** A theft accusation quickly becomes a cruel choice between risking injury and letting an innocent husband face the gallows.

> **Audit (llm): PASS.** The class-based insult lands immediately, and the demand, deadline, and threat to hang Juliana’s husband are all explicit, so the tagged hook and cliffhanger read without prior context. The pocket-watch accusation and charges are unexplained, but they remain easy to follow as the setup for Clarissa’s coercive demand.
>
> **Risks:** The viewer does not learn why the magistrate is coming or what evidence supports the charges, though neither is needed to understand the immediate stakes.

---

### Rank 3: Intimate Betrayal / Public Abandonment (single episode)
- **Episode(s):** Episode 1
- **Segments:** [00:39.10 → 01:23.60] (44.5s) | **Total:** 44.5s
- **Score:** 7.91 / 10 (raw 7.91)
- **Components:** hook 9.0, cliffhanger 7.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Hook (intimate_betrayal):** `00:39.10` - *"Because he is marrying me."*
- **Cliffhanger (new:withheld_response):** `01:23.60` - *"Tell them this is a mistake."*
  - *Withheld:* Whether Juliana's father will defend her or leave her to face the humiliation alone.
- **Why it works:** The wedding betrayal is instantly clear, and Juliana's plea to her father cuts off before his response.

> **Audit (llm): PASS.** The public wedding betrayal is clear from the dialogue, and the clip ends on an unanswered plea rather than resolving the conflict. The opening “he” is briefly unexplained to a cold viewer, but the wedding context and later lines quickly identify the groom and the betrayal.
>
> **Risks:** The opening pronoun “he” depends briefly on viewers inferring the wedding context.

---

### Rank 4: Unjust Framing / False Blame (single episode)
- **Episode(s):** Episode 27
- **Segments:** [02:03.10 → 02:28.00] (24.9s) | **Total:** 24.9s
- **Score:** 7.74 / 10 (raw 7.74)
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Hook (unjust_accusation):** `02:04.80` - *"She admits she has been giving the Duchess poison in secret!"*
- **Cliffhanger (new:forced_removal_in_progress):** `02:28.00` - *"The guard twists Juliana around and drags her forcibly toward the doorway as she struggles against his grip."*
  - *Withheld:* Whether Juliana can stop her forced removal and expose who has really been poisoning the Duchess.
- **Why it works:** A clear false accusation turns Juliana's attempt to help into apparent guilt, and the clip cuts while she is being forcibly taken away.

> **Audit (llm): PASS.** The accusation lands within the first two seconds, and Juliana immediately denies it; the nobleman then orders her removal, so the clip does not resolve the conflict. A cold viewer may not know why she has the vial or who the Duchess is, but the false-blame and immediate threat are clear from the dialogue and action.
>
> **Risks:** The vial and restricted chamber are unexplained, leaving some backstory unclear.

---

### Rank 5: new:poisoning_reveal (single episode)
- **Episode(s):** Episode 23
- **Segments:** [01:19.00 → 02:11.20] (52.2s) | **Total:** 52.2s
- **Score:** 6.86 / 10 (raw 6.86)
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 7.0, clarity 7.0
- **Hook (new:poisoning_reveal):** `01:19.00` - *"Someone is poisoning her."*
- **Cliffhanger (new:imminent_discovery):** `02:11.20` - *"Loud, metallic clack of the door latch turning, followed by the slow creak of wood hinges."*
  - *Withheld:* Who is at the door, whether they discover Juliana treating the Duchess, and whether the antidote can save her.
- **Why it works:** The poisoning accusation is immediately clear, and the rescue attempt is interrupted just as someone appears to reach the door.

> **Audit (llm): PASS.** The opening line’s “her” is briefly unanchored for a cold viewer, but the Duchess’s immediate coughing makes the poisoning stakes legible. The unfinished cure and the approaching person create a clear unresolved cliffhanger; its impact depends somewhat on the door sounds and close-up.
>
> **Risks:** The victim is not identified before the opening line, though the next beats clarify who is ill.; The cliffhanger relies on the latch sound and door movement landing clearly on screen.

---

### Rank 6: Physical Aggression / Shock Violence (single episode)
- **Episode(s):** Episode 15
- **Segments:** [00:46.50 → 01:18.50] (32.0s) | **Total:** 32.0s
- **Score:** 6.58 / 10 (raw 6.58)
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 10.0, injustice 9.0, clarity 9.0
- **Hook (physical_aggression):** `00:47.40` - *"The Thug with Cap violently shoves Juliana back with both hands; she cries out as she loses her balance and crashes hard onto the wet stone path."*
- **Cliffhanger (unexpected_arrival):** `01:18.50` - *"Alexander places himself directly between Juliana and the three thugs, staring them down with cold, deadly intent."*
  - *Withheld:* Whether Alexander can protect Juliana and what he will do against the three thugs.
- **Why it works:** A violent shove establishes the danger immediately, and Alexander’s sudden intervention cuts off before the thugs face any consequences.

> **Audit (llm): PASS.** The shove lands within the first two seconds, and Alexander’s arrival interrupts rather than resolves the threat. A cold viewer may not understand why the flowers matter or who Alexander is, but the assault and his role as Juliana’s rescuer are clear from the action.
>
> **Risks:** The emotional importance of the flowers depends on visual cues and a brief line of dialogue.; The cliffhanger relies on Alexander’s entrance and the thugs’ reactions reading clearly on screen.

---

### Rank 7: new:marriage_legitimacy_attack (single episode)
- **Episode(s):** Episode 46
- **Segments:** [01:06.80 → 01:58.20] (51.4s) | **Total:** 51.4s
- **Score:** 6.29 / 10 (raw 6.29)
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 7.0
- **Hook (new:marriage_legitimacy_attack):** `01:06.80` - *"Love doesn't make a Duchess, girl. Paper does."*
- **Cliffhanger (new:unanswered_legal_challenge):** `01:58.20` - *"Then let it prove that in ten days, before witnesses. Not with six halberds pointed at me in my own chapel."*
  - *Withheld:* Whether the High Priest will accept Alexander's demand for a witnessed trial or use his armed authority to stop him.
- **Why it works:** A church official denies Juliana's marriage and dignity, then Alexander openly challenges him while the outcome is still undecided.

> **Audit (llm): PASS.** The opening line immediately establishes a marriage-and-status dispute, and the later dialogue clarifies that the priest is challenging the marriage's validity; the ten-day demand remains unresolved. References to the church having “chained” Juliana and to “this floor” may be unclear to cold viewers, but they do not obscure the central conflict.
>
> **Risks:** Some backstory is unexplained; The legal and religious authority dispute may feel jargon-heavy

---

### Rank 8: new:precious_object_in_immediate_danger (single episode)
- **Episode(s):** Episode 18
- **Segments:** [00:56.20 → 01:27.50] (31.3s) | **Total:** 31.3s
- **Score:** 6.25 / 10 (raw 6.25)
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 9.0, injustice 6.0, clarity 8.0
- **Hook (new:precious_object_in_immediate_danger):** `00:56.50` - *"The ledger!"*
- **Cliffhanger (new:imminent_disaster):** `01:27.50` - *"Down!"*
  - *Withheld:* Whether Alexander can shield Juliana from the massive beam about to crash where she was standing.
- **Why it works:** A woman risks a burning room to save her mother’s ledger, and the clip cuts just as a beam threatens both of them.

> **Audit (llm): PASS.** The ledger is in danger immediately, and the collapse remains unresolved when the clip cuts; a cold viewer can understand the stakes from “It’s my mother’s” and “the ceiling is coming down.” The main risk is that the tension depends on convincing fire and collapse effects, and Juliana does retrieve the ledger before the final disaster beat.
>
> **Risks:** The fire and collapsing-beam effects need to feel convincing for the danger to land.; Retrieving the ledger pays off the object-in-danger hook before the clip ends.

---

### Rank 9: Unjust Framing / False Blame (single episode)
- **Episode(s):** Episode 28
- **Segments:** [00:12.70 → 00:47.00] (34.3s) | **Total:** 34.3s
- **Score:** 6.14 / 10 (raw 7.49) (diversity x0.82)
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Hook (unjust_accusation):** `00:12.70` - *"She looks exactly like a poisoner."*
- **Cliffhanger (new:interrupted_testimony):** `00:47.00` - *"They have been—"*
  - *Withheld:* The Duchess’s unfinished accusation could expose who was involved in the poisoning, but she collapses before she can finish.
- **Why it works:** A cold viewer immediately sees Juliana accused of poisoning, then hears the victim defend her and begin to expose the real culprit before collapsing.

> **Audit (llm): PASS.** The accusation is explicitly cleared when the Duchess declares Juliana innocent, but the scene pivots to her accusation against Rupert and Catherine and cuts off mid-testimony, leaving a new conflict unresolved. The first exchange makes the basic stakes understandable without prior context; names and relationships remain unexplained but are not necessary to follow the scene.
>
> **Risks:** The initial accusation gets a clear payoff before the clip ends; The final interruption relies partly on the Duchess’s visible collapse

---

### Rank 10: Public Humiliation & Scorn (single episode)
- **Episode(s):** Episode 41
- **Segments:** [00:30.50 → 00:52.40] (21.9s), [01:21.00 → 01:33.50] (12.5s) | **Total:** 34.4s
- **Score:** 5.76 / 10 (raw 5.76)
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 10.0, injustice 9.0, clarity 7.0
- **Hook (public_humiliation):** `00:30.50` - *"Look at her."*
- **Cliffhanger (unexpected_arrival):** `01:33.50` - *"Silhouetted armed figures emerge through the smoke and rubble of the breached doorway. Juliana slowly turns her head, glancing back toward the light."*
  - *Withheld:* Who has breached the cathedral, and what will they do to the people humiliating Juliana?
- **Why it works:** A noblewoman’s public sneer quickly reveals Juliana’s humiliation, then the unexpected breach leaves the crowd’s fate—and Juliana’s rescue—unresolved.

> **Audit (llm): PASS.** The public humiliation is explicit: aristocrats mock Juliana before a visible congregation, and the armed figures appear as a new disruption that the clip ends on. The emotional payoff depends partly on selling the explosion, smoky silhouettes, and Juliana’s reaction, while the exact backstory remains unexplained but is not needed to follow this moment.
>
> **Risks:** Climactic impact depends on convincing explosion and smoke effects; Cold viewers will not know why Juliana was disgraced

---

### Rank 11: new:coerced_renunciation (single episode)
- **Episode(s):** Episode 34
- **Segments:** [02:22.40 → 03:10.00] (47.6s) | **Total:** 47.6s
- **Score:** 5.75 / 10 (raw 5.75)
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 10.0, injustice 8.0, clarity 7.0
- **Hook (new:coerced_renunciation):** `02:22.40` - *"Lady Juliana, if you wish to save yourself, renounce these practices."*
- **Cliffhanger (new:verdict_cut):** `03:10.00` - *"The Judge extends his raised hand high in judgment over Lady Juliana as the scene holds on her standing still and unbroken before fading to black."*
  - *Withheld:* The judge's ruling: whether Juliana will be condemned for refusing to renounce her healing.
- **Why it works:** A judge pressures a woman to abandon her healing to save herself, and she refuses while his verdict remains unseen.

> **Audit (llm): PASS.** The ultimatum and Juliana’s refusal establish the coercion immediately, while her later reference to healing and witchcraft supplies enough context for a cold viewer. The verdict is withheld rather than leaked; its impact relies somewhat on the Judge’s raised hand and the fade to black, but the dialogue makes clear that a sentence is imminent.
>
> **Risks:** The phrase “these practices” is initially vague, though the later dialogue clarifies the accusation.; The cliffhanger depends partly on the visual of the Judge raising his hand and the cut before the sentence.

---

### Rank 12: new:presumed_dead_survivor (single episode)
- **Episode(s):** Episode 35
- **Segments:** [01:47.00 → 02:25.00] (38.0s) | **Total:** 38.0s
- **Score:** 5.15 / 10 (raw 5.15)
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 7.0, clarity 7.0
- **Hook (new:presumed_dead_survivor):** `01:47.00` - *"I was shot. Left for dead."*
- **Cliffhanger (new:unanswered_identity):** `02:25.00` - *"Who?"*
  - *Withheld:* The identity of the person who orchestrated the ambush and wanted Alexander dead.
- **Why it works:** A blunt survival reveal quickly turns into a conspiracy mystery, then cuts just as Alexander’s mother demands the culprit’s identity.

> **Audit (llm): PASS.** The opening immediately establishes that Alexander was presumed dead, and the final unanswered “Who?” cleanly withholds the identity of the person behind the ambush. The conspiracy remains broad for a cold viewer, but the dialogue makes the basic stakes understandable without prior context.
>
> **Risks:** The identity and motive behind the plot remain vague by design; The stormy setting and intense close-ups add atmosphere, but the dialogue carries the hook and cliffhanger

---

### Rank 13: new:identity_reclamation_declaration (single episode)
- **Episode(s):** Episode 39
- **Segments:** [01:02.00 → 01:38.41] (36.4s) | **Total:** 36.4s
- **Score:** 4.98 / 10 (raw 4.98)
- **Components:** hook 6.0, cliffhanger 7.0, payoff withheld 9.0, injustice 3.0, clarity 6.0
- **Hook (new:identity_reclamation_declaration):** `01:02.00` - *"Enough hiding."*
- **Cliffhanger (new:rescue_vow_cut):** `01:38.00` - *"And I am bringing my wife home."*
  - *Withheld:* Whether Alexander reaches Juliana and succeeds in rescuing her.
- **Why it works:** A man declares he is done hiding, reclaims his authority, and vows to bring his wife home, then the clip cuts before the rescue.

> **Audit (llm): PASS.** The hook is immediate and supported by Alexander’s explicit lines about ending his hiding and reclaiming his identity; the final vow is cut before any rescue or resolution occurs. A cold viewer may not know why his wife needs bringing home or what “my house” means, but the core stakes remain legible and the visuals are reinforced by dialogue.
>
> **Risks:** The wife’s situation and the significance of the chapel are unexplained; The transformation’s impact relies partly on the costume and staging

---

### Rank 14: Class & Status Contempt (single episode)
- **Episode(s):** Episode 28
- **Segments:** [01:41.50 → 02:16.70] (35.2s) | **Total:** 35.2s
- **Score:** 4.87 / 10 (raw 6.98) (diversity x0.697)
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 7.0
- **Hook (class_status_contempt):** `01:44.20` - *"The disgraced daughter..."*
- **Cliffhanger (new:execution_threat):** `02:16.70` - *"...before he sends you to the gallows."*
  - *Withheld:* Whether Juliana can defend herself against the charge and avoid execution remains unresolved.
- **Why it works:** The clip turns a revealed identity into a string of personal and class-based attacks, then ends with Juliana facing a threatened execution.

> **Audit (llm): PASS.** The class-status contempt and gallows threat are both explicit, and the insult arrives within the first three seconds; the dialogue carries the stakes without requiring subtle visuals. A cold viewer may not understand why a botanical book could lead to execution, but the immediate humiliation and danger remain clear.
>
> **Risks:** The book’s connection to the alleged offense is unexplained

---

### Rank 15: Unjust Framing / False Blame (single episode)
- **Episode(s):** Episode 29
- **Segments:** [00:37.70 → 01:18.10] (40.4s) | **Total:** 40.4s
- **Score:** 4.35 / 10 (raw 6.47) (diversity x0.672)
- **Components:** hook 8.0, cliffhanger 7.0, payoff withheld 9.0, injustice 9.0, clarity 7.0
- **Hook (unjust_accusation):** `00:37.70` - *"The magistrate will call it witchcraft."*
- **Cliffhanger (new:challenge_response_cut):** `01:18.10` - *"What exactly do you think a penniless veteran can do against Ashbrook?"*
  - *Withheld:* Whether Juliana's husband can defy Ashbrook and find her before Catherine's framing succeeds.
- **Why it works:** A cold viewer immediately hears Catherine threaten to frame Juliana for witchcraft, then sees her hope of rescue mocked without learning whether anyone can save her.

> **Audit (llm): PASS.** The witchcraft framing is clear and appears knowingly false, and the threat arrives immediately; the dialogue carries the stakes without requiring the described facial acting. A cold viewer may not know what the book contains or what Ashbrook is, but can still follow the threat and Catherine’s contempt for Juliana’s husband.
>
> **Risks:** The book’s significance is unexplained; Ashbrook is an unfamiliar reference

---
