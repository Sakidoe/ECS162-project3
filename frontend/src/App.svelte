<script lang="ts">
  import { onMount } from 'svelte';

  interface Article {
    _id: string;
    headline: { main: string };
    snippet: string;
    web_url: string;
    multimedia?: { url: string; subtype: string }[];
  }

  let articles: Article[] = [];
  let isLoading = true;
  let errorMsg = '';
  let userEmail = '';
  let userRole = '';
  let showSidebar = false;

  let commentSidebarOpen = false;
  let activeArticleUrl = '';
  let comments = [];
  let commentInput = '';
  let replyTo: string = '';
  let replyInput: string = '';

  let editingCommentId: string = '';
  let editingContent: string = '';

  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'
  });

  function panelClass(i: number) {
    return ['tl', 'tm', 'tr', 'bl', 'bm', 'br'][i] + '-panel';
  }

  function toggleSidebar() {
    showSidebar = !showSidebar;
  }

  function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }

  function openComments(url: string) {
    activeArticleUrl = url;
    commentSidebarOpen = true;
    loadComments();
  }

  function toggleReply(commentId: string) {
    replyTo = replyTo === commentId ? '' : commentId;
    replyInput = '';
  }

  function getTopLevelParent(id: string): string {
    const parent = comments.find(c => c._id === id);
    if (!parent || !parent.parent_id) return id; // already top-level
    return getTopLevelParent(parent.parent_id);  // recursively find top
  }


  function startEditComment(c) {
    editingCommentId = c._id;
    editingContent = c.content;
  }

  function getReplies(parentId: string) {
    return comments.filter(c => c.parent_id === parentId);
  }

  async function fetchNews() {
    try {
      const res = await fetch('http://localhost:8000/api/news?q=Sacramento+OR+Davis');
      const data = await res.json();
      articles = data.response.docs;
    } catch (e) {
      errorMsg = 'Could not load articles.';
    } finally {
      isLoading = false;
    }
  }

  async function fetchUser() {
    try {
      const res = await fetch('http://localhost:8000/api/user', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        userEmail = data.email;
        userRole = data.role;
      }
    } catch (err) {
      console.error('Not logged in');
    }
  }

  async function loadComments() {
    const res = await fetch(`http://localhost:8000/api/comments?url=${encodeURIComponent(activeArticleUrl)}`);
    comments = await res.json();
  }

  async function submitComment() {
    if (!commentInput.trim()) return;
    await fetch('http://localhost:8000/api/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ article_url: activeArticleUrl, content: commentInput })
    });
    commentInput = '';
    await loadComments();
  }

  async function submitReply(parentId: string, username: string) {
  if (!replyInput.trim()) return;

  const topLevelParentId = getTopLevelParent(parentId);

  await fetch('http://localhost:8000/api/comments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      article_url: activeArticleUrl,
      content: replyInput,
      parent_id: topLevelParentId  
    })
  });

  replyInput = '';
  replyTo = '';
  await loadComments();
}

  async function deleteComment(id: string) {
    await fetch(`http://localhost:8000/api/comments/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    await loadComments();
  }

  async function saveEditComment(id: string) {
    if (!editingContent.trim()) return;
    await fetch(`http://localhost:8000/api/comments/${id}/edit`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ content: editingContent })
    });
    editingCommentId = '';
    editingContent = '';
    await loadComments();
  }

  function logout() {
    window.location.href = 'http://localhost:8000/logout';
  }

  onMount(async () => {
    await fetchUser();
    await fetchNews();
  });
</script>

<!-- Header -->
<header class="header-layout">
  <div class="date-time">{currentDate}</div>
  <h1 class="nyt-title">The New&nbsp;York&nbsp;Times</h1>
  {#if userEmail}
    <button class="account-button" on:click={toggleSidebar}>Account</button>
    {#if showSidebar}
      <div class="sidebar sidebar-open">
        <div class="sidebar-content">
          <h2>{getGreeting()},</h2>
          <p>{userEmail}</p>
          <button class="logout-btn" on:click={logout}>Log out</button>
        </div>
        <button class="overlay" on:click={toggleSidebar}></button>
      </div>
    {/if}
  {:else}
    <a href="http://localhost:8000/login"><button>Log in</button></a>
  {/if}
</header>

<!-- News Grid -->
<main class="fs-body-container">
  {#if isLoading}
    <p class="loading">Loading news…</p>
  {:else if errorMsg}
    <p class="error">{errorMsg}</p>
  {:else}
    {#each [0,1,2,3,4,5] as i}
      <div class={panelClass(i)}>
        {#if articles[i]}
          {#if articles[i].multimedia && articles[i].multimedia.length > 0}
            {#each articles[i].multimedia as media}
              {#if media.subtype === 'xlarge' || media.subtype === 'thumbnail'}
                <img src={"https://www.nytimes.com/" + media.url} alt={articles[i].headline.main} width="100%" />
                {@html ''}
              {/if}
            {/each}
          {/if}
          <h1>{articles[i].headline.main}</h1>
          <p>{articles[i].snippet}</p>
          <a class="read-more" href={articles[i].web_url} target="_blank">Continue reading →</a>
          <button on:click={() => openComments(articles[i].web_url)}>💬 Comments</button>
        {/if}
      </div>
    {/each}
  {/if}
</main>

<!-- Comments Sidebar -->
{#if commentSidebarOpen}
  <div class="sidebar sidebar-open">
    <div class="sidebar-content">
      <h2>Comments ({comments.length})</h2>
      {#if userEmail}
        <textarea bind:value={commentInput} placeholder="Share your thoughts..." rows="3"></textarea>
        <button on:click={submitComment}>Post</button>
      {:else}
        <p>Please log in to comment.</p>
      {/if}
      <hr />
      {#each comments.filter(c => !c.parent_id) as c (c._id)}
        <div class="comment-block">
          <div class="avatar">{c.username[0].toUpperCase()}</div>
          <div>
            <strong>{c.username}</strong> {#if c.role}<small> ({c.role})</small>{/if}
            <p>{c.content}</p>

            {#if userEmail}
              <button on:click={() => toggleReply(c._id)}>Reply</button>
            {/if}
            {#if userRole === 'moderator'}
              <button on:click={() => startEditComment(c)}>Edit</button>
              <button on:click={() => deleteComment(c._id)}>Delete</button>
            {/if}

            {#if replyTo === c._id}
              <div class="reply-box">
                <textarea bind:value={replyInput} rows="2"></textarea>
                <button on:click={() => submitReply(c._id, c.username)}>Post Reply</button>
                <button on:click={() => replyTo = ''}>Cancel</button>
              </div>
            {/if}
            {#if editingCommentId === c._id}
              <div class="edit-box">
                <textarea bind:value={editingContent} rows="3"></textarea>
                <button on:click={() => saveEditComment(c._id)}>Save</button>
                <button on:click={() => editingCommentId = ''}>Cancel</button>
              </div>
            {/if}

            <!-- Replies -->
            {#each getReplies(c._id) as reply (reply._id)}
              <div class="comment-block reply-child">
                <div class="avatar">{reply.username[0].toUpperCase()}</div>
                <div>
                  <strong>{reply.username}</strong> {#if reply.role}<small> ({reply.role})</small>{/if}
                  <p>{reply.content}</p>
                  {#if userEmail}
                    <button on:click={() => toggleReply(reply._id)}>Reply</button>
                  {/if}
                  <!-- {#if true} -->
                  {#if userRole === 'moderator'}
                    <button on:click={() => startEditComment(reply)}>Edit</button>
                    <button on:click={() => deleteComment(reply._id)}>Delete</button>
                  {/if}
                  {#if replyTo === reply._id}
                    <div class="reply-box">
                      <textarea bind:value={replyInput} rows="2"></textarea>
                      <button on:click={() => submitReply(reply._id, reply.username)}>Post Reply</button>
                      <button on:click={() => replyTo = ''}>Cancel</button>
                    </div>
                  {/if}
                  {#if editingCommentId === reply._id}
                    <div class="edit-box">
                      <textarea bind:value={editingContent} rows="3"></textarea>
                      <button on:click={() => saveEditComment(reply._id)}>Save</button>
                      <button on:click={() => editingCommentId = ''}>Cancel</button>
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
    <button class="overlay" on:click={() => commentSidebarOpen = false}></button>
  </div>
{/if}

<style>
  .loading { padding: 2rem; text-align: center; }
  .error { color: black; padding: 1rem; text-align: center; }
  .read-more { color: #326891; text-decoration: none; font-weight: bold; }

  .sidebar {
    position: fixed;
    top: 0;
    right: -100%;
    width: 30vw;
    background: white;
    height: 100vh;
    overflow-y: scroll;
    padding: 1rem;
    box-shadow: -2px 0 6px rgba(0,0,0,0.1);
    transition: right 0.3s ease;
    z-index: 1000;
  }

  .sidebar-open { right: 0; }
  .sidebar-content { padding: 1rem; }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 70vw;
    height: 100vh;
    background: transparent;
    border: none;
    z-index: 999;
  }

  .comment-block {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .avatar {
    background-color: #ccc;
    border-radius: 50%;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }

  .reply-box textarea,
  .edit-box textarea {
    width: 100%;
    margin: 0.5rem 0;
  }

  .reply-box button,
  .edit-box button {
    margin-right: 0.5rem;
  }

  .reply-child {
    margin-left: 2rem;
    padding-left: 1rem;
    border-left: 2px solid #ddd;
  }

  .logout-btn {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: black;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
  }

  .logout-btn:hover {
    background-color: #e74c3c;
  }
</style>
