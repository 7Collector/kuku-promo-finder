import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const epNum = parseInt(searchParams.get("ep") || "1", 10);

    const assetDir = path.join(process.cwd(), "assets", "I Married a Broken Soldier. He was a Duke");
    if (!fs.existsSync(assetDir)) {
      return NextResponse.json({ error: "Assets directory not found" }, { status: 404 });
    }

    const files = fs.readdirSync(assetDir).filter((f) => f.endsWith(".txt"));
    files.sort();

    // Map list of episodes
    const episodeList = files.map((f, idx) => ({
      number: idx + 1,
      filename: f,
    }));

    // Find requested episode
    const targetFile = files[epNum - 1] || files[0];
    const fullPath = path.join(assetDir, targetFile);
    const content = fs.readFileSync(fullPath, "utf-8");

    // Quick parse of header
    const loglineMatch = content.match(/EPISODE LOGLINE:\s*([\s\S]*?)(?=\nCONTINUITY NOTES:|\n---|\nSCENE|\Z)/);
    const logline = loglineMatch ? loglineMatch[1].trim() : "";

    // Extract dialogue and action beats
    const beatMatches = Array.from(
      content.matchAll(/\*\*([^*]+)\*\*\s*\nStart:\s*\(?([0-9:.]+)\)?\s*\|\s*End:\s*\(?([0-9:.]+)\)?\s*\n([\s\S]*?)(?=\n\*\*[^*]+\*\*\s*\nStart:|\nSCENE\s+\d+|\Z)/g)
    );

    const beats = beatMatches.map((m) => {
      const rawHeader = m[1].trim().replace(/:$/, "");
      const isCamera = rawHeader.toUpperCase() === "CAMERA";
      const isAction = rawHeader.toUpperCase() === "ACTION";
      const isSound = /SOUND|SFX/i.test(rawHeader);

      let speaker: string | null = null;
      let emotion: string | null = null;

      if (!isCamera && !isAction && !isSound) {
        if (rawHeader.includes("(") && rawHeader.includes(")")) {
          const openIdx = rawHeader.indexOf("(");
          const closeIdx = rawHeader.lastIndexOf(")");
          speaker = rawHeader.substring(0, openIdx).trim();
          emotion = rawHeader.substring(openIdx + 1, closeIdx).trim();
        } else {
          speaker = rawHeader;
        }
      }

      return {
        type: isCamera ? "CAMERA" : isAction ? "ACTION" : isSound ? "SOUND" : "DIALOGUE",
        speaker,
        emotion,
        start: m[2].trim(),
        end: m[3].trim(),
        text: m[4].trim(),
      };
    });

    return NextResponse.json({
      episodeNumber: epNum,
      filename: targetFile,
      logline,
      beatsCount: beats.length,
      beats,
      episodes: episodeList,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
