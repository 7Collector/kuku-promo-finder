# Kuku Promo Finder - Ranked Promos
**Show:** I Married a Broken Soldier. He was a Duke  
**Generated:** 2026-11-07T15:34:49Z (commit 9223301)  
**Extractor:** openai / gpt-6-luna  
**Auditor:** panel / ['openai:gpt-6-luna', 'gemini:gemini-3.5-flash-lite'] (LLM reads the clip screenplay)  
**Stages:** extraction, audit, audit_panel, export_csv  
**Promos listed:** 15 of 60 candidates (26 passed audit, 34 failed, 0 unaudited)

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
- **Audit Tier:** Tier 1
- **Hook (new:threatened_last_keepsake):** `00:49.00` - *"It belonged to my mother! It is all I have left of her."*
- **Cliffhanger (interrupted_retaliation):** `01:40.80` - *"Choose your next words carefully."*
  - *Withheld:* Whether the mysterious husband follows through on his warning to Gerald, and how Gerald responds.
- **Why it works:** A heartbreaking loss turns into a direct threat, leaving viewers waiting to see whether her new husband will make Gerald regret humiliating her.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The keepsake is recovered, but the antagonists’ humiliation of Juliana is not answered: the man’s explicit warning to Gerald cuts off before any retaliation lands, so the main conflict remains open. The immediate stakes are legible from the opening, though the final threat is familiar and the rescued book settles the clip’s first, smaller source of suspense.] | [gemini-3.5-flash-lite: The promo opens instantly with emotional stakes and physical drama, transitioning smoothly into hero protection and ending on a sharp, tense verbal threat before any resolution occurs.]
> - **openai (gpt-6-luna):** PASS - The keepsake is recovered, but the antagonists’ humiliation of Juliana is not answered: the man’s explicit warning to Gerald cuts off before any retal
> - **gemini (gemini-3.5-flash-lite):** PASS - The promo opens instantly with emotional stakes and physical drama, transitioning smoothly into hero protection and ending on a sharp, tense verbal th
>
> **Risks:** The closing ultimatum is clear but generic; the clip does not establish who the bearded man is or what he can do.; Slight reliance on atmospheric production value (rain and mud effects) to land the full emotional weight; The threatened keepsake is returned before the ending, reducing the payoff of the opening hook.

---

### Rank 2: Intimate Betrayal / Public Abandonment (single episode)
- **Episode(s):** Episode 2
- **Segments:** [00:00.00 → 00:37.10] (37.1s) | **Total:** 37.1s
- **Score:** 7.48 / 10 (raw 7.48) | conversion intent: 8.5/10
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 9.0
- **Payoff Location:** `Ep 2 00:37.50`
- **Audit Tier:** Tier 1
- **Hook (intimate_betrayal):** `00:00.00` - *"I cannot marry you, Juliana."*
- **Cliffhanger (new:unanswered_plea_for_protection):** `00:37.10` - *"Surely you will not let him humiliate me like this?"*
  - *Withheld:* Whether Juliana's father will defend her or abandon her too.
- **Why it works:** The immediate altar rejection establishes the stakes, then the cut makes viewers wait to learn whether Juliana's own family will protect her.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The public wedding rejection and selfish switch to Clarissa are immediately legible, and the clip ends on Juliana’s unanswered plea to her father without showing a rescue or comeuppance. The only notable dependency is visual: the father’s stern reaction needs to read clearly as refusal or withheld support, since he does not answer in the excerpt.] | [gemini-3.5-flash-lite: The clip delivers an immediate intimate betrayal within the first three seconds and steadily escalates tension without resolving the humiliation. Ending on an unanswered plea to her cold father leaves a strong curiosity gap for a viewer looking for revenge or rescue.]
> - **openai (gpt-6-luna):** PASS - The public wedding rejection and selfish switch to Clarissa are immediately legible, and the clip ends on Juliana’s unanswered plea to her father with
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip delivers an immediate intimate betrayal within the first three seconds and steadily escalates tension without resolving the humiliation. Endi
>
> **Risks:** High reliance on dramatic dialogue tropes; relies on the viewer engaging with classic wedding rejection melodrama.; The father’s silent reaction may be less clear on screen than the dialogue-driven betrayal.

---

### Rank 3: Physical Aggression / Shock Violence (single episode)
- **Episode(s):** Episode 3
- **Segments:** [00:58.30 → 01:23.90] (25.6s) | **Total:** 25.6s
- **Score:** 7.4 / 10 (raw 7.4) | conversion intent: 8.4/10
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Payoff Location:** `Ep 3 01:24.00`
- **Audit Tier:** Tier 1
- **Hook (physical_aggression):** `01:00.50` - *"The guards forcefully grab Juliana by both shoulders and drag her backwards."*
- **Cliffhanger (new:armed_standoff_before_violence):** `01:23.90` - *"...let her go."*
  - *Withheld:* Whether the stranger can stop the armed guard and free Juliana before her family has her removed.
- **Why it works:** The forced removal makes the injustice immediate, and the stranger's final command cuts just before the armed guard's response.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The opening immediately establishes Juliana being forcibly removed, and the stranger’s final order leaves the confrontation unresolved, creating a clear reason to watch the next moment. The cold viewer need not know the characters’ backstory; however, the “armed standoff” label overstates what the screenplay shows, since no weapons appear.] | [gemini-3.5-flash-lite: The clip delivers an immediate hook with the heroine being violently dragged out, followed by high-tension hero intervention that cuts cleanly before any physical resolution or identity reveal.]
> - **openai (gpt-6-luna):** PASS - The opening immediately establishes Juliana being forcibly removed, and the stranger’s final order leaves the confrontation unresolved, creating a cle
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip delivers an immediate hook with the heroine being violently dragged out, followed by high-tension hero intervention that cuts cleanly before 
>
> **Risks:** The cliffhanger tag notes an 'armed standoff', but no physical weapons are drawn in the screenplay text.; The armed-standoff tag is unsupported by the screenplay; the cliffhanger is a threatened confrontation, not a shown armed standoff.; The payoff depends on the stranger’s threatening delivery, though the physical action and dialogue make the stakes legible.

---

### Rank 4: new:dangerous_coerced_choice (single episode)
- **Episode(s):** Episode 12
- **Segments:** [00:57.30 → 01:24.70] (27.4s) | **Total:** 27.4s
- **Score:** 7.29 / 10 (raw 7.29) | conversion intent: 8.0/10
- **Components:** hook 9.0, cliffhanger 9.0, payoff withheld 10.0, injustice 9.0, clarity 7.0
- **Audit Tier:** Tier 1
- **Hook (new:dangerous_coerced_choice):** `00:57.30` - *"You will retrieve it with your bare hands before the magistrate arrives."*
- **Cliffhanger (new:accepted_dangerous_challenge):** `01:24.70` - *"Tell me where the garden is."*
  - *Withheld:* Whether Juliana can retrieve the ring from the frozen briars—and whether doing so will save Alexander.
- **Why it works:** A cruel demand turns into Juliana's desperate decision, then cuts before she faces the frozen thorns.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The ultimatum and threat to hang her husband make the danger and Juliana’s sacrifice understandable immediately, and the clip ends before we see what she must retrieve or what happens next. “It” has no clear antecedent for a cold viewer, but the uncertainty is a curiosity gap rather than a resolution leak.] | [gemini-3.5-flash-lite: The promo effectively establishes a high-stakes, dangerous situation with a clear, immediate threat to the protagonist's husband. The dialogue clearly conveys the coercion and Juliana's sacrificial resolve, creating a strong curiosity gap about the dangerous task ahead.]
> - **openai (gpt-6-luna):** PASS - The ultimatum and threat to hang her husband make the danger and Juliana’s sacrifice understandable immediately, and the clip ends before we see what 
> - **gemini (gemini-3.5-flash-lite):** PASS - The promo effectively establishes a high-stakes, dangerous situation with a clear, immediate threat to the protagonist's husband. The dialogue clearly
>
> **Risks:** Reliance on strong visual acting to convey emotional intensity described in screenplay; Minor context deficit regarding the specific 'charges' but the threat is clear; The object Juliana must retrieve is never identified, which may make the challenge feel vague.; The clip depends somewhat on facial expressions and tense delivery, though the dialogue carries the stakes.

---

### Rank 5: new:forced_renunciation (single episode)
- **Episode(s):** Episode 34
- **Segments:** [02:22.40 → 03:10.00] (47.6s) | **Total:** 47.6s
- **Score:** 7.13 / 10 (raw 7.13) | conversion intent: 8.0/10
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 10.0, injustice 9.0, clarity 8.0
- **Audit Tier:** Tier 1
- **Hook (new:forced_renunciation):** `02:22.40` - *"Lady Juliana, if you wish to save yourself, renounce these practices."*
- **Cliffhanger (new:verdict_withheld):** `03:10.00` - *"The Judge extends his raised hand high in judgment over Lady Juliana as the scene holds on her standing still and unbroken before fading to black."*
  - *Withheld:* The judge's verdict and the consequences of Juliana refusing to renounce her healing.
- **Why it works:** The threat is explicit from the start, and the final raised hand promises a verdict while withholding it.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The ultimatum and Juliana’s refusal create a clear choice, and the clip withholds the judge’s sentence rather than resolving the conflict. Cold viewers may not understand what “these practices” means until the witchcraft accusation arrives later, and the final cliff relies partly on the raised-hand visual, but the courtroom dialogue makes the pending verdict legible.] | [gemini-3.5-flash-lite: This promo effectively establishes a high-stakes conflict around Lady Juliana's defiance against a witchcraft accusation, ending on a strong cliffhanger with her verdict withheld. The dialogue is self-contained and compelling, creating immediate curiosity for a new viewer.]
> - **openai (gpt-6-luna):** PASS - The ultimatum and Juliana’s refusal create a clear choice, and the clip withholds the judge’s sentence rather than resolving the conflict. Cold viewer
> - **gemini (gemini-3.5-flash-lite):** PASS - This promo effectively establishes a high-stakes conflict around Lady Juliana's defiance against a witchcraft accusation, ending on a strong cliffhang
>
> **Risks:** The final beat depends partly on the judge's visual gesture; Reliance on strong visual acting for full emotional impact; The nature of the accused practices is unclear in the opening seconds

---

### Rank 6: Class & Status Contempt (single episode)
- **Episode(s):** Episode 31
- **Segments:** [01:51.60 → 02:35.20] (43.6s) | **Total:** 43.6s
- **Score:** 6.97 / 10 (raw 6.97) | conversion intent: 8.0/10
- **Components:** hook 8.0, cliffhanger 9.0, payoff withheld 9.0, injustice 9.0, clarity 8.0
- **Audit Tier:** Tier 1
- **Hook (class_status_contempt):** `01:51.60` - *"That is why you were born in the wrong world. Women like me are meant to be admired. Women like you are meant to serve."*
- **Cliffhanger (new:imminent_torture):** `02:35.20` - *"Juliana recoils back against the hard dungeon wall, gasping for breath in raw terror as the searing iron stops inches from her eyes."*
  - *Withheld:* Whether Catherine burns Juliana's mother's book or uses the hot iron on Juliana, and how Juliana survives the threat.
- **Why it works:** A cruel class-based threat turns into a personal attack on Juliana's last keepsake, then cuts with the hot iron still inches from her eyes.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The class-based contempt lands immediately, and Juliana’s sharp retort is only a brief reversal: Catherine escalates by destroying the book and ends with the poker inches from Juliana’s face, leaving the central danger unresolved. The book’s destruction and the final threat rely partly on convincing fire and close-up visuals, but the dialogue makes the emotional stakes legible without prior knowledge.] | [gemini-3.5-flash-lite: The clip hooks immediately with high-stakes elitist dialogue and escalates rapidly through emotional destruction to physical jeopardy. The unresolved threat of the hot iron inches from the protagonist's eyes creates a powerful curiosity gap with zero resolution leak.]
> - **openai (gpt-6-luna):** PASS - The class-based contempt lands immediately, and Juliana’s sharp retort is only a brief reversal: Catherine escalates by destroying the book and ends w
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip hooks immediately with high-stakes elitist dialogue and escalates rapidly through emotional destruction to physical jeopardy. The unresolved 
>
> **Risks:** The burning book and glowing poker need to read clearly on a phone screen.; The clip gives no context for who Catherine and Juliana are, though their conflict and immediate stakes are understandable.; Relies on believable prop/FX execution for the red-hot poker to maintain immersion

---

### Rank 7: Unjust Framing / False Blame (single episode)
- **Episode(s):** Episode 30
- **Segments:** [01:34.60 → 02:23.50] (48.9s) | **Total:** 48.9s
- **Score:** 6.73 / 10 (raw 6.73) | conversion intent: 8.5/10
- **Components:** hook 9.0, cliffhanger 8.0, payoff withheld 9.0, injustice 10.0, clarity 8.0
- **Audit Tier:** Tier 1
- **Hook (unjust_accusation):** `01:34.60` - *"Do not hide the evidence, manufacture it."*
- **Cliffhanger (new:imminent_false_charge):** `02:23.50` - *"Tomorrow, she stops being a prisoner. She becomes a witch."*
  - *Withheld:* Whether Juliana can expose the fabricated charge or escape the trial and threat of hanging.
- **Why it works:** The blunt order to fabricate evidence stops the scroll, and the cut leaves Juliana facing a planned witchcraft charge without showing her response.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The conspiracy and imminent execution threat are clear immediately, and nothing shows the accusation succeeding or the conflict being resolved. A cold viewer is not told who “her” is or why she is being targeted, and the long, dialogue-heavy villain scene offers little connection to the protagonist—but the explicit plan to frame and hang her creates a strong next-moment question.] | [gemini-3.5-flash-lite: The promo effectively establishes a chilling conspiracy against Juliana, clearly outlining the manufactured evidence and the dire consequences. The immediate threat and high stakes are evident from the opening seconds, creating a strong curiosity gap.]
> - **openai (gpt-6-luna):** PASS - The conspiracy and imminent execution threat are clear immediately, and nothing shows the accusation succeeding or the conflict being resolved. A cold
> - **gemini (gemini-3.5-flash-lite):** PASS - The promo effectively establishes a chilling conspiracy against Juliana, clearly outlining the manufactured evidence and the dire consequences. The im
>
> **Risks:** Initial pronoun ambiguity before Juliana is named; The plan is spelled out in detail, so the remaining curiosity is mainly whether she can escape it.; The target remains unnamed until later, with no context for why the villains are targeting her.; Unexplained references to 'the Dowager' and 'witch's disgraced daughter' might hint at complex backstory without immediate clarity; The clip relies almost entirely on exposition and villain performances; the protagonist is absent.

---

### Rank 8: new:marriage_invalidation (single episode)
- **Episode(s):** Episode 46
- **Segments:** [01:32.20 → 02:03.60] (31.4s) | **Total:** 31.4s
- **Score:** 6.64 / 10 (raw 6.64) | conversion intent: 8.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 8.0, clarity 8.0
- **Audit Tier:** Tier 1
- **Hook (new:marriage_invalidation):** `01:32.20` - *"God did not marry you. A frightened parishioner did, without leave, without license, without the Crown's blessing!"*
- **Cliffhanger (new:trial_verdict_threat):** `02:03.60` - *"Ten days. And if the council rules against you, this county watches you lose her twice."*
  - *Withheld:* The council's ruling and whether Alexander and Juliana will remain married.
- **Why it works:** It opens on a direct attack on the marriage, then turns the conflict into a deadline with a painful consequence.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The clip clearly establishes that Alexander’s marriage is being challenged and that a council ruling is pending in ten days; neither the marriage nor the dispute is resolved. A cold viewer may not know why losing her would matter emotionally, but the immediate stakes and unresolved outcome are legible from the dialogue.] | [gemini-3.5-flash-lite: The promo immediately establishes a high-stakes conflict over Alexander's marriage and identity, culminating in a compelling, unresolved threat. While some initial character references might be vague for a cold viewer, the core conflict and Alexander's status are quickly clarified.]
> - **openai (gpt-6-luna):** PASS - The clip clearly establishes that Alexander’s marriage is being challenged and that a council ruling is pending in ten days; neither the marriage nor 
> - **gemini (gemini-3.5-flash-lite):** PASS - The promo immediately establishes a high-stakes conflict over Alexander's marriage and identity, culminating in a compelling, unresolved threat. While
>
> **Risks:** Minor initial context deficit regarding 'girl' and 'you'; The relationship history and the meaning of losing her twice are unexplained.; Moderate visual dependency for emotional impact; The pending ruling creates a clear open loop, but the ten-day deadline may feel distant rather than like an immediate next-moment payoff.

---

### Rank 9: new:rightful_status_usurpation (single episode)
- **Episode(s):** Episode 19
- **Segments:** [00:55.30 → 01:18.80] (23.5s) | **Total:** 23.5s
- **Score:** 6.56 / 10 (raw 6.56) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 8.0, clarity 7.0
- **Audit Tier:** Tier 1
- **Hook (new:rightful_status_usurpation):** `00:55.30` - *"Rupert has become the face of Ashburg. He sits in your father's room, signs your estate papers, gives orders as though the title already belongs to him."*
- **Cliffhanger (new:family_in_peril_revelation):** `01:18.80` - *"My mother is a prisoner in her own house."*
  - *Withheld:* Whether Alexander can free his mother and reclaim Ashburg from the usurpers.
- **Why it works:** The takeover is legible immediately, then the conflict sharpens into a personal threat before Alexander can act.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The opening immediately establishes a takeover, and the final line makes the danger personal without showing Alexander solve it. A cold viewer may not know who Rupert or Lady Catherine are, or how Catherine relates to the mother, but the estate usurpation and family peril remain understandable.] | [gemini-3.5-flash-lite: The promo effectively establishes a high-stakes family peril and the usurper threat right away without leaking the resolution. The dialogue clearly frames the mother's imprisonment and the antagonist's takeover, driving strong curiosity.]
> - **openai (gpt-6-luna):** PASS - The opening immediately establishes a takeover, and the final line makes the danger personal without showing Alexander solve it. A cold viewer may not
> - **gemini (gemini-3.5-flash-lite):** PASS - The promo effectively establishes a high-stakes family peril and the usurper threat right away without leaking the resolution. The dialogue clearly fr
>
> **Risks:** Unexplained names and titles add some context fog; Relies entirely on exposition rather than immediate physical conflict; The emotional force depends partly on Alexander's restrained visual reaction, though the dialogue carries the stakes

---

### Rank 10: new:poisoning_conspiracy (single episode)
- **Episode(s):** Episode 26
- **Segments:** [00:56.00 → 01:55.50] (59.5s) | **Total:** 59.5s
- **Score:** 6.52 / 10 (raw 6.52) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 7.0, clarity 8.0
- **Audit Tier:** Tier 1
- **Hook (new:poisoning_conspiracy):** `00:56.00` - *"Rupert and Catherine want me dead. They are poisoning me in my own bed, aren't they?"*
- **Cliffhanger (truth_half_revealed):** `01:55.50` - *"Where... where... Where did you get this ring? Speak to me!"*
  - *Withheld:* Why the Duchess recognizes Juliana's ring and what it reveals about Juliana's identity or connection to her.
- **Why it works:** The Duchess's immediate danger is clear from the opening line, and the ring question ends on a concrete mystery without revealing its answer.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The poisoning accusation is answered almost immediately—Juliana confirms it and says the Duchess is safe—so that hook loses its tension. The ring question supplies a fresh unresolved mystery, though its impact depends on viewers noticing the ring and reading the Duchess’s reaction as significant.] | [gemini-3.5-flash-lite: The clip establishes high stakes and clear emotional resonance immediately, culminating in a powerful cliffhanger regarding the signet ring. A cold viewer will easily understand the tension of the poisoning plot and the mystery of the protagonist's hidden identity, driving strong curiosity to see the next episode.]
> - **openai (gpt-6-luna):** PASS - The poisoning accusation is answered almost immediately—Juliana confirms it and says the Duchess is safe—so that hook loses its tension. The ring ques
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip establishes high stakes and clear emotional resonance immediately, culminating in a powerful cliffhanger regarding the signet ring. A cold vi
>
> **Risks:** The poisoning thread is effectively resolved within the opening seconds.; Reliance on the viewer noticing the signet ring detail amidst the dialogue; The ring’s significance is not explained; viewers must trust the Duchess’s shock and urgent question.; The key reveal relies on the ring being visually distinct and readable in a brief close-up.

---

### Rank 11: new:poisoning_discovery (single episode)
- **Episode(s):** Episode 23
- **Segments:** [01:19.00 → 02:11.20] (52.2s) | **Total:** 52.2s
- **Score:** 6.44 / 10 (raw 6.44) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 7.0, clarity 7.0
- **Audit Tier:** Tier 1
- **Hook (new:poisoning_discovery):** `01:19.00` - *"Someone is poisoning her."*
- **Cliffhanger (new:approaching_intruder_at_door):** `02:11.20` - *"SFX: Loud, metallic clack of the door latch turning, followed by the slow creak of wood hinges."*
  - *Withheld:* Who is entering, what they will do, and whether Juliana can save the Duchess.
- **Why it works:** A blunt poisoning reveal gives the stakes immediately, then the turning latch makes the viewer wonder whether the culprit is coming in.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The poisoning is stated immediately, and the Duchess’s collapse makes the stakes legible; the cure is only being prepared, not shown to work. The approaching person is unidentified and the door opening cuts off before we see who it is, creating a clear next-moment question, though the opening “her” has a brief referential ambiguity for cold viewers.] | [gemini-3.5-flash-lite: The clip establishes high medical and physical stakes immediately through the poisoning discovery and tense race to brew an antidote. The closing door latch creates a powerful, high-anxiety cliffhanger that forces viewers to want to know who is entering and whether they can finish the cure.]
> - **openai (gpt-6-luna):** PASS - The poisoning is stated immediately, and the Duchess’s collapse makes the stakes legible; the cure is only being prepared, not shown to work. The appr
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip establishes high medical and physical stakes immediately through the poisoning discovery and tense race to brew an antidote. The closing door
>
> **Risks:** The threat relies partly on door and sound effects, but Prudence’s warning also communicates that someone is coming.; Dialogue pronoun usage ('Someone is poisoning her') lacks explicit naming of the target, though visual context makes it clear she is treating the Duchess.; The first line’s “her” is briefly unexplained, though the Duchess’s collapse clarifies the reference moments later.

---

### Rank 12: new:ceremony_interruption (single episode)
- **Episode(s):** Episode 45
- **Segments:** [01:26.50 → 02:01.75] (35.2s) | **Total:** 35.2s
- **Score:** 6.32 / 10 (raw 6.32) | conversion intent: 8.0/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 7.0, injustice 8.0, clarity 8.0
- **Audit Tier:** Tier 1
- **Hook (new:ceremony_interruption):** `01:28.40` - *"No one will bow yet!"*
- **Cliffhanger (new:antagonist_triumph_before_countermove):** `02:01.75` - *"ACTION: Catherine raises her chin, a vindictive smirk spreading across her lips as she realizes her rival's claim has just been torn to pieces."*
  - *Withheld:* Whether Alexander will challenge the ruling and protect Juliana's claim as his wife and Duchess.
- **Why it works:** The interruption instantly turns a public triumph into a legal crisis, then ends on the antagonist's apparent victory before Alexander can respond.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The opening door slam and immediate order create a clear interruption, and the proclamation makes the stakes legible even without prior context. It does reveal that the marriage is being declared invalid, but cuts before Alexander or Juliana can respond, leaving the counter-move as a credible reason to continue.] | [gemini-3.5-flash-lite: The clip establishes an immediate, high-stakes crisis with the wedding being invalidated by religious and state authority, creating a strong curiosity gap regarding how the protagonists will retaliate. The ending cuts on the antagonist's triumphant smirk, forcing the viewer to want to see the countermove.]
> - **openai (gpt-6-luna):** PASS - The opening door slam and immediate order create a clear interruption, and the proclamation makes the stakes legible even without prior context. It do
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip establishes an immediate, high-stakes crisis with the wedding being invalidated by religious and state authority, creating a strong curiosity
>
> **Risks:** The legal ruling answers the immediate question of whether the marriage is recognized, reducing some suspense.; Relies on the viewer understanding medieval/noble wedding tropes instantly; Catherine's relationship to Juliana is unexplained, though her triumphant reaction is readable from context.; Pacing starts with a door slam rather than spoken dialogue in the very first second

---

### Rank 13: new:wartime_massacre_revelation (single episode)
- **Episode(s):** Episode 35
- **Segments:** [01:41.50 → 02:09.50] (28.0s) | **Total:** 28.0s
- **Score:** 6.2 / 10 (raw 6.2) | conversion intent: 7.5/10
- **Components:** hook 7.0, cliffhanger 8.0, payoff withheld 9.0, injustice 7.0, clarity 7.0
- **Payoff Location:** `Ep 35 02:25.50`
- **Audit Tier:** Tier 1
- **Hook (new:wartime_massacre_revelation):** `01:41.50` - *"My men were slaughtered."*
- **Cliffhanger (new:unknown_conspirator):** `02:09.50` - *"Because someone wanted you to believe I was dead."*
  - *Withheld:* Who arranged the ambush and kept Alexander's family believing he was dead.
- **Why it works:** The massacre lands immediately, then the story turns it into a personal conspiracy and cuts before Alexander names the people behind it.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The opening line immediately signals a massacre, and the dialogue makes Alexander’s survival and the unresolved question of who wanted him presumed dead understandable without prior context. The answer is withheld at the final “Who?”, leaving a clear curiosity gap; the emotional weight does rely somewhat on the close-ups and performed intensity.] | [gemini-3.5-flash-lite: The clip maintains a strong curiosity gap by framing a conspiracy involving the protagonist's survival, effectively drawing the viewer into the mystery of who betrayed him. The emotional stakes are clear and immediate, successfully pivoting from a personal tragedy to a larger political intrigue.]
> - **openai (gpt-6-luna):** PASS - The opening line immediately signals a massacre, and the dialogue makes Alexander’s survival and the unresolved question of who wanted him presumed de
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip maintains a strong curiosity gap by framing a conspiracy involving the protagonist's survival, effectively drawing the viewer into the myster
>
> **Risks:** The emotional payoff relies heavily on the mother's reaction shot at the very end.; The clip gives little context for Alexander’s relationship to the people who sought him, though the immediate mystery remains legible.; The dramatic impact depends partly on the actor’s close-up performance.; Potential risk that the 'soldier' context is not visually established if the viewer hasn't seen the premise, though the dialogue is self-explanatory.

---

### Rank 14: new:fire_trap_peril (single episode)
- **Episode(s):** Episode 18
- **Segments:** [00:03.50 → 00:41.80] (38.3s) | **Total:** 38.3s
- **Score:** 6.16 / 10 (raw 6.16) | conversion intent: 7.5/10
- **Components:** hook 8.0, cliffhanger 8.0, payoff withheld 9.0, injustice 4.0, clarity 8.0
- **Payoff Location:** `Ep 18 01:51.50`
- **Audit Tier:** Tier 1
- **Hook (new:fire_trap_peril):** `00:03.50` - *"Juliana coughs, her eyes widening in immediate alarm as the smell of burning wood fills her lungs."*
- **Cliffhanger (new:trapped_in_fire):** `00:41.80` - *"We cannot get through!"*
  - *Withheld:* Whether Alexander can find another way to get them out of the burning cottage.
- **Why it works:** It opens on immediate physical danger, then cuts as the couple discovers their escape route is blocked.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The danger is clear from the opening cough and smoke, and the clip ends with Juliana and Alexander still trapped—there is no resolution leak. The fire peril is compelling but generic, so a cold viewer may be curious about their escape without yet seeing why this moment connects to the broader show.] | [gemini-3.5-flash-lite: The clip maintains high tension by establishing immediate danger and isolating the protagonists, effectively using the fire as a ticking-clock mechanism. It avoids resolution leaks by ending at the peak of the impasse, successfully forcing the viewer to wonder how they will escape.]
> - **openai (gpt-6-luna):** PASS - The danger is clear from the opening cough and smoke, and the clip ends with Juliana and Alexander still trapped—there is no resolution leak. The fire
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip maintains high tension by establishing immediate danger and isolating the protagonists, effectively using the fire as a ticking-clock mechani
>
> **Risks:** Suspense depends on the fire and smoke reading clearly on screen.; Pacing relies on the urgency of the actors' screams; High dependency on production quality of fire effects; The payoff is an imminent escape question, not a show-specific mystery or relationship hook.

---

### Rank 15: Intimate Betrayal / Public Abandonment (single episode)
- **Episode(s):** Episode 1
- **Segments:** [00:39.10 → 01:10.40] (31.3s) | **Total:** 31.3s
- **Score:** 5.82 / 10 (raw 7.1) (diversity x0.82) | conversion intent: 7.5/10
- **Components:** hook 9.0, cliffhanger 7.0, payoff withheld 8.0, injustice 9.0, clarity 9.0
- **Payoff Location:** `Ep 1 01:10.60`
- **Audit Tier:** Tier 1
- **Hook (intimate_betrayal):** `00:39.10` - *"Because he is marrying me."*
- **Cliffhanger (new:unanswered_betrayal_question):** `01:10.40` - *"And you knew?"*
  - *Withheld:* Whether Clarissa knew about and participated in Gerald's betrayal; the next beat answers her.
- **Why it works:** The betrayal is unmistakable from the opening line, then Juliana's question makes the viewer wait for proof of how long her sister has known.

> **Audit (llm): PASS.** [Both pass] [gpt-6-luna: The wedding betrayal is clear within the opening seconds, and Juliana's final accusation leaves a charged beat unanswered. The sister's smugness makes her likely complicity fairly obvious, so the cliffhanger is more about her confirming it than a genuinely uncertain reveal.] | [gemini-3.5-flash-lite: The clip hits an immediate, clear public wedding betrayal within the first 3 seconds and escalates dramatic tension without resolving Juliana's plight or revealing her next step.]
> - **openai (gpt-6-luna):** PASS - The wedding betrayal is clear within the opening seconds, and Juliana's final accusation leaves a charged beat unanswered. The sister's smugness makes
> - **gemini (gemini-3.5-flash-lite):** PASS - The clip hits an immediate, clear public wedding betrayal within the first 3 seconds and escalates dramatic tension without resolving Juliana's plight
>
> **Risks:** The opening line's “he” briefly lacks context until the altar scene clarifies the stakes.; The sister's answer is strongly implied by her earlier mocking response and expression.; Slight dialogue repetition where Juliana accuses her sister of knowing early on and ends on the same realization.

---
