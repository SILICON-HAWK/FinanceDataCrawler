<script>
  let { title = '', data = {}, columns = [] } = $props();
</script>

<div class="section">
  <h3 class="section-title">{title}</h3>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th></th>
          {#each Object.keys(data) as period}
            <th>{period}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each columns as col}
          <tr>
            <td class="row-label">{col}</td>
            {#each Object.values(data) as row}
              <td>{row[col] ?? '-'}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

<style>
  .section { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .section-title { font-size: .9rem; font-weight: 600; padding: .75rem 1rem; border-bottom: 1px solid var(--border); background: var(--bg-hover); }
  .table-wrap { overflow-x: auto; }
  .row-label { font-weight: 500; white-space: nowrap; color: var(--text-dim); position: sticky; left: 0; background: var(--bg-card); }
</style>
