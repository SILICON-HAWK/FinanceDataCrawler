<script>
  import { api } from '$lib/api.js';

  let companies = $state([]);
  let selected = $state([]);
  let status = $state(null);
  let running = $state(false);
  let message = $state('');

  async function loadCompanies() {
    const data = await api.companies.list();
    companies = data;
  }

  async function pollStatus() {
    status = await api.extract.status();
    running = status.running;
    if (running) {
      setTimeout(pollStatus, 2000);
    }
  }

  async function startExtraction() {
    message = '';
    const urls = selected.flatMap(s => s.urls.map(u => u.url));
    try {
      const res = await api.extract.start({ company_urls: urls.length ? urls : undefined });
      message = res.message;
      await pollStatus();
    } catch (e) {
      message = e.message;
    }
  }

  function toggleSector(sector) {
    if (selected.includes(sector)) {
      selected = selected.filter(s => s !== sector);
    } else {
      selected = [...selected, sector];
    }
  }

  loadCompanies();
</script>

<div class="page">
  <h1>Extraction</h1>

  {#if status}
    <div class="status-bar">
      <span class="badge" class:running={status.running}>
        {status.running ? 'Running' : 'Idle'}
      </span>
      {#if status.progress}
        <span class="phase">Phase: {status.progress.phase}</span>
      {/if}
      <span>Processed: {status.processed} / {status.total}</span>
    </div>
  {/if}

  <div class="sectors">
    <h2>Companies by Sector</h2>
    {#each Object.entries(companies) as [sectorName, urls]}
      <div class="sector-group">
        <label class="sector-header">
          <input type="checkbox" checked={selected.includes(sectorName)} onchange={() => toggleSector(sectorName)} />
          <strong>{sectorName}</strong>
          <span class="count">({urls.length})</span>
        </label>
      </div>
    {/each}
  </div>

  <button onclick={startExtraction} disabled={running || selected.length === 0}>
    {running ? 'Extracting...' : 'Start Extraction'}
  </button>

  {#if message}
    <p class="message">{message}</p>
  {/if}
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 1.5rem; }
  .status-bar { display: flex; align-items: center; gap: 1rem; padding: 0.75rem 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); }
  .badge { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: var(--bg-hover); }
  .running { background: #22c55e; color: white; }
  .phase { color: var(--text-dim); }
  .sector-group { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .sector-header { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1rem; background: var(--bg-card); cursor: pointer; }
  .count { color: var(--text-dim); font-size: 0.8rem; }
  .message { color: var(--text-dim); }
</style>
