import { NextResponse } from "next/server";
import { extractEpisodeCandidates, Episode } from "@/lib/pipeline";

export const dynamic = "force-dynamic";
export const maxDuration = 60; // Max allowed execution duration per route (Hobby ceiling 300s)

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const episode: Episode = body.episode;
    if (!episode || !Array.isArray(episode.beats)) {
      return NextResponse.json(
        { error: "Invalid episode payload: missing episode or beats array." },
        { status: 400 }
      );
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

    if (provider !== "heuristic" && !apiKey) {
      return NextResponse.json(
        {
          error: `Missing API key for ${provider}. Supply an apiKey in request or configure ${provider === "gemini" ? "GEMINI_API_KEY" : "OPENAI_API_KEY"} in environment.`,
        },
        { status: 401 }
      );
    }

    const result = await extractEpisodeCandidates(episode, {
      provider,
      model: body.model,
      apiKey,
      showTitle: body.showTitle,
      showPremise: body.showPremise,
    });

    return NextResponse.json({
      success: true,
      episode_number: result.episode_number,
      candidates: result.candidates,
      rejected: result.rejected,
    });
  } catch (err: any) {
    const status = err?.status || (err?.message?.includes("429") ? 429 : 500);
    return NextResponse.json(
      {
        error: `Extraction failed on episode: ${err?.message || String(err)}`,
        status,
      },
      { status }
    );
  }
}
