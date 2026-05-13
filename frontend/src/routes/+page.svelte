<script>
  let companies = $state([]);
  let search = $state('');
  let loading = $state(true);
  let error = $state('');

  async function load() {
    try {
      const res = await fetch('/api/companies');
      if (!res.ok) throw new Error('Failed to load');
      companies = await res.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  load();

  let filtered = $derived(
    companies.filter(c =>
      c.company_name?.toLowerCase().includes(search.toLowerCase())
    )
  );
</script>

<div class="page">
  <div class="header">
    <h1>Companies</h1>
    <input type="text" placeholder="Search companies..." bind:value={search} />
    <span class="count">{filtered.length} of {companies.length}</span>
  </div>

  {#if loading}
    <p class="dim">Loading...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <div class="grid">
      {#each filtered as company}
        <a href="/company/{company.company_name}" class="card">
          <div class="card-header">
            <h2>{company.company_name}</h2>
          </div>
          {#if company.ratios}
            <div class="card-metrics">
              <div class="metric">
                <span class="label">Price</span>
                <span class="value">{company.stock_price}</span>
              </div>
              <div class="metric">
                <span class="label">Change</span>
                <span class="value" class:positive={company.percentage_change && !company.percentage_change.startsWith('-')} class:negative={company.percentage_change?.startsWith('-')}>
                  {company.percentage_change}
                </span>
              </div>
              <div class="metric">
                <span class="label">Mkt Cap</span>
                <span class="value">{company.ratios['Market Cap']}</span>
              </div>
              <div class="metric">
                <span class="label">P/E</span>
                <span class="value">{company.ratios['Stock P/E']}</span>
              </div>
            </div>
          {/if}
        </a>
      {/each}
    </div>
  {/if}
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 1.5rem; }
  .header { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
  .header h1 { font-size: 1.5rem; }
  .header input { flex: 1; min-width: 200px; }
  .count { color: var(--text-dim); font-size: 0.875rem; }
  .dim { color: var(--text-dim); }
  .error { color: var(--red); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem; }
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    transition: border-color .2s, transform .2s;
  }
  .card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .card-header h2 { font-size: 1rem; font-weight: 600; margin-bottom: .75rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .card-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
  .metric { display: flex; flex-direction: column; gap: .125rem; }
  .label { font-size: .7rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: .05em; }
  .value { font-size: .9rem; font-weight: 500; }
  .positive { color: var(--green); }
  .negative { color: var(--red); }
</style>
