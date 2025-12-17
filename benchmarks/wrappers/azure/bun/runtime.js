/**
 * Custom server for Azure
 */

import { handler } from "./handler.js";

const PORT = parseInt(process.env.FUNCTIONS_CUSTOMHANDLER_PORT) || 3000;

console.log(`Starting Bun server on port ${PORT}...`);

Bun.serve({
  port: PORT,
  async fetch(req) {
    let body = null;
    if (req.body) {
      try {
        body = await req.json();
      } catch (e) {}
    }

    const context = {
      invocationId:
        req.headers.get("x-azure-functions-invocationid") || "unknown",
    };

    try {
      const result = await handler(req, context);

      return new Response(result.body, {
        status: result.statusCode || 200,
        headers: {
          "Content-Type": "application/json",
        },
      });
    } catch (error) {
      console.error(error);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
      });
    }
  },
});
