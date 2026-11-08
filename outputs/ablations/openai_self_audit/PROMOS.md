# Kuku Promo Finder - Ranked Promos
**Show:** I Married a Broken Soldier. He was a Duke  
**Generated:** 2026-11-07T14:21:05Z (commit 9223301)  
**Extractor:** openai / gpt-6-luna  
**Auditor:** openai / gpt-6-luna (LLM reads the clip screenplay)  
**Stages:** extraction, audit, export_csv  
**Promos listed:** 15 of 60 candidates (34 passed audit, 26 failed, 0 unaudited)

---

## Hard rules enforced in code (see `src/validation.py`)
- Total duration 20-60s
- Hook beat starts within 3s of the opening cut; stakes legible in 3s
- Every cut is on a real beat edge; hook and cliffhanger quotes exist verbatim in the screenplay
- Audit-passing promos rank above audit-failing ones; repeated hook types/episodes are penalised

---

## Ranked Promos

### Rank 1: new:threatened_last_keepsake (single episode)
- **Episode(s):** Episode 5
- **Segments:** [00:49.00 → 01:40.80] (51.8s) | **Total:** 51.8s
- **Score:** 7.51 / 10 (raw 7.51) | conversion intent: 8.0/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Hook (new:threatened_last_keepsake):** `00:49.00` - *"It belonged to my mother! It is all I have left of her."*
- **Cliffhanger (interrupted_retaliation):** `01:40.80` - *"Choose your next words carefully."*
  - *Withheld:* Whether the mysterious husband follows through on his warning to Gerald, and how Gerald responds.
- **Why it works:** A heartbreaking loss turns into a direct threat, leaving viewers waiting to see whether her new husband will make Gerald regret humiliating her.

> **Audit (llm): PASS.** The keepsake is recovered, but the antagonists’ humiliation of Juliana is not answered: the man’s explicit warning to Gerald cuts off before any retaliation lands, so the main conflict remains open. The immediate stakes are legible from the opening, though the final threat is familiar and the rescued book settles the clip’s first, smaller source of suspense.
>
> **Risks:** The threatened keepsake is returned before the ending, reducing the payoff of the opening hook.; The closing ultimatum is clear but generic; the clip does not establish who the bearded man is or what he can do.

---

### Rank 2: Intimate Betrayal / Public Abandonment (single episode)
- **Episode(s):** Episode 2
- **Segments:** [00:00.00 → 00:37.10] (37.1s) | **Total:** 37.1s
- **Score:** 7.48 / 10 (raw 7.48) | conversion intent: 8.5/10
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 9.0
- **Payoff Location:** `Ep 2 00:34.30`
- **Hook (intimate_betrayal):** `00:00.00` - *"I cannot marry you, Juliana."*
- **Cliffhanger (new:unanswered_plea_for_protection):** `00:37.10` - *"Surely you will not let him humiliate me like this?"*
  - *Withheld:* Whether Juliana's father will defend her or abandon her too.
- **Why it works:** The immediate altar rejection establishes the stakes, then the cut makes viewers wait to learn whether Juliana's own family will protect her.

> **Audit (llm): PASS.** The public wedding rejection and selfish switch to Clarissa are immediately legible, and the clip ends on Juliana’s unanswered plea to her father without showing a rescue or comeuppance. The only notable dependency is visual: the father’s stern reaction needs to read clearly as refusal or withheld support, since he does not answer in the excerpt.
>
> **Risks:** The father’s silent reaction may be less clear on screen than the dialogue-driven betrayal.

---

### Rank 3: Physical Aggression / Shock Violence (single episode)
- **Episode(s):** Episode 3
- **Segments:** [00:58.30 → 01:23.90] (25.6s) | **Total:** 25.6s
- **Score:** 7.4 / 10 (raw 7.4) | conversion intent: 8.4/10
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Payoff Location:** `Ep 3 01:21.80`
- **Hook (physical_aggression):** `01:00.50` - *"The guards forcefully grab Juliana by both shoulders and drag her backwards."*
- **Cliffhanger (new:armed_standoff_before_violence):** `01:23.90` - *"...let her go."*
  - *Withheld:* Whether the stranger can stop the armed guard and free Juliana before her family has her removed.
- **Why it works:** The forced removal makes the injustice immediate, and the stranger's final command cuts just before the armed guard's response.

> **Audit (llm): PASS.** The opening immediately establishes Juliana being forcibly removed, and the stranger’s final order leaves the confrontation unresolved, creating a clear reason to watch the next moment. The cold viewer need not know the characters’ backstory; however, the “armed standoff” label overstates what the screenplay shows, since no weapons appear.
>
> **Risks:** The armed-standoff tag is unsupported by the screenplay; the cliffhanger is a threatened confrontation, not a shown armed standoff.; The payoff depends on the stranger’s threatening delivery, though the physical action and dialogue make the stakes legible.

---

### Rank 4: new:dangerous_coerced_choice (single episode)
- **Episode(s):** Episode 12
- **Segments:** [00:57.30 → 01:24.70] (27.4s) | **Total:** 27.4s
- **Score:** 7.29 / 10 (raw 7.29) | conversion intent: 8.0/10
- **Components:** hook 9.0, cliffhanger 9.0, payoff withheld 10.0, injustice 9.0, clarity 7.0
- **Hook (new:dangerous_coerced_choice):** `00:57.30` - *"You will retrieve it with your bare hands before the magistrate arrives."*
- **Cliffhanger (new:accepted_dangerous_challenge):** `01:24.70` - *"Tell me where the garden is."*
  - *Withheld:* Whether Juliana can retrieve the ring from the frozen briars—and whether doing so will save Alexander.
- **Why it works:** A cruel demand turns into Juliana's desperate decision, then cuts before she faces the frozen thorns.

> **Audit (llm): PASS.** The ultimatum and threat to hang her husband make the danger and Juliana’s sacrifice understandable immediately, and the clip ends before we see what she must retrieve or what happens next. “It” has no clear antecedent for a cold viewer, but the uncertainty is a curiosity gap rather than a resolution leak.
>
> **Risks:** The object Juliana must retrieve is never identified, which may make the challenge feel vague.; The clip depends somewhat on facial expressions and tense delivery, though the dialogue carries the stakes.

---

### Rank 5: new:forced_renunciation (single episode)
- **Episode(s):** Episode 34
- **Segments:** [02:22.40 → 03:10.00] (47.6s) | **Total:** 47.6s
- **Score:** 7.13 / 10 (raw 7.13) | conversion intent: 8.0/10
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 10.0, injustice 9.0, clarity 8.0
- **Hook (new:forced_renunciation):** `02:22.40` - *"Lady Juliana, if you wish to save yourself, renounce these practices."*
- **Cliffhanger (new:verdict_withheld):** `03:10.00` - *"The Judge extends his raised hand high in judgment over Lady Juliana as the scene holds on her standing still and unbroken before fading to black."*
  - *Withheld:* The judge's verdict and the consequences of Juliana refusing to renounce her healing.
- **Why it works:** The threat is explicit from the start, and the final raised hand promises a verdict while withholding it.

> **Audit (llm): PASS.** The ultimatum and Juliana’s refusal create a clear choice, and the clip withholds the judge’s sentence rather than resolving the conflict. Cold viewers may not understand what “these practices” means until the witchcraft accusation arrives later, and the final cliff relies partly on the raised-hand visual, but the courtroom dialogue makes the pending verdict legible.
>
> **Risks:** The nature of the accused practices is unclear in the opening seconds; The final beat depends partly on the judge's visual gesture

---

### Rank 6: Class & Status Contempt (single episode)
- **Episode(s):** Episode 31
- **Segments:** [01:51.60 → 02:35.20] (43.6s) | **Total:** 43.6s
- **Score:** 6.97 / 10 (raw 6.97) | conversion intent: 8.0/10
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Hook (class_status_contempt):** `01:51.60` - *"That is why you were born in the wrong world. Women like me are meant to be admired. Women like you are meant to serve."*
- **Cliffhanger (new:imminent_torture):** `02:35.20` - *"Juliana recoils back against the hard dungeon wall, gasping for breath in raw terror as the searing iron stops inches from her eyes."*
  - *Withheld:* Whether Catherine burns Juliana's mother's book or uses the hot iron on Juliana, and how Juliana survives the threat.
- **Why it works:** A cruel class-based threat turns into a personal attack on Juliana's last keepsake, then cuts with the hot iron still inches from her eyes.

> **Audit (llm): PASS.** The class-based contempt lands immediately, and Juliana’s sharp retort is only a brief reversal: Catherine escalates by destroying the book and ends with the poker inches from Juliana’s face, leaving the central danger unresolved. The book’s destruction and the final threat rely partly on convincing fire and close-up visuals, but the dialogue makes the emotional stakes legible without prior knowledge.
>
> **Risks:** The burning book and glowing poker need to read clearly on a phone screen.; The clip gives no context for who Catherine and Juliana are, though their conflict and immediate stakes are understandable.

---

### Rank 7: Unjust Framing / False Blame (single episode)
- **Episode(s):** Episode 30
- **Segments:** [01:34.60 → 02:23.50] (48.9s) | **Total:** 48.9s
- **Score:** 6.73 / 10 (raw 6.73) | conversion intent: 8.5/10
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 9.0, injustice 10.0, clarity 8.0
- **Hook (unjust_accusation):** `01:34.60` - *"Do not hide the evidence, manufacture it."*
- **Cliffhanger (new:imminent_false_charge):** `02:23.50` - *"Tomorrow, she stops being a prisoner. She becomes a witch."*
  - *Withheld:* Whether Juliana can expose the fabricated charge or escape the trial and threat of hanging.
- **Why it works:** The blunt order to fabricate evidence stops the scroll, and the cut leaves Juliana facing a planned witchcraft charge without showing her response.

> **Audit (llm): PASS.** The conspiracy and imminent execution threat are clear immediately, and nothing shows the accusation succeeding or the conflict being resolved. A cold viewer is not told who “her” is or why she is being targeted, and the long, dialogue-heavy villain scene offers little connection to the protagonist—but the explicit plan to frame and hang her creates a strong next-moment question.
>
> **Risks:** The target remains unnamed until later, with no context for why the villains are targeting her.; The clip relies almost entirely on exposition and villain performances; the protagonist is absent.; The plan is spelled out in detail, so the remaining curiosity is mainly whether she can escape it.

---

### Rank 8: new:property_desecration (single episode)
- **Episode(s):** Episode 15
- **Segments:** [00:03.60 → 01:02.00] (58.4s) | **Total:** 58.4s
- **Score:** 6.68 / 10 (raw 6.68) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 7.0
- **Payoff Location:** `Ep 15 01:03.50`
- **Hook (new:property_desecration):** `00:03.60` - *"The thug brutally smashes his club down into a wooden planter box, shattering the frame."*
- **Cliffhanger (new:poised_destruction_cut):** `01:02.00` - *"The Tall Thug hoists his heavy wooden club above his head to crush the remaining herbs right before Juliana."*
  - *Withheld:* Whether the thug brings the club down and whether Juliana is hurt before anyone intervenes.
- **Why it works:** The smash opens on active destruction, while Juliana's pleas and the raised club build anger and urgency toward an unresolved intervention.

> **Audit (llm): PASS.** The opening smash makes the threat legible immediately, and the clip ends before the raised club lands, preserving an unresolved danger rather than leaking a comeuppance. A cold viewer may not know why the thugs are targeting Juliana, but the destruction of her medicinal plants and her being shoved into the mud make the immediate stakes clear.
>
> **Risks:** The clip relies on the destruction, shove, and blood seeping through bandages reading clearly on screen.; The larger reason for the attack is not established within the clip.

---

### Rank 9: new:marriage_invalidation (single episode)
- **Episode(s):** Episode 46
- **Segments:** [01:32.20 → 02:03.60] (31.4s) | **Total:** 31.4s
- **Score:** 6.64 / 10 (raw 6.64) | conversion intent: 8.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 8.0, clarity 8.0
- **Hook (new:marriage_invalidation):** `01:32.20` - *"God did not marry you. A frightened parishioner did, without leave, without license, without the Crown's blessing!"*
- **Cliffhanger (new:trial_verdict_threat):** `02:03.60` - *"Ten days. And if the council rules against you, this county watches you lose her twice."*
  - *Withheld:* The council's ruling and whether Alexander and Juliana will remain married.
- **Why it works:** It opens on a direct attack on the marriage, then turns the conflict into a deadline with a painful consequence.

> **Audit (llm): PASS.** The clip clearly establishes that Alexander’s marriage is being challenged and that a council ruling is pending in ten days; neither the marriage nor the dispute is resolved. A cold viewer may not know why losing her would matter emotionally, but the immediate stakes and unresolved outcome are legible from the dialogue.
>
> **Risks:** The relationship history and the meaning of losing her twice are unexplained.; The pending ruling creates a clear open loop, but the ten-day deadline may feel distant rather than like an immediate next-moment payoff.

---

### Rank 10: new:rightful_status_usurpation (single episode)
- **Episode(s):** Episode 19
- **Segments:** [00:55.30 → 01:18.80] (23.5s) | **Total:** 23.5s
- **Score:** 6.56 / 10 (raw 6.56) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 8.0, clarity 7.0
- **Hook (new:rightful_status_usurpation):** `00:55.30` - *"Rupert has become the face of Ashburg. He sits in your father's room, signs your estate papers, gives orders as though the title already belongs to him."*
- **Cliffhanger (new:family_in_peril_revelation):** `01:18.80` - *"My mother is a prisoner in her own house."*
  - *Withheld:* Whether Alexander can free his mother and reclaim Ashburg from the usurpers.
- **Why it works:** The takeover is legible immediately, then the conflict sharpens into a personal threat before Alexander can act.

> **Audit (llm): PASS.** The opening immediately establishes a takeover, and the final line makes the danger personal without showing Alexander solve it. A cold viewer may not know who Rupert or Lady Catherine are, or how Catherine relates to the mother, but the estate usurpation and family peril remain understandable.
>
> **Risks:** Unexplained names and titles add some context fog; The emotional force depends partly on Alexander's restrained visual reaction, though the dialogue carries the stakes

---

### Rank 11: new:poisoning_conspiracy (single episode)
- **Episode(s):** Episode 26
- **Segments:** [00:56.00 → 01:55.50] (59.5s) | **Total:** 59.5s
- **Score:** 6.52 / 10 (raw 6.52) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 7.0, clarity 8.0
- **Hook (new:poisoning_conspiracy):** `00:56.00` - *"Rupert and Catherine want me dead. They are poisoning me in my own bed, aren't they?"*
- **Cliffhanger (truth_half_revealed):** `01:55.50` - *"Where... where... Where did you get this ring? Speak to me!"*
  - *Withheld:* Why the Duchess recognizes Juliana's ring and what it reveals about Juliana's identity or connection to her.
- **Why it works:** The Duchess's immediate danger is clear from the opening line, and the ring question ends on a concrete mystery without revealing its answer.

> **Audit (llm): PASS.** The poisoning accusation is answered almost immediately—Juliana confirms it and says the Duchess is safe—so that hook loses its tension. The ring question supplies a fresh unresolved mystery, though its impact depends on viewers noticing the ring and reading the Duchess’s reaction as significant.
>
> **Risks:** The poisoning thread is effectively resolved within the opening seconds.; The ring’s significance is not explained; viewers must trust the Duchess’s shock and urgent question.; The key reveal relies on the ring being visually distinct and readable in a brief close-up.

---

### Rank 12: new:poisoning_discovery (single episode)
- **Episode(s):** Episode 23
- **Segments:** [01:19.00 → 02:11.20] (52.2s) | **Total:** 52.2s
- **Score:** 6.44 / 10 (raw 6.44) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 7.0, clarity 7.0
- **Hook (new:poisoning_discovery):** `01:19.00` - *"Someone is poisoning her."*
- **Cliffhanger (new:approaching_intruder_at_door):** `02:11.20` - *"SFX: Loud, metallic clack of the door latch turning, followed by the slow creak of wood hinges."*
  - *Withheld:* Who is entering, what they will do, and whether Juliana can save the Duchess.
- **Why it works:** A blunt poisoning reveal gives the stakes immediately, then the turning latch makes the viewer wonder whether the culprit is coming in.

> **Audit (llm): PASS.** The poisoning is stated immediately, and the Duchess’s collapse makes the stakes legible; the cure is only being prepared, not shown to work. The approaching person is unidentified and the door opening cuts off before we see who it is, creating a clear next-moment question, though the opening “her” has a brief referential ambiguity for cold viewers.
>
> **Risks:** The first line’s “her” is briefly unexplained, though the Duchess’s collapse clarifies the reference moments later.; The threat relies partly on door and sound effects, but Prudence’s warning also communicates that someone is coming.

---

### Rank 13: Secret Status Reveal / Authority Exposure (single episode)
- **Episode(s):** Episode 42
- **Segments:** [00:30.50 → 01:17.50] (47.0s) | **Total:** 47.0s
- **Score:** 6.37 / 10 (raw 6.37) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 7.0, payoff withheld 8.0, injustice 6.0, clarity 8.0
- **Hook (secret_status_reveal):** `00:30.50` - *"You cannot be him. Alexander died!"*
- **Cliffhanger (new:revenge_confrontation):** `01:17.50` - *"And now, Rupert... we settle what you stole."*
  - *Withheld:* Alexander's confrontation with Rupert and what happens when he tries to settle what Rupert stole.
- **Why it works:** The incredulous opening instantly frames a high-stakes return, while the final threat makes the viewer want to see Rupert face its consequences.

> **Audit (llm): PASS.** The opening immediately establishes that Alexander was believed dead, and his mother’s explicit Duke proclamation plus Rupert’s terror make the reveal legible without prior context. His revenge is promised but not shown; the long emotional reunion slows the middle, and the clip leaves the specifics of what Rupert stole unclear.
>
> **Risks:** The revenge payoff is a familiar, nonspecific promise; The mother-son reunion takes up substantial time after the opening hook; A cold viewer does not learn what Rupert stole

---

### Rank 14: new:child_life_at_risk (single episode)
- **Episode(s):** Episode 21
- **Segments:** [00:04.20 → 00:40.40] (36.2s) | **Total:** 36.2s
- **Score:** 6.36 / 10 (raw 6.36) | conversion intent: 6.5/10
- **Components:** hook 8.0, cliffhanger 7.0, payoff withheld 8.0, injustice 8.0, clarity 9.0
- **Payoff Location:** `Ep 21 01:06.80`
- **Hook (new:child_life_at_risk):** `00:04.20` - *"Lady Juliana! Please! You have to help me, Toby is dying!"*
- **Cliffhanger (new:rescue_before_outcome):** `00:40.40` - *"Stand up. Sinking to your knees will not save him. Let me grab my ledger. We go now."*
  - *Withheld:* Whether Juliana's remedy can save Toby.
- **Why it works:** The desperate plea makes the danger instantly legible, then cuts just as Juliana sets out to save him.

> **Audit (llm): PASS.** The child’s danger and Juliana’s decision to help are clear even without prior context, and the clip ends before Toby’s fate or the rescue is shown. The repeated pleas make the middle feel somewhat prolonged, and the ending promises a rescue more than a distinctive twist, which may limit paid conversion.
>
> **Risks:** Repeated pleas slow the middle; The rescue setup is emotionally clear but not especially distinctive; The outcome is withheld, but the next moment is framed as a rescue rather than a surprising reveal

---

### Rank 15: new:ceremony_interruption (single episode)
- **Episode(s):** Episode 45
- **Segments:** [01:26.50 → 02:01.75] (35.2s) | **Total:** 35.2s
- **Score:** 6.32 / 10 (raw 6.32) | conversion intent: 8.0/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 7.0, injustice 8.0, clarity 8.0
- **Hook (new:ceremony_interruption):** `01:28.40` - *"No one will bow yet!"*
- **Cliffhanger (new:antagonist_triumph_before_countermove):** `02:01.75` - *"ACTION: Catherine raises her chin, a vindictive smirk spreading across her lips as she realizes her rival's claim has just been torn to pieces."*
  - *Withheld:* Whether Alexander will challenge the ruling and protect Juliana's claim as his wife and Duchess.
- **Why it works:** The interruption instantly turns a public triumph into a legal crisis, then ends on the antagonist's apparent victory before Alexander can respond.

> **Audit (llm): PASS.** The opening door slam and immediate order create a clear interruption, and the proclamation makes the stakes legible even without prior context. It does reveal that the marriage is being declared invalid, but cuts before Alexander or Juliana can respond, leaving the counter-move as a credible reason to continue.
>
> **Risks:** The legal ruling answers the immediate question of whether the marriage is recognized, reducing some suspense.; Catherine's relationship to Juliana is unexplained, though her triumphant reaction is readable from context.

---
