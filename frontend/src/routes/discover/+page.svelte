<script>
  import { api } from '$lib/api.js';

  let status = $state(null);
  let loading = $state(false);
  let message = $state('');

  async function loadStatus() {
    try {
      status = await api.status();
    } catch (e) {
      message = e.message;
    }
  }

  async function runSectorDiscovery() {
    loading = true;
    message = '';
    try {
      const res = await api.discover.sectors();
      message = res.message;
      await loadStatus();
    } catch (e) {
      message = e.message;
    } finally {
      loading = false;
    }
  }

  async function runCompanyDiscovery() {
    loading = true;
    message = '';
    try {
      const res = await api.discover.companies(60);
      message = res.message;
      await loadStatus();
    } catch (e) {
      message = e.message;
    } finally {
      loading = false;
    }
  }

  loadStatus();
</script>

<div class="page">
  <h1>Discovery</h1>

  {#if status}
    <div class="stats">
      <div class="stat">
        <span class="stat-value">{status.pipeline.total_sectors}</span>
        <span class="stat-label">Sectors</span>
      </div>
      <div class="stat">
        <span class="stat-value">{status.pipeline.visited_sectors}</span>
        <span class="stat-label">Visited</span>
      </div>
      <div class="stat">
        <span class="stat-value">{status.pipeline.total_companies}</span>
        <span class="stat-label">Companies</span>
      </div>
    </div>
  {/if}

  <div class="actions">
    <button onclick={runSectorDiscovery} disabled={loading}>
      {loading ? 'Running...' : 'Discover Sectors'}
    </button>
    <button onclick={runCompanyDiscovery} disabled={loading}>
      {loading ? 'Running...' : 'Discover Companies'}
    </button>
  </div>

  {#if message}
    <p class="message">{message}</p>
  {/if}
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 1.5rem; }
  .stats { display: flex; gap: 1rem; }
  .stat { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.5rem; display: flex; flex-direction: column; gap: 0.25rem; }
  .stat-value { font-size: 1.5rem; font-weight: 700; }
  .stat-label { font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em; }
  .actions { display: flex; gap: 0.75rem; }
  .message { color: var(--text-dim); }
</style>
