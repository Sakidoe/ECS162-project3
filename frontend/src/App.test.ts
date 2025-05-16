// App.test.ts
import { test, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import App from './App.svelte';

// API key test
test('API key is returned from backend', async () => {
  const res = await fetch('http://localhost:8000/api/key');
  const data = await res.json();
  expect(res.ok).toBe(true);
  expect(data).toHaveProperty('apiKey');
});

// NYT article structure test
test('NYT API proxy returns correct structure', async () => {
  const res = await fetch('http://localhost:8000/api/news');
  const data = await res.json();
  expect(data.response.docs[0]).toHaveProperty('headline');
});

// Date test
test('Displays today\'s date', () => {
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  const { getByText } = render(App);
  expect(getByText(today)).toBeTruthy();
});
