<script lang="ts">
  import { onMount } from 'svelte';

  // date banner
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  // typing article
  interface Article {
    _id: string;
    headline: { 
      main: string 
    };
    snippet: string;
    web_url: string;
    multimedia?: {
      caption?: string;
      default?: {
        url: string;
      };
    };
  }

  let articles: Article[] = [];
  let isLoading = true;
  let errorMsg = '';

  // fetching data from nyt api
  async function fetchNews() {
    try {
      const res = await fetch('http://localhost:8000/api/news?q=Sacramento+OR+Davis');
      const data = await res.json();
      articles = data.response.docs as Article[];
    } catch (e) {
      errorMsg = 'Could not load articles.';
      console.error(e);
    } finally {
      isLoading = false;
    }
  }
  onMount(fetchNews);

  // Indexes each panel to be a number between 1 and 6. This way, the program is able to sort through without an aggregious amount of html
  function panelClass(i: number) {
    return ['tl','tm','tr','bl','bm','br'][i] + '-panel';
  }
</script>

<!-- Header of Website -->
<header class="header-layout">
  <div class="date-time">{currentDate}</div>
  <h1 class="nyt-title">The New&nbsp;York&nbsp;Times</h1>
  <p class="stocks">STONKS!</p>
</header>


<main class="fs-body-container">
  <!-- screen if loading info -->
  {#if isLoading}
    <p class="loading">Loading news…</p>
  <!-- error screen -->
  {:else if errorMsg}
    <p class="error">{errorMsg}</p>
  {:else}
  <!-- successful screen formatting, numbering each grid as a news block with i-->
    {#each [0,1,2,3,4,5] as i}
      <div class={panelClass(i)}>
        {#if articles[i]}
          {#if articles[i].multimedia?.default?.url}
            <img src={articles[i].multimedia.default.url}
                alt={articles[i].headline.main} />
          {/if}

          <h1>{articles[i].headline.main}</h1>
          <p>{articles[i].snippet}</p>

          <a class="read-more" href={articles[i].web_url} target="_blank">
            Continue reading →
          </a>

          {#if articles[i].multimedia?.caption}
            <p class="img-cap">{articles[i].multimedia.caption}</p>
          {/if}
        {/if}
      </div>
    {/each}
  {/if}
</main>

<style>
  .loading{padding:2rem;text-align:center}
  .error{color:red;padding:1rem;text-align:center}
  .img-cap{font-size:.8rem;color:#666;margin-top:.25rem}
  .read-more{color:#326891;text-decoration:none;font-weight:bold}
</style>
