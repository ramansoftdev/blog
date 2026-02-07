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
  const userId = document.getElementById('post-user-id').value;
  const errorEl = document.getElementById('post-error');
  if (!title || !content || !userId) {
    errorEl.textContent = 'All fields are required.';
    errorEl.classList.remove('hidden');
    return;
  }
  try {
    const res = await fetch('/api/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content, user_id: Number(userId) })
    });
    if (!res.ok) {
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
