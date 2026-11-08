import { NextResponse } from "next/server";
import {
  parseUploadFiles,
  parseEpisodeScreenplay,
  Episode,
} from "@/lib/pipeline";

export const dynamic = "force-dynamic";
export const maxDuration = 60; // Verified Hobby ceiling is 300s (source: https://vercel.com/docs/functions/limitations)

const VERCEL_MAX_BODY_BYTES = 4.5 * 1024 * 1024; // 4.5 MB = 4,718,592 bytes

export async function POST(request: Request) {
  try {
    const contentLength = request.headers.get("content-length");
    if (contentLength && parseInt(contentLength, 10) > VERCEL_MAX_BODY_BYTES) {
      return NextResponse.json(
        {
          error:
            "Upload payload exceeds Vercel's 4.5 MB request body limit (source: https://vercel.com/docs/functions/limitations). Please split your zip file into smaller batches or paste individual episodes.",
        },
        { status: 413 }
      );
    }

    const contentType = request.headers.get("content-type") || "";
    const episodes: Episode[] = [];

    if (contentType.includes("multipart/form-data")) {
      const formData = await request.formData();
      const files: { filename: string; buffer: Buffer }[] = [];
      let totalBytes = 0;

      for (const [key, value] of formData.entries()) {
        if (typeof value !== "string" && value && "arrayBuffer" in value) {
          const file = value as any;
          const arrayBuf = await file.arrayBuffer();
          totalBytes += arrayBuf.byteLength;
          if (totalBytes > VERCEL_MAX_BODY_BYTES) {
            return NextResponse.json(
              {
                error:
                  "Upload payload exceeds Vercel's 4.5 MB request body limit (source: https://vercel.com/docs/functions/limitations). Please split your zip file into smaller batches or paste individual episodes.",
              },
              { status: 413 }
            );
          }
          files.push({
            filename: file.name || "screenplay.txt",
            buffer: Buffer.from(arrayBuf),
          });
        }
      }

      // Check for pasted text
      const pastedScript = formData.get("screenplayText");
      if (
        pastedScript &&
        typeof pastedScript === "string" &&
        pastedScript.trim().length > 0
      ) {
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
      const text = body.screenplayText || body.text;
      if (text && typeof text === "string") {
        const ep = parseEpisodeScreenplay(text, body.filename || "pasted_screenplay.txt");
        if (ep.beats.length > 0) episodes.push(ep);
      }
    }

    if (episodes.length === 0) {
      return NextResponse.json(
        {
          error:
            "No valid screenplay episodes could be parsed. Ensure files follow the standard beat format (**SPEAKER:** Start: (mm:ss.ss) | End: (mm:ss.ss)).",
        },
        { status: 400 }
      );
    }

    episodes.sort((a, b) => a.episode_number - b.episode_number);
    const totalBeats = episodes.reduce((acc, ep) => acc + ep.beats.length, 0);

    return NextResponse.json({
      success: true,
      total_episodes: episodes.length,
      total_beats: totalBeats,
      episodes,
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: `Parsing failed: ${err?.message || String(err)}` },
      { status: 500 }
    );
  }
}
