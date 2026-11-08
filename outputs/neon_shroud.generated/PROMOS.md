# Kuku Promo Finder - Ranked Promos
**Show:** Neo-Veridia: Neural Blackout  
**Generated:** 2026-11-07T15:40:41Z (commit 9223301)  
**Extractor:** openai / gpt-6-luna  
**Auditor:** gemini / gemini-3.5-flash-lite (LLM reads the clip screenplay)  
**Stages:** extraction, audit, auto_profile  
**Promos listed:** 3 of 3 candidates (0 passed audit, 3 failed, 0 unaudited)

---

## Hard rules enforced in code (see `src/validation.py`)
- Total duration 20-60s
- Hook beat starts within 3s of the opening cut; stakes legible in 3s
- Every cut is on a real beat edge; hook and cliffhanger quotes exist verbatim in the screenplay
- Audit-passing promos rank above audit-failing ones; repeated hook types/episodes are penalised

---

## Ranked Promos

### Rank 1: new:catastrophic_stakes_ultimatum (single episode)
- **Episode(s):** Episode 3
- **Segments:** [00:00.00 → 00:40.00] (40.0s) | **Total:** 40.0s
- **Score:** 4.55 / 10 (raw 5.83) (audit x0.78) | conversion intent: 6.5/10
- **Components:** hook 8.0, cliffhanger 7.0, payoff withheld 9.0, injustice 3.0, clarity 8.0
- **Audit Tier:** Tier 3
- **Hook (new:catastrophic_stakes_ultimatum):** `00:00.00` - *"Cut the main uplink or the entire sector goes dark!"*
- **Cliffhanger (new:life_or_death_sacrifice_decision):** `00:40.00` - *"Silas, don't do it!"*
  - *Withheld:* Whether Silas pulls the relay, stopping the sector-wide blackout at the cost of his neural heart.
- **Why it works:** It opens on an urgent citywide threat, then reveals the personal cost before cutting off at Kira's plea, with Silas's choice unresolved.

> **Audit (llm): FAIL - flaw: slow_burn.** The clip relies entirely on a prolonged ethical dilemma without introducing a fresh escalating action or plot twist within the first three seconds, leading to a slow burn that causes viewers to swipe away.
> - **gemini (gemini-3.5-flash-lite):** FAIL (slow_burn) - The clip relies entirely on a prolonged ethical dilemma without introducing a fresh escalating action or plot twist within the first three seconds, le
>
> **Risks:** Slow burn start; High reliance on shouting dialogue without immediate visual context

---

### Rank 2: new:syndicate_death_warning (single episode)
- **Episode(s):** Episode 1
- **Segments:** [00:08.00 → 00:45.00] (37.0s) | **Total:** 37.0s
- **Score:** 4.2 / 10 (raw 5.39) (audit x0.78) | conversion intent: 5.5/10
- **Components:** hook 7.0, cliffhanger 6.0, payoff withheld 8.0, injustice 5.0, clarity 7.0
- **Audit Tier:** Tier 3
- **Hook (new:syndicate_death_warning):** `00:08.00` - *"Silas, drop the badge. Syndicate leader Vance ordered everyone who saw this code silenced."*
- **Cliffhanger (new:imminent_confrontation_threat):** `00:45.00` - *"Tell Vance I am coming for his server farm next."*
  - *Withheld:* Whether Silas reaches Vance's server farm and what happens when he confronts him.
- **Why it works:** The warning makes Silas's danger clear immediately, then his answer promises a confrontation viewers have not seen.

> **Audit (llm): FAIL - flaw: wrong_tag.** The promo tags rely on unverified model-proposed types instead of standard platform taxonomy, and the tough-guy one-liners lack a compelling narrative mystery or open question that forces an immediate app install.
> - **gemini (gemini-3.5-flash-lite):** FAIL (wrong_tag) - The promo tags rely on unverified model-proposed types instead of standard platform taxonomy, and the tough-guy one-liners lack a compelling narrative
>
> **Risks:** Generic action dialogue fails to build a unique curiosity gap; Unstandardized taxonomy tags

---

### Rank 3: new:imminent_threat_trap (single episode)
- **Episode(s):** Episode 2
- **Segments:** [00:00.00 → 00:50.00] (50.0s) | **Total:** 50.0s
- **Score:** 3.6 / 10 (raw 5.43) (audit x0.663) | conversion intent: 6.5/10
- **Components:** hook 7.0, cliffhanger 8.0, payoff withheld 8.0, injustice 2.0, clarity 7.0
- **Audit Tier:** Tier 3
- **Hook (new:imminent_threat_trap):** `00:00.00` - *"You walked right into the kill zone, Detective."*
- **Cliffhanger (new:citywide_disaster_reveal):** `00:50.00` - *"The virus is already pulsing through the city grid. You are ten seconds too late."*
  - *Withheld:* Whether Silas can stop the virus from taking down the city grid.
- **Why it works:** It opens on a direct threat and ends with a citywide catastrophe already in motion, leaving Silas’s next move unresolved.

> **Audit (llm): FAIL - flaw: resolution_leak.** The clip completely gives away the climax of the confrontation by immediately revealing that the virus is already active and the protagonist has failed to stop it, leaving no active question about whether the trap succeeds.
> - **gemini (gemini-3.5-flash-lite):** FAIL (resolution_leak) - The clip completely gives away the climax of the confrontation by immediately revealing that the virus is already active and the protagonist has faile
>
> **Risks:** Resolution leak gives away the antagonist's success too early; Dialogue is somewhat generic cyberpunk cliché

---
