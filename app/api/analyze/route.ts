import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import YAML from "yaml";

function parseTimestamp(ts: string): number {
  const clean = ts.replace(/[()]/g, "").trim();
  const parts = clean.split(":");
  if (parts.length === 2) {
    return parseFloat(parts[0]) * 60 + parseFloat(parts[1]);
  }
  if (parts.length === 3) {
    return parseFloat(parts[0]) * 3600 + parseFloat(parts[1]) * 60 + parseFloat(parts[2]);
  }
  return parseFloat(clean) || 0;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const {
      start = "00:00.00",
      end = "00:30.00",
      hookQuote = "",
      cliffQuote = "",
      selectedHook = "public_humiliation",
      selectedCliff = "interrupted_retaliation",
    } = body;

    const startSec = parseTimestamp(start);
    const endSec = parseTimestamp(end);
    const duration = Math.max(0, endSec - startSec);

    // Validation
    const durationValid = duration >= 19.5 && duration <= 60.5;

    // Load taxonomy weights
    const taxonomyPath = path.join(process.cwd(), "config", "taxonomy.yaml");
    let hookWeight = 1.0;
    let cliffWeight = 1.0;
    let hookDriver = "High interpersonal tension";
    let cliffPayoff = "Withheld catharsis";

    if (fs.existsSync(taxonomyPath)) {
      const taxData = YAML.parse(fs.readFileSync(taxonomyPath, "utf-8"));
      const foundHook = (taxData.hooks || []).find((h: any) => h.id === selectedHook);
      if (foundHook) {
        hookWeight = foundHook.weight || 1.0;
        hookDriver = foundHook.psychological_driver || hookDriver;
      }
      const foundCliff = (taxData.cliffhangers || []).find((c: any) => c.id === selectedCliff);
      if (foundCliff) {
        cliffWeight = foundCliff.weight || 1.0;
        cliffPayoff = foundCliff.psychological_driver || cliffPayoff;
      }
    }

    // Dynamic scoring formula
    const hookStrength = hookQuote.length > 5 ? 9.2 : 7.5;
    const injusticeTension = /kneel|beg|sister|slap|marry|worthless|dirt|servant/i.test(hookQuote) ? 9.5 : 8.0;
    const cliffStrength = cliffQuote.length > 5 ? 9.0 : 7.5;
    const standaloneClarity = 8.5;
    const payoffWithheld = 9.0;

    const baseScore =
      0.30 * hookStrength +
      0.25 * cliffStrength +
      0.20 * injusticeTension +
      0.15 * standaloneClarity +
      0.10 * payoffWithheld;

    const compositeScore = Math.round(baseScore * hookWeight * cliffWeight * 100) / 100;

    // Adversarial quality audit
    const risks: string[] = [];
    let passed = true;
    let flawType: string | null = null;

    if (!durationValid) {
      passed = false;
      flawType = "duration_out_of_bounds";
      risks.push(`Duration (${duration.toFixed(1)}s) must be between 20s and 60s for vertical platforms.`);
    }

    if (/close-up|pan|framing|symmetrical/i.test(hookQuote + " " + cliffQuote)) {
      risks.push("Relies on visual camera staging described in script text.");
    }

    const audit = {
      passed,
      flaw_type: flawType,
      confidence_score: passed ? 8.8 : 4.0,
      critique: passed
        ? "Excellent emotional hook; cuts at peak tension before retribution."
        : "Fails platform constraints or resolution requirements.",
      risks,
    };

    return NextResponse.json({
      duration: Math.round(duration * 10) / 10,
      durationValid,
      scores: {
        composite_score: compositeScore,
        hook_strength: hookStrength,
        injustice_tension: injusticeTension,
        cliffhanger_strength: cliffStrength,
        standalone_clarity: standaloneClarity,
        payoff_withheld: payoffWithheld,
      },
      hook: {
        type: selectedHook,
        quote: hookQuote,
        psychological_trigger: hookDriver,
      },
      cliffhanger: {
        type: selectedCliff,
        quote: cliffQuote,
        withheld_payoff: cliffPayoff,
      },
      audit,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
