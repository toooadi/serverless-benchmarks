import fs from "node:fs";
import path from "node:path";
import * as func from "./function.js";

export async function handler(req) {
  const begin = Date.now() / 1000;
  const start = process.hrtime();
  let input_data = {};
  try {
    if (req.body) {
      input_data = await req.json();
    }
  } catch (e) {
    console.error("Failed to parse JSON body:", e);
  }

  const result = await func.handler(input_data);

  const elapsed = process.hrtime(start);
  const end = Date.now() / 1000;
  const micro = elapsed[1] / 1e3 + elapsed[0] * 1e6;

  let is_cold = false;
  const fname = path.join("/tmp", "cold_run");
  if (!fs.existsSync(fname)) {
    is_cold = true;
    fs.closeSync(fs.openSync(fname, "w"));
  }

  const responseData = {
    begin: begin,
    end: end,
    compute_time: micro,
    results_time: 0,
    result: { output: result },
    is_cold: is_cold,
    request_id: req.headers.get("function-execution-id") || "unknown",
  };

  return new Response(JSON.stringify(responseData), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
