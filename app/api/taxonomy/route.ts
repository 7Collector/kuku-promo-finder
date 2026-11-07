import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import YAML from "yaml";
import { readShowProfile } from "@/lib/kuku";

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), "config", "taxonomy.yaml");
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: "taxonomy.yaml not found" }, { status: 404 });
    }
    const taxonomy = YAML.parse(fs.readFileSync(filePath, "utf-8"));
    return NextResponse.json({ taxonomy, context: readShowProfile() });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
