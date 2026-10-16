const grid = document.getElementById("grid");
const empty = document.getElementById("empty");
const search = document.getElementById("search");
const dialog = document.getElementById("details");
const detailsBody = document.getElementById("details-body");

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function posterEl(movie) {
  const img = el("img", "poster");
  img.src = movie.poster;
  img.alt = `${movie.title} poster`;
  img.loading = "lazy";
  return img;
}

function cardEl(movie) {
  const card = el("button", "card");

  const frame = el("div", "poster-frame");
  frame.append(posterEl(movie));

  const caption = el("div", "caption");
  caption.append(el("div", "t", movie.title), el("div", "y", movie.year));

  card.append(frame, caption);
  card.addEventListener("click", () => showDetails(movie));
  return card;
}

function showDetails(movie) {
  const info = el("div", "info");
  info.append(
    el("h2", "", movie.title),
    el("div", "year", movie.year),
    el("div", "director", "Directed by"),
    el("div", "director-name", movie.director),
    el("p", "", movie.blurb)
  );

  const wrap = el("div", "detail");
  wrap.append(posterEl(movie), info);
  detailsBody.replaceChildren(wrap);
  dialog.showModal();
}

// Oldest first, then alphabetical within a year
const SORTED = [...MOVIES].sort((a, b) => a.year - b.year || a.title.localeCompare(b.title));

function render() {
  const q = search.value.trim().toLowerCase();
  const matches = SORTED.filter((m) =>
    [m.title, m.year, m.director].join(" ").toLowerCase().includes(q)
  );
  grid.replaceChildren(...matches.map(cardEl));
  empty.hidden = matches.length > 0;
}

search.addEventListener("input", render);
document.getElementById("close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (e) => {
  if (e.target === dialog) dialog.close();
});

render();
