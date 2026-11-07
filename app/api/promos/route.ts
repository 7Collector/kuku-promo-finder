import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const hookType = searchParams.get("hook");
    const promoType = searchParams.get("type");
    const minScore = parseFloat(searchParams.get("min_score") || "0");
    const query = (searchParams.get("q") || "").toLowerCase().trim();

    const filePath = path.join(process.cwd(), "outputs", "promos.json");
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: "promos.json not found" }, { status: 404 });
    }

    const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));

    let filtered = data;

    if (hookType && hookType !== "all") {
      filtered = filtered.filter((p: any) => p.hook?.type === hookType);
    }

    if (promoType && promoType !== "all") {
      filtered = filtered.filter((p: any) => p.promo_type === promoType);
    }

    if (minScore > 0) {
      filtered = filtered.filter(
        (p: any) =>
          (p.scores?.adjusted_score || p.scores?.composite_score || 0) >= minScore
      );
    }

    if (query) {
      filtered = filtered.filter((p: any) => {
        const text = (
          (p.hook?.quote || "") +
          " " +
          (p.cliffhanger?.quote || "") +
          " " +
          (p.why_it_works || "") +
          " " +
          (p.hook?.name || "")
        ).toLowerCase();
        return text.includes(query);
      });
    }

    return NextResponse.json({
      total: filtered.length,
      promos: filtered,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
