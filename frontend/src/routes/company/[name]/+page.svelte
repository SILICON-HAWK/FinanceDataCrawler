<script>
  import { page } from '$app/stores';
  import DataTable from '$lib/components/DataTable.svelte';
  import ShareholdingTable from '$lib/components/ShareholdingTable.svelte';

  let data = $state(null);
  let loading = $state(true);
  let error = $state('');

  let name = $derived($page.params.name);

  async function load() {
    try {
      const res = await fetch(`/api/companies?name=${encodeURIComponent(name)}`);
      if (!res.ok) throw new Error('Company not found');
      data = await res.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  load();

  let company = $derived(data?.company_data);
  let quarters = $derived(data?.quarters_data ?? {});
  let balanceSheet = $derived(data?.balance_sheet_data ?? {});
  let cashFlows = $derived(data?.cash_flows_data ?? {});
  let profitLoss = $derived(data?.profit_loss_data?.['Profit & Loss'] ?? {});
  let growth = $derived(data?.profit_loss_data?.['Compounded Growth'] ?? {});
  let ratiosData = $derived(data?.ratios_data ?? {});
  let shQ = $derived(data?.shareholding_data?.Quarterly ?? {});
  let shY = $derived(data?.shareholding_data?.Yearly ?? {});

  let qCols = ['Sales','Expenses','Operating Profit','OPM %','Other Income','Interest','Depreciation','Profit before tax','Tax %','Net Profit','EPS in Rs'];
  let bsCols = ['Equity Capital','Reserves','Borrowings','Other Liabilities','Total Liabilities','Fixed Assets','CWIP','Investments','Other Assets','Total Assets'];
  let cfCols = ['Cash from Operating Activity','Cash from Investing Activity','Cash from Financing Activity','Net Cash Flow'];
  let plCols = ['Sales','Expenses','Operating Profit','OPM %','Other Income','Interest','Depreciation','Profit before tax','Tax %','Net Profit','EPS in Rs'];
  let rCols = ['Debtor Days','Inventory Days','Days Payable','Cash Conversion Cycle','Working Capital Days','ROCE %'];
</script>

<div class="page">
  {#if loading}
    <p class="dim">Loading...</p>
  {:else if error}
    <p class="error">{error}</p>
    <a href="/" class="back">&larr; Back to companies</a>
  {:else if data}
    <a href="/" class="back">&larr; Back to companies</a>

    <div class="company-header">
      <div>
        <h1>{data.company_name}</h1>
        {#if company?.about_and_key_points}
          <p class="about">{company.about_and_key_points}</p>
        {/if}
      </div>
      {#if company?.ratios}
        <div class="price-card">
          <div class="price">{company.stock_price}</div>
          <div class="change" class:positive={company.percentage_change && !company.percentage_change.startsWith('-')} class:negative={company.percentage_change?.startsWith('-')}>
            {company.percentage_change}
          </div>
        </div>
      {/if}
    </div>

    {#if company?.ratios}
      <div class="ratios-bar">
        {#each Object.entries(company.ratios) as [key, val]}
          <div class="ratio-chip">
            <span class="rc-label">{key}</span>
            <span class="rc-value">{val}</span>
          </div>
        {/each}
      </div>
    {/if}

    {#if company?.company_links}
      <div class="links">
        <h3>Links</h3>
        <div class="link-list">
          {#each company.company_links as link}
            <a href={link} target="_blank" rel="noopener noreferrer">{new URL(link).hostname}</a>
          {/each}
        </div>
      </div>
    {/if}

    {#if Object.keys(quarters).length}
      <DataTable title="Quarterly Results" data={quarters} columns={qCols} />
    {/if}
    {#if Object.keys(balanceSheet).length}
      <DataTable title="Balance Sheet" data={balanceSheet} columns={bsCols} />
    {/if}
    {#if Object.keys(cashFlows).length}
      <DataTable title="Cash Flows" data={cashFlows} columns={cfCols} />
    {/if}
    {#if Object.keys(profitLoss).length}
      <DataTable title="Profit & Loss" data={profitLoss} columns={plCols} />
    {/if}
    {#if Object.keys(ratiosData).length}
      <DataTable title="Key Ratios" data={ratiosData} columns={rCols} />
    {/if}

    {#if Object.keys(growth).length}
      <div class="section">
        <h3 class="section-title">Compounded Growth</h3>
        <div class="growth-grid">
          {#each Object.entries(growth) as [label, periods]}
            <div class="growth-group">
              <h4>{label}</h4>
              <div class="growth-items">
                {#each Object.entries(periods) as [period, val]}
                  <div class="growth-item">
                    <span class="gi-period">{period}</span>
                    <span class="gi-value">{val}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    {#if Object.keys(shQ).length}
      <ShareholdingTable title="Shareholding Pattern (Quarterly)" data={shQ} />
    {/if}
    {#if Object.keys(shY).length}
      <ShareholdingTable title="Shareholding Pattern (Yearly)" data={shY} />
    {/if}
  {/if}
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 1.5rem; padding-bottom: 4rem; }
  .back { font-size: .875rem; color: var(--text-dim); }
  .back:hover { color: var(--accent); }
  .dim { color: var(--text-dim); }
  .error { color: var(--red); }
  .company-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 2rem; flex-wrap: wrap; }
  .company-header h1 { font-size: 1.5rem; }
  .about { margin-top: .5rem; color: var(--text-dim); font-size: .875rem; max-width: 800px; line-height: 1.7; }
  .price-card { text-align: right; flex-shrink: 0; }
  .price { font-size: 1.75rem; font-weight: 700; }
  .change { font-size: 1rem; font-weight: 500; }
  .positive { color: var(--green); }
  .negative { color: var(--red); }
  .ratios-bar { display: flex; flex-wrap: wrap; gap: .5rem; }
  .ratio-chip { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: .5rem .75rem; display: flex; flex-direction: column; gap: .125rem; font-size: .8rem; }
  .rc-label { color: var(--text-dim); font-size: .65rem; text-transform: uppercase; letter-spacing: .05em; }
  .rc-value { font-weight: 600; }
  .links { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; }
  .links h3 { font-size: .8rem; color: var(--text-dim); margin-bottom: .5rem; text-transform: uppercase; letter-spacing: .05em; }
  .link-list { display: flex; flex-wrap: wrap; gap: .5rem; }
  .link-list a { font-size: .8rem; background: var(--bg-hover); padding: .25rem .5rem; border-radius: 4px; border: 1px solid var(--border); }
  .section { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .section-title { font-size: .9rem; font-weight: 600; padding: .75rem 1rem; border-bottom: 1px solid var(--border); background: var(--bg-hover); }
  .growth-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; padding: 1rem; }
  .growth-group h4 { font-size: .8rem; color: var(--text-dim); margin-bottom: .5rem; text-transform: uppercase; letter-spacing: .05em; }
  .growth-items { display: flex; flex-direction: column; gap: .25rem; }
  .growth-item { display: flex; justify-content: space-between; padding: .25rem 0; font-size: .85rem; border-bottom: 1px solid var(--border); }
  .gi-period { color: var(--text-dim); }
  .gi-value { font-weight: 500; }
</style>
