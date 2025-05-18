<script lang="ts">
  import { onMount } from 'svelte';
  let userEmail = ''; //store email of user for login purposes
  let showSidebar = false;

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

  onMount(async () => {
  try {
    const res = await fetch('http://localhost:8000/api/user', {
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      console.log('Logged in as:', data.email);
      userEmail = data.email;
    }
  } catch (err) {
    console.error('Not logged in');
  }

  fetchNews();
});


  // Indexes each panel to be a number between 1 and 6. This way, the program is able to sort through without an aggregious amount of html
  function panelClass(i: number) {
    return ['tl','tm','tr','bl','bm','br'][i] + '-panel';
  }

  //toggleSidebar function later used in account button
  function toggleSidebar(){
    showSidebar = !showSidebar;
  }

// greeting that updates in sidebar based on time of day
  function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}
</script>

<!-- Header of Website -->
<header class="header-layout">
  <div class="date-time">{currentDate}</div>
  <h1 class="nyt-title">The New&nbsp;York&nbsp;Times</h1>
  <p class="stocks">STONKS!</p>
  
<!--Log in button, leads to Dex login page-->
<!--Once logged in, Account button replaces log in button and leads to a sidebar menu with greeting message, user email, and logout button-->
{#if userEmail}
  <button class="account-button" on:click={toggleSidebar}>Account</button>

  <div class={`sidebar ${showSidebar ? 'sidebar-open' : ''}`}>
    <div class="sidebar-content">
      <h2>{getGreeting()},</h2>
      <p>{userEmail}</p>
      <a class="logout-btn" href="http://localhost:8000/logout">Log out</a>
    </div>
  </div>

  {#if showSidebar}
    <button
      class="overlay"
      on:click={toggleSidebar}
      aria-label="Close sidebar"
    ></button>
  {/if}
{:else}
  <a href="http://localhost:8000/login">
    <button>Log in</button>
  </a>
{/if}

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



  .account-menu {
    position: relative;
    display: inline-block;
  }

  .dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #ccc;
    border-radius: 0.25rem;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 100;
    min-width: 150px;
  }

  .dropdown p,
  .dropdown a {
    padding: 0.5rem 1rem;
    margin: 0;
    text-decoration: none;
    display: block;
    color: #333;
  }

  .dropdown a:hover {
    background-color: #f0f0f0;
  }
</style>
