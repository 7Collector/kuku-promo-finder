import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import YAML from "yaml";

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), "config", "taxonomy.yaml");
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: "taxonomy.yaml not found" }, { status: 404 });
    }

    const fileContent = fs.readFileSync(filePath, "utf-8");
    const parsed = YAML.parse(fileContent);

    const contextPath = path.join(process.cwd(), "config", "show_context.yaml");
    let showContext = {};
    if (fs.existsSync(contextPath)) {
      showContext = YAML.parse(fs.readFileSync(contextPath, "utf-8"));
    }

    return NextResponse.json({
      taxonomy: parsed,
      context: showContext,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
