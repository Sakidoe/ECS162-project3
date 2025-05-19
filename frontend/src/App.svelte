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
  let commentCounts: Record<string, number> = {};
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

  async function fetchCommentCounts() {
    const res = await fetch('http://localhost:8000/api/comments/counts');
    commentCounts = await res.json(); // find number of comments made
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
    await fetchCommentCounts(); // refresh comment count
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
  await fetchCommentCounts(); // refresh comment count
}

  async function deleteComment(id: string) {
    await fetch(`http://localhost:8000/api/comments/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    await loadComments();
    await fetchCommentCounts(); // refresh comment count
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
    await fetchCommentCounts(); // refresh comment count 
  }

  function logout() {
    window.location.href = 'http://localhost:8000/logout';
  }

  onMount(async () => {
    await fetchUser();
    await fetchNews();
    await fetchCommentCounts(); // Load counts
  });
</script>

<!-- Header -->
<header class="header-layout">
  <div class="date-time">{currentDate}</div>
  <h1 class="nyt-title">The New&nbsp;York&nbsp;Times</h1>
  {#if userEmail}
    <button class="account-button" on:click={toggleSidebar}>
      <span class="account-label">Account</span>
      <span class="account-caret">⌄</span>
    </button>
    {#if showSidebar}
    <div class="sidebar sidebar-open">
      <div class="sidebar-header">
        <strong>{userEmail}</strong>
      </div>
      <hr />
      <div class="sidebar-content">
        <h2 class="greeting">{getGreeting()}.</h2>
        <button class="logout-btn" on:click={logout}>Log out</button>
      </div>
      <button class="overlay" on:click={toggleSidebar}></button>
    </div>
    {/if}
  {:else}
    <a href="http://localhost:8000/login" class="login-button">
      <span class="login-text">Log In</span>
      <span class="login-caret">⌄</span>
    </a>
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
      <div class={panelClass(i)} style="position: relative;">
        {#if articles[i]}
          <!-- Updated Image Handling -->
          {#if articles[i].multimedia}
            {#if articles[i].multimedia.default}
              <img 
                src={articles[i].multimedia.default.url} 
                alt={articles[i].multimedia.caption || articles[i].headline.main} 
                width="100%"
                class="article-image"
                on:error={(e) => e.target.style.display = 'none'}
              />
            {:else if articles[i].multimedia.thumbnail}
              <img 
                src={articles[i].multimedia.thumbnail.url} 
                alt={articles[i].multimedia.caption || articles[i].headline.main} 
                width="100%"
                class="article-image"
              />
            {:else}
              <div class="image-placeholder">📰</div>
            {/if}
          {:else}
            <div class="image-placeholder">📰</div>
          {/if}
          
          <h1>{articles[i].headline.main}</h1>
          <p>{articles[i].snippet}</p>
          <a class="read-more" href={articles[i].web_url} target="_blank">Continue reading →</a>
          
          <!-- Comment button -->
          <div class="comment-button-wrapper">
            <button class="comment-button" on:click={() => openComments(articles[i].web_url)}>
              💬 {commentCounts[articles[i].web_url] || 0}
            </button>
          </div>
        {/if}
      </div>
    {/each}
  {/if}
</main>

<!-- Comments Sidebar -->
{#if commentSidebarOpen}
  <div class="sidebar sidebar-open">
    <div class="sidebar-content">
      <h2>
        {#if articles.find(a => a.web_url === activeArticleUrl)}
          {articles.find(a => a.web_url === activeArticleUrl).headline.main}
        {/if}
      </h2>
      <p>{comments.length} Comment{comments.length === 1 ? '' : 's'}</p>
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

  .comment-button-wrapper {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  }

.comment-button {
  background-color: white;
  color: #444;
  border: 1px solid #aaa;
  border-radius: 999px;
  padding: 0.4rem 0.7rem;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: background 0.2s;
  }

.comment-button:hover {
  background-color: #f0f0f0;
  } 

</style>