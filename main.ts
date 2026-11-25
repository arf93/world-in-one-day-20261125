// World in One Day — Wednesday 25 November 2026 (make.fun news-image-20261125)
//
// Copies the entry picture this repository holds (entry.png, 1024x1024,
// under 1 MiB) to the output directory. Node 22, standard library only.
// Runs with no network and writes the same bytes on every run.

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const target = join(outDir, "entry.png");

const bytes = readFileSync(source);

if (bytes.length > MAX_BYTES) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file");
}
// IHDR: width at bytes 16-19, height at bytes 20-23, big-endian.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}

mkdirSync(outDir, { recursive: true });
writeFileSync(target, bytes);

// Read back and confirm the copy is byte-identical.
const written = readFileSync(target);
if (!written.equals(bytes)) {
  throw new Error("entry.png copy differs from the source");
}
console.log(`wrote ${target} (${bytes.length} bytes, 1024x1024 PNG)`);
