document.querySelectorAll('[data-paper-filter]').forEach(button => {
  button.addEventListener('click', () => {
    const filter = button.dataset.paperFilter;
    document.querySelectorAll('[data-paper-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    document.querySelectorAll('.paper').forEach(paper => { paper.hidden = filter !== 'All' && paper.dataset.type !== filter; });
  });
});

const repositoryList = document.querySelector('#repo-list');
if (repositoryList) {
  fetch('/data/activity.json').then(response => {
    if (!response.ok) throw new Error('Snapshot unavailable');
    return response.json();
  }).then(data => {
    repositoryList.replaceChildren();
    data.repositories.sort((a, b) => b.stars - a.stars || a.name.localeCompare(b.name)).forEach(repo => {
      const article = document.createElement('article');
      article.className = 'card';
      const heading = document.createElement('h3');
      const anchor = document.createElement('a');
      anchor.href = repo.url;
      anchor.textContent = repo.name;
      heading.append(anchor);
      const metadata = document.createElement('p');
      metadata.textContent = `${repo.language || 'Language not specified'} · ${repo.stars} stars · ${repo.forks} forks`;
      article.append(heading, metadata);
      repositoryList.append(article);
    });
    const note = document.createElement('p');
    note.className = 'meta';
    note.textContent = `Snapshot: ${data.updated.slice(0, 10)} UTC. Owned public repositories; forks excluded.`;
    repositoryList.after(note);
  }).catch(() => {
    repositoryList.textContent = 'The snapshot could not be loaded. Visit github.com/soz223 to view the repositories.';
  });
}
