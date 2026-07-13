import test from 'node:test';
import assert from 'node:assert/strict';
import { filterAndSort } from './app.js';

const articles = [
  { category: 'it', score: 70 }, { category: 'it', score: 95 }, { category: 'top', score: 80 },
];

test('カテゴリを正しく絞り込める', () => {
  const it = filterAndSort(articles, 'it', 'newest');
  assert.equal(it.length, 2);
  assert.ok(it.every(article => article.category === 'it'));
});

test('おすすめ順ではスコアの高い記事が先頭になる', () => {
  const result = filterAndSort(articles, 'all', 'recommended');
  assert.equal(result[0].score, 95);
  assert.ok(result.every((article, index) => index === 0 || result[index - 1].score >= article.score));
});
