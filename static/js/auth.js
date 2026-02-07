const TOKEN_KEY = "access_token";
let user = null;
let userPromise = null;

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  user = null;
  window.location.href = "/";
}

export function clearUserCache() {
  user = null;
}

export async function getUser() {
  if (user) return user;
  if (userPromise) return userPromise;

  const token = getToken();
  if (!token) return null;

  userPromise = fetch("/api/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((res) => (res.ok ? res.json() : null))
    .then((data) => {
      user = data;
      userPromise = null;
      return user;
    })
    .catch(() => {
      userPromise = null;
      return null;
    });

  return userPromise;
}
