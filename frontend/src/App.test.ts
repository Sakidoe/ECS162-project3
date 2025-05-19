import { test, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/svelte';
import App from './App.svelte';

// Utility function to mock fetch sequence for App.svelte
function mockAppFetch({
  user = { email: 'test@example.com', role: 'user' },
  news = [],
  counts = {},
  failNews = false
} = {}) {
  global.fetch = vi.fn();

  // 1. /api/user
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => user
  });

  // 2. /api/news (or simulate failure)
  if (failNews) {
    global.fetch.mockRejectedValueOnce(new Error('API failed'));
  } else {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ response: { docs: news } })
    });
  }

  // 3. /api/comments/counts
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => counts
  });
}

beforeEach(() => {
  vi.restoreAllMocks(); 
});

test('renders the current date', () => {
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });


  const { getByText } = render(App);
  expect(getByText(today)).toBeTruthy();
});

test('renders Account button if logged in', async () => {
  mockAppFetch(); 

  const { findByText } = render(App);
  expect(await findByText('Account')).toBeTruthy();
});

test('fetches and displays news articles', async () => {
  mockAppFetch({
    news: [
      {
        _id: '1',
        headline: { main: 'Breaking Headline' },
        snippet: 'Some snippet',
        web_url: 'https://example.com',
        multimedia: []
      }
    ]
  });

  const { findByText } = render(App);
  expect(await findByText('Breaking Headline')).toBeTruthy();
});

test('shows error message if news fetch fails', async () => {
  mockAppFetch({ failNews: true });

  const { findByText } = render(App);
  expect(await findByText('Could not load articles.')).toBeTruthy();
});
