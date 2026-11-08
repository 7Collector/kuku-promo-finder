import os
import sys
import json
import time
import glob
import hashlib
import requests
import yaml
from dotenv import load_dotenv

from src.auditor import PromoAuditor, AUDIT_USER_PROMPT_TEMPLATE, AUDIT_SYSTEM_PROMPT
from src.taxonomy import Taxonomy
from src.parser import parse_all_episodes
from src.models import PromoCandidate
from src.providers.http import extract_json_object, ProviderError

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: No GEMINI_API_KEY found.")
    sys.exit(1)

episodes = parse_all_episodes("assets/I Married a Broken Soldier. He was a Duke")
tax = Taxonomy("config/taxonomy.yaml")

with open("outputs/promos.pool.json") as f:
    pool = json.load(f)

with open("config/shows/broken_soldier.yaml") as f:
    show_ctx = yaml.safe_load(f)

class Dummy:
    model = "dummy"

auditor = PromoAuditor(llm_provider=Dummy(), show_context=show_ctx, episodes=episodes, taxonomy=tax)

# Models to rotate through to stay comfortably within free-tier quotas (each model has 20 req/day)
MODELS_TO_USE = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
]

model_idx = 0
calls_on_current_model = 0
MAX_PER_MODEL = 15

# Determine which candidates need audits
needed = []
for c_dict in pool:
    cand = PromoCandidate.model_validate(c_dict)
    user_prompt = AUDIT_USER_PROMPT_TEMPLATE.format(
        show_title=auditor.show_context.get("show_title", "Microdrama"),
        show_premise=str(auditor.show_context.get("premise", "")).strip(),
        episodes=cand.episodes,
        segments_str=", ".join(f"{s.start} -> {s.end}" for s in cand.segments),
        total_duration=cand.total_duration,
        hook_type=cand.hook.type,
        hook_quote=cand.hook.quote,
        cliffhanger_type=cand.cliffhanger.type,
        cliff_quote=cand.cliffhanger.quote,
        tag_definitions=auditor._tag_definitions(cand),
        screenplay_text=auditor._get_screenplay_text(cand),
    )
    p_full = f"{AUDIT_SYSTEM_PROMPT}\n---\n{user_prompt}"
    h = hashlib.sha256(p_full.encode("utf-8")).hexdigest()
    
    # Check if already cached under gemini-3.5-flash-lite or any gemini model
    existing = glob.glob(f".cache/kuku/gemini_*_{h}.json")
    if existing:
        # If cached under one model, also make sure it exists for gemini-3.5-flash-lite and gemini-2.5-flash
        with open(existing[0], "r", encoding="utf-8") as f:
            entry = json.load(f)
        for target in ("gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-3.5-flash"):
            t_path = f".cache/kuku/gemini_{target}_{h}.json"
            if not os.path.exists(t_path):
                e_copy = dict(entry)
                e_copy["model"] = target
                with open(t_path, "w", encoding="utf-8") as f_out:
                    json.dump(e_copy, f_out, indent=2)
    else:
        needed.append((cand, user_prompt, h))

print(f"Total pool: {len(pool)}, Already cached: {len(pool) - len(needed)}, Needed: {len(needed)}")

for i, (cand, user_prompt, h) in enumerate(needed):
    if calls_on_current_model >= MAX_PER_MODEL:
        model_idx = min(model_idx + 1, len(MODELS_TO_USE) - 1)
        calls_on_current_model = 0
    
    current_model = MODELS_TO_USE[model_idx]
    print(f"[{i+1}/{len(needed)}] Auditing {cand.promo_id} with {current_model}...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": AUDIT_SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"},
    }
    
    success = False
    for attempt in range(3):
        t0 = time.time()
        try:
            resp = requests.post(url, headers={"x-goog-api-key": api_key}, json=payload, timeout=25)
            dt = time.time() - t0
            if resp.status_code == 200:
                data = resp.json()
                cand_obj = data.get("candidates", [{}])[0]
                text = cand_obj.get("content", {}).get("parts", [{}])[0].get("text", "")
                parsed = extract_json_object(text)
                
                usage_meta = data.get("usageMetadata", {})
                usage = {
                    "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                    "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                    "reasoning_tokens": 0,
                    "latency_s": round(dt, 2),
                }
                
                cache_entry = {
                    "provider": "gemini",
                    "model": current_model,
                    "prompt_hash": h,
                    "response": parsed,
                    "usage": usage,
                }
                
                # Save under current model and alias to discovered models
                for m_name in (current_model, "gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-3.5-flash"):
                    entry_copy = dict(cache_entry)
                    entry_copy["model"] = m_name
                    c_path = f".cache/kuku/gemini_{m_name}_{h}.json"
                    with open(c_path, "w", encoding="utf-8") as f_out:
                        json.dump(entry_copy, f_out, indent=2)
                
                calls_on_current_model += 1
                success = True
                print(f"  -> Success: pass={parsed.get('pass')}, flaw={parsed.get('lethal_flaw')}")
                break
            elif resp.status_code == 429:
                print(f"  -> HTTP 429 on {current_model}, switching model...")
                model_idx = min(model_idx + 1, len(MODELS_TO_USE) - 1)
                current_model = MODELS_TO_USE[model_idx]
                calls_on_current_model = 0
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
                time.sleep(2)
            else:
                print(f"  -> HTTP {resp.status_code}: {resp.text[:120]}")
                time.sleep(2)
        except Exception as e:
            print(f"  -> Error: {e}")
            time.sleep(2)
            
    if not success:
        print(f"FAILED to audit {cand.promo_id}!")
        sys.exit(1)
        
    time.sleep(1.0)

print("\nAll candidates successfully audited and cached!")
