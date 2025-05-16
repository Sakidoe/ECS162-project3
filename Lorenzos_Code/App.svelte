<script lang="ts">
  import { onMount } from 'svelte';

   // Get current date in NYT format (e.g. "Thursday, April 30, 2025")
   let currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  // Article matches NYT API structure
  interface Article {
    _id: string;
    headline: {
      main: string;
    };
    snippet: string;
    web_url: string;
    multimedia?: {
      caption?: string;
      credit?: string;
      default?: {
        url: string;
      };
      thumbnail?: {
        url: string;
      };
    };
  }

  let articles: Article[] = [];
  let isLoading: boolean = true;

  async function fetchNews(): Promise<void> {
    try {
      const response = await fetch('http://localhost:8000/api/news?q=Sacramento+OR+Davis');
      const data = await response.json();
      articles = data.response.docs as Article[];   
      isLoading = false;
    } catch (err) {
      console.error("Fetch error:", err);
    }
  }
  onMount(fetchNews);

</script>

<header class="nyt-header">
  <div class="header-content">
    <img 
      src="https://upload.wikimedia.org/wikipedia/commons/7/77/The_New_York_Times_logo.png" 
      alt="The New York Times" 
      class="nyt-logo"
    >
    <div class="current-date">
      {currentDate}
    </div>
  </div>
</header>

<main class="article-columns">
  {#if isLoading}
    <p>Loading news...</p>
  {:else}
  <!--Start First Column-->
    <div class="left-column">
      {#each articles.slice(0, 2) as article}

        <article class="news-card">
          {#if article.multimedia?.default?.url}
            <figure>
              <img 
                src={article.multimedia?.default?.url}
                alt={article.headline.main}
                class="article-image"
              >
              <figcaption class="image-caption">
                {article.multimedia.caption || 'Credit: The New York Times'}
              </figcaption>
            </figure>
          {:else}
            <div class="no-image"></div>
          {/if}
          <h2 class="headline">{article.headline.main}</h2>
          <p class="summary">{article.snippet}</p>
          <a href={article.web_url} class="read-more" target="_blank">Continue reading →</a>
        </article>
      {/each}
    </div>
    <!--End First Column-->

    <!--Start Second Column-->
    <div class="middle-column">
      {#each articles.slice(2, 4) as article}

        <article class="news-card">
          {#if article.multimedia?.default?.url}
            <figure>
              <img 
                src={article.multimedia?.default?.url}
                alt={article.headline.main}
                class="article-image"
              >
              <figcaption class="image-caption">
                {article.multimedia.caption || 'Credit: The New York Times'}
              </figcaption>
            </figure>
          {:else}
            <div class="no-image"></div>
          {/if}
          <h2 class="headline">{article.headline.main}</h2>
          <p class="summary">{article.snippet}</p>
          <a href={article.web_url} class="read-more" target="_blank">Continue reading →</a>
        </article>
      {/each}
    </div>
    <!--End Second Column-->

    <!--Start Third Column-->
    <div class="right-column">
      {#each articles.slice(4, 6) as article}

        <article class="news-card">
          {#if article.multimedia?.default?.url}
            <figure>
              <img 
                src={article.multimedia?.default?.url}
                alt={article.headline.main}
                class="article-image"
              >
              <figcaption class="image-caption">
                {article.multimedia.caption || 'Credit: The New York Times'}
              </figcaption>
            </figure>
          {:else}
            <div class="no-image"></div> <!--Empty, but good practice-->
          {/if}
          <h2 class="headline">{article.headline.main}</h2>
          <p class="summary">{article.snippet}</p>
          <a href={article.web_url} class="read-more" target="_blank">Continue reading →</a>
        </article>
      {/each}
    </div>
    <!--End Third Column-->

    <!-- Repeat same structure for middle/right columns with articles.slice(2,4) and slice(4,6) -->
  {/if}
</main>

<style>
  .article-columns {
    display: flex;
    gap: 20px;
    padding: 2px;
  }

  .news-card {
    margin-bottom: 10px;
  }

  .article-image {
    width: 100%;
    height: auto;
    margin-bottom: 12px;
  }

  .image-caption {
    font-size: 0.8rem;
    color: #666;
    margin-top: 4px;
  }

  .headline {
    font-family: Georgia, serif;
    font-size: 1.5rem;
    margin-bottom: 8px;
  }

  .summary {
    font-size: 1rem;
    line-height: 1.5;
    margin-bottom: 12px;
  }

  .read-more {
    color: #326891;
    text-decoration: none;
    font-weight: bold;
  }

  .nyt-header {
    background: white;
    padding: 20px;
    text-align: center;
    border-bottom: none;
    margin-bottom: 10px;
  }
  
  .nyt-logo {
    height: 40px;
    width: auto;
  }

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px;
    border-bottom: 1px solid #e2e2e2;
  }

  .current-date {
    font-family: 'Georgia', serif;
    font-size: 14px;
    color: #333;
  }

  :global(body) {
  background: white;
  margin: 0;
  font-family: 'Georgia', serif;
  color: #333;
}

</style>