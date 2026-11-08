import { NextResponse } from "next/server";
import {
  parseUploadFiles,
  parseEpisodeScreenplay,
  runPipelineOnEpisodes,
  exportPromosToCSV,
  Episode,
} from "@/lib/pipeline";

export const dynamic = "force-dynamic";
export const maxDuration = 60; // Allows up to 60s if on Pro / supports max time allowed by platform

export async function POST(request: Request) {
  try {
    const contentType = request.headers.get("content-type") || "";
    let episodes: Episode[] = [];
    let provider: "gemini" | "openai" | "heuristic" = "gemini";
    let model: string | undefined;
    let apiKey: string | undefined;
    let showTitle: string | undefined;
    let showPremise: string | undefined;
    let topK: number = 15;
    let format: string = "json";

    if (contentType.includes("multipart/form-data")) {
      const formData = await request.formData();
      const files: { filename: string; buffer: Buffer }[] = [];

      for (const [key, value] of formData.entries()) {
        if (key === "provider") provider = value as any;
        else if (key === "model") model = String(value);
        else if (key === "apiKey") apiKey = String(value);
        else if (key === "showTitle") showTitle = String(value);
        else if (key === "showPremise") showPremise = String(value);
        else if (key === "topK") topK = parseInt(String(value), 10) || 15;
        else if (key === "format") format = String(value);
        else if (typeof value !== "string" && value && "arrayBuffer" in value) {
          const file = value as any;
          const arrayBuf = await file.arrayBuffer();
          files.push({
            filename: file.name || "screenplay.txt",
            buffer: Buffer.from(arrayBuf),
          });
        }
      }

      // Check if text was pasted directly in form
      const pastedScript = formData.get("screenplayText");
      if (pastedScript && typeof pastedScript === "string" && pastedScript.trim().length > 0) {
        const ep = parseEpisodeScreenplay(pastedScript, "pasted_screenplay.txt");
        if (ep.beats.length > 0) episodes.push(ep);
      }

      if (files.length > 0) {
        const parsed = await parseUploadFiles(files);
        episodes.push(...parsed);
      }
    } else {
      // JSON body
      const body = await request.json();
      provider = body.provider || "gemini";
      model = body.model;
      apiKey = body.apiKey;
      showTitle = body.showTitle;
      showPremise = body.showPremise;
      topK = body.topK || 15;
      format = body.format || "json";

      if (body.episodes && Array.isArray(body.episodes)) {
        for (const item of body.episodes) {
          const ep = parseEpisodeScreenplay(item.content || "", item.filename || "episode.txt");
          if (ep.beats.length > 0) episodes.push(ep);
        }
      } else if (body.screenplayText && typeof body.screenplayText === "string") {
        const ep = parseEpisodeScreenplay(body.screenplayText, "pasted_screenplay.txt");
        if (ep.beats.length > 0) episodes.push(ep);
      }
    }

    if (episodes.length === 0) {
      return NextResponse.json(
        {
          error:
            "No valid screenplays found. Please upload .txt files, a .zip archive, or paste screenplay text in standard format (**SPEAKER (emotion):** Start: mm:ss.ss | End: mm:ss.ss).",
        },
        { status: 400 }
      );
    }

    // Resolve API Key from environment if not provided by caller
    if (!apiKey) {
      if (provider === "gemini" && process.env.GEMINI_API_KEY) {
        apiKey = process.env.GEMINI_API_KEY;
      } else if (provider === "openai" && process.env.OPENAI_API_KEY) {
        apiKey = process.env.OPENAI_API_KEY;
      }
    }

    // If still no API key and an LLM provider was requested, fallback to heuristic or warn
    if (!apiKey && provider !== "heuristic") {
      // If no API key is configured at all in Vercel or input, fallback to heuristic smoke test
      provider = "heuristic";
    }

    const result = await runPipelineOnEpisodes(episodes, {
      provider,
      model,
      apiKey,
      showTitle,
      showPremise,
      topK,
    });

    if (format === "csv") {
      const csvData = exportPromosToCSV(result.ranked_promos);
      return new Response(csvData, {
        headers: {
          "Content-Type": "text/csv; charset=utf-8",
          "Content-Disposition": 'attachment; filename="custom_promos.csv"',
        },
      });
    }

    return NextResponse.json({
      ok: true,
      show_title: showTitle || "Custom Microdrama",
      episodes_analyzed: episodes.length,
      total_beats: episodes.reduce((a, e) => a + e.beats.length, 0),
      ranked_promos: result.ranked_promos,
      pool: result.pool,
      rejected: result.rejected,
      meta: result.meta,
    });
  } catch (error: any) {
    console.error("Pipeline analysis error:", error);
    return NextResponse.json(
      { error: error.message || "An unexpected error occurred during pipeline execution." },
      { status: 500 }
    );
  }
}
