import { openModal, closeModal, submitPost } from './utils.js';
import { logout, getUser } from './auth.js';

async function update_auth_ui() {
  const authButtons = document.getElementById('auth-nav-buttons');
  const guestButtons = document.getElementById('guest-nav-buttons');
  const usernameDisplay = document.getElementById('username-display');
  const user = await getUser();

  if (user) {
    // Show auth buttons, hide guest buttons
    authButtons.classList.remove('hidden');
    authButtons.classList.add('flex');
    guestButtons.classList.add('hidden');
    guestButtons.classList.remove('flex');

    // Display username
    if (usernameDisplay) {
      usernameDisplay.textContent = `Welcome, ${user.username}`;
    }
  } else {
    // Hide auth buttons, show guest buttons
    authButtons.classList.add('hidden');
    authButtons.classList.remove('flex');
    guestButtons.classList.remove('hidden');
    guestButtons.classList.add('flex');
  }
}

document.getElementById('theme-toggle').onclick = () => {
  document.documentElement.classList.toggle('dark');
  localStorage.blog_theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
};

document.getElementById('login-btn').onclick = () => { window.location.href = '/login'; };
document.getElementById('register-btn').onclick = () => { window.location.href = '/register'; };

const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
  logoutBtn.onclick = logout;
}

// Update UI on page load

const newPostBtn = document.getElementById('new-post-btn');
if (newPostBtn) {
  newPostBtn.onclick = () => openModal('new-post-modal');
  document.getElementById('new-post-modal-backdrop').onclick = () => closeModal('new-post-modal');
  document.getElementById('new-post-modal-card').onclick = (e) => e.stopPropagation();
  document.getElementById('new-post-modal-cancel').onclick = () => closeModal('new-post-modal');
  document.getElementById('new-post-form').onsubmit = submitPost;
}

update_auth_ui();