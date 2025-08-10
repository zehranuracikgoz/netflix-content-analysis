async function fetchAndRenderList(apiUrl, containerId, listClass, itemLabel) {
  try {
    const res = await fetch(apiUrl);
    const data = await res.json();

    const box = document.getElementById(containerId);
    box.innerHTML = '';

    const ul = document.createElement('ul');
    ul.classList.add(listClass);

    Object.entries(data).forEach(([key, count]) => {
      const li = document.createElement('li');
      li.textContent = `${key} — ${count}`;
      ul.appendChild(li);
    });

    box.appendChild(ul);
  } catch (err) {
    console.error(`${itemLabel} verisi yüklenemedi:`, err);
  }
}

async function renderTopCountriesBox() {
  await fetchAndRenderList("/api/top-countries", "topCountriesBox", "country-list", "Ülke");
}

async function renderTopGenresBox() {
  await fetchAndRenderList("/api/top-genres", "topGenresBox", "genre-list", "Tür");
}

async function renderTopActorsBox() {
  await fetchAndRenderList("/api/top_actors", "topActorsBox", "actor-list", "Oyuncu");
}

async function renderTopDirectorsBox() {
  await fetchAndRenderList("/api/top_directors", "topDirectorsBox", "director-list", "Yönetmen");
}

async function renderRecentlyAdded() {
  try {
    const res = await fetch('/api/recently-added');
    const { results } = await res.json();
    const container = document.getElementById('recent-shows');

    container.innerHTML = '';

    results.slice(0, 10).forEach(show => {
      const date = new Date(show.date_added);
      const options = { month: 'long', year: 'numeric' };
      const formattedDate = date.toLocaleDateString('tr-TR', options);

      const showElement = document.createElement('div');
      showElement.className = 'show-card';
      showElement.innerHTML = `
        <h3>${show.title} (${show.release_year})</h3>
        <p class="show-type">${show.type}</p>
        <p class="show-date">Eklenme: ${formattedDate}</p>
        <p class="show-meta">
          <span>${show.rating}</span> • 
          <span>${show.duration}</span>
        </p>
        <div class="show-genres">
          ${show.genres.map(g => `<span>${g}</span>`).join(' ')}
        </div>
      `;
      container.appendChild(showElement);
    });

    const cardWidth = container.querySelector(".show-card").offsetWidth + 10;

    document.getElementById("nextBtn").addEventListener("click", () => {
      container.scrollBy({ left: cardWidth, behavior: "smooth" });
    });

    document.getElementById("prevBtn").addEventListener("click", () => {
      container.scrollBy({ left: -cardWidth, behavior: "smooth" });
    });

  } catch (err) {
    console.error("Hata:", err);
    document.getElementById('recent-shows').innerHTML =
      '<p class="error">İçerikler yüklenirken bir hata oluştu</p>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  renderTopCountriesBox();
  renderTopGenresBox();
  renderTopActorsBox();
  renderTopDirectorsBox();
  renderRecentlyAdded();

  const updateElem = document.getElementById('lastUpdate');
  if (updateElem) {
    updateElem.textContent = new Date().toLocaleDateString();
  }
});
