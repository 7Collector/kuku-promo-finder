import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const hasGeminiKey = Boolean(process.env.GEMINI_API_KEY);
  const hasOpenaiKey = Boolean(process.env.OPENAI_API_KEY);

  return NextResponse.json({
    hasGeminiKey,
    hasOpenaiKey,
    defaultProvider: hasGeminiKey ? "gemini" : hasOpenaiKey ? "openai" : "heuristic",
  });
}
