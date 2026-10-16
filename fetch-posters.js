// Downloads missing posters from TMDB into posters/.
// Usage: node fetch-posters.js [--force]
// Reads TMDB_API_KEY from .env. Accepts either the v3 API key or the v4 read access token.
const fs = require("fs");
const path = require("path");

const root = __dirname;
const force = process.argv.includes("--force");

function loadEnv() {
  const env = {};
  const file = path.join(root, ".env");
  if (!fs.existsSync(file)) return env;
  for (const line of fs.readFileSync(file, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m && !line.trim().startsWith("#")) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
  return env;
}

const secret = process.env.TMDB_API_KEY || loadEnv().TMDB_API_KEY;
if (!secret || secret === "paste_your_key_here") {
  console.error("Missing TMDB_API_KEY. Add it to .env first.");
  process.exit(1);
}

// Read access tokens are JWTs and start with "eyJ". v3 keys are 32 hex characters.
const isToken = secret.startsWith("eyJ");
const headers = isToken ? { Authorization: `Bearer ${secret}` } : {};

async function tmdb(endpoint, params) {
  const url = new URL(`https://api.themoviedb.org/3/${endpoint}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  if (!isToken) url.searchParams.set("api_key", secret);
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`TMDB ${res.status} ${res.statusText}`);
  return res.json();
}

const MOVIES = new Function(`${fs.readFileSync(path.join(root, "movies.js"), "utf8")}; return MOVIES;`)();

(async () => {
  fs.mkdirSync(path.join(root, "posters"), { recursive: true });

  for (const movie of MOVIES) {
    const file = path.join(root, movie.poster);
    if (fs.existsSync(file) && !force) {
      console.log(`skip     ${movie.title} (already have ${movie.poster})`);
      continue;
    }

    const { results } = await tmdb("search/movie", { query: movie.title, year: movie.year });
    const hit = results.find((r) => r.poster_path);
    if (!hit) {
      console.log(`no match ${movie.title} (${movie.year})`);
      continue;
    }

    const img = await fetch(`https://image.tmdb.org/t/p/w780${hit.poster_path}`);
    if (!img.ok) throw new Error(`Image download failed for ${movie.title}: ${img.status}`);
    fs.writeFileSync(file, Buffer.from(await img.arrayBuffer()));
    console.log(`saved    ${movie.title} -> ${movie.poster} (TMDB: ${hit.title}, ${hit.release_date})`);
  }
})().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
