import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: "http://localhost:8000/openapi.json",
    output: {
      target: "./src/api/generated.ts",
      mode: "single",
      client: "react-query",
      override: {
        mutator: {
          path: "./src/api/client.ts",
          name: "client",
        },
        fetch: {
          includeHttpResponseReturnType: false,
        },
      },
    },
  },
  apiZod: {
    input: "http://localhost:8000/openapi.json",
    output: {
      target: "./src/api/schemas.ts",
      mode: "single",
      client: "zod",
    },
  },
});
