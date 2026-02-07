import { getUser, getToken } from './auth.js';

export function openModal(modalId) {
  document.getElementById(modalId).classList.remove('hidden');
}

export function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.add('hidden');
  const form = modal.querySelector('form');
  if (form) form.reset();
  const error = modal.querySelector('[data-error]');
  if (error) error.classList.add('hidden');
}

export function getErrorMessage(detail) {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(e => e.msg).join(', ');
  return 'Failed to create post.';
}

export async function submitPost(e) {
  e.preventDefault();
  const title = document.getElementById('post-title').value.trim();
  const content = document.getElementById('post-content').value.trim();
  const errorEl = document.getElementById('post-error');

  if (!title || !content) {
    errorEl.textContent = 'All fields are required.';
    errorEl.classList.remove('hidden');
    return;
  }

  const user = await getUser();
  if (!user) {
    window.location.href = '/login';
    return;
  }

  try {
    const res = await fetch('/api/posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ title, content })
    });
    if (!res.ok) {
      if (res.status === 401) {
        window.location.href = '/login';
        return;
      }
      const data = await res.json();
      errorEl.textContent = getErrorMessage(data.detail);
      errorEl.classList.remove('hidden');
      return;
    }
    closeModal('new-post-modal');
    window.location.reload();
  } catch {
    errorEl.textContent = 'Network error. Please try again.';
    errorEl.classList.remove('hidden');
  }
}
