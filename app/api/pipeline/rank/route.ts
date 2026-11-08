import { NextResponse } from "next/server";
import { rankCandidates, PromoCandidate } from "@/lib/pipeline";

export const dynamic = "force-dynamic";
export const maxDuration = 60; // Max allowed execution duration per route (Hobby ceiling 300s)

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const candidates: PromoCandidate[] = body.candidates || [];
    const topK: number = body.topK || 15;
    const weights = body.weights;

    const ranked = rankCandidates(candidates, topK, weights);

    return NextResponse.json({
      success: true,
      ranked_promos: ranked,
      total_candidates: candidates.length,
      top_k: topK,
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: `Ranking failed: ${err?.message || String(err)}` },
      { status: 500 }
    );
  }
}
