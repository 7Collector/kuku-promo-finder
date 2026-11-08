import { NextResponse } from "next/server";
import { auditCandidateBatch, PromoCandidate, Episode } from "@/lib/pipeline";

export const dynamic = "force-dynamic";
export const maxDuration = 60; // Max allowed execution duration per route (Hobby ceiling 300s)

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const candidates: PromoCandidate[] = body.candidates || [];
    const episodes: Episode[] = body.episodes || [];

    if (!Array.isArray(candidates) || candidates.length === 0) {
      return NextResponse.json({ success: true, audited_candidates: [] });
    }

    const provider: "gemini" | "openai" | "heuristic" = body.provider || "gemini";
    let apiKey: string | undefined = body.apiKey;

    // Use server-side keys by default if user-supplied key is not provided
    if (!apiKey) {
      if (provider === "gemini") {
        apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
      } else if (provider === "openai") {
        apiKey = process.env.OPENAI_API_KEY;
      }
    }

    const audited = await auditCandidateBatch(candidates, episodes, {
      provider,
      model: body.model,
      apiKey,
      showTitle: body.showTitle,
      showPremise: body.showPremise,
    });

    return NextResponse.json({
      success: true,
      audited_candidates: audited,
    });
  } catch (err: any) {
    const status = err?.status || (err?.message?.includes("429") ? 429 : 500);
    return NextResponse.json(
      {
        error: `Audit failed: ${err?.message || String(err)}`,
        status,
      },
      { status }
    );
  }
}
