<script>
  let { title = '', data = {} } = $props();
  let categories = $derived(Object.keys(data));
  let periods = $derived(categories.length > 0 ? Object.keys(data[categories[0]]) : []);
  let colors = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#06b6d4'];
</script>

<div class="section">
  <h3 class="section-title">{title}</h3>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Category</th>
          {#each periods as p}
            <th>{p}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each categories as cat, i}
          <tr>
            <td class="row-label">
              <span class="dot" style="background: {colors[i % colors.length]}"></span>
              {cat}
            </td>
            {#each periods as p}
              <td>{data[cat]?.[p] ?? '-'}</td>
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
  .row-label { font-weight: 500; white-space: nowrap; display: flex; align-items: center; gap: .5rem; position: sticky; left: 0; background: var(--bg-card); }
  .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
</style>
