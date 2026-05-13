<script>
  import '../app.css';
  let { children } = $props();
</script>

<nav>
  <div class="nav-inner">
    <a href="/" class="logo">FinanceDataCrawler</a>
    <div class="nav-links">
      <a href="/">Companies</a>
      <a href="/discover">Discover</a>
      <a href="/extract">Extract</a>
    </div>
  </div>
</nav>

<main>
  {@render children()}
</main>

<style>
  nav {
    border-bottom: 1px solid var(--border);
    background: var(--bg-card);
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .nav-inner {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .logo { font-weight: 700; font-size: 1.1rem; color: var(--text); }
  main {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
  }
</style>
