import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { ASSETS_DIR, listEpisodes, parseBeats } from "@/lib/kuku";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const episodes = listEpisodes();
    if (episodes.length === 0) {
      return NextResponse.json({ error: "No screenplay files found" }, { status: 404 });
    }

    const requested = searchParams.get("ep");
    const epNum = requested ? parseInt(requested, 10) : episodes[0].number;
    const target = episodes.find((e) => e.number === epNum);
    if (!target) {
      return NextResponse.json({ error: `Episode ${requested} not found` }, { status: 404 });
    }

    const content = fs.readFileSync(path.join(ASSETS_DIR, target.filename), "utf-8");
    const loglineMatch = content.match(/EPISODE LOGLINE:\s*([\s\S]*?)(?=\nCONTINUITY NOTES:|\n---|\nSCENE)/);
    const beats = parseBeats(content);

    return NextResponse.json({
      episodeNumber: target.number,
      filename: target.filename,
      logline: loglineMatch ? loglineMatch[1].trim() : "",
      beatsCount: beats.length,
      beats,
      episodes,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
