/**
 * Custom server for GCP
 *
 * Based on https://docs.cloud.google.com/run/docs/container-contract
 */

import { handler } from "./handler.js";

const PORT = parseInt(process.env.PORT) || 8080;

Bun.serve({
  port: PORT,

  async fetch(req) {
    try {
      return await handler(req);
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), {
        status: 500,
      });
    }
  },
});

console.log(`Listening on port ${PORT}`);
