const themeToggle = document.getElementById('theme-toggle');
const root = document.documentElement;

function applyTheme(theme) {
  if (theme === 'light') {
    root.setAttribute('data-theme', 'light');
    themeToggle.textContent = '☀️';
  } else {
    root.removeAttribute('data-theme');
    themeToggle.textContent = '🌙';
  }
}

let savedTheme = 'dark';
try {
  savedTheme = localStorage.getItem('portfolio-theme') || 'dark';
} catch (e) {
}
applyTheme(savedTheme);

themeToggle.addEventListener('click', () => {
  const isLight = root.getAttribute('data-theme') === 'light';
  const next = isLight ? 'dark' : 'light';
  applyTheme(next);
  try { localStorage.setItem('portfolio-theme', next); } catch (e) {}
});

const homeView = document.getElementById('home-view');
const stackView = document.getElementById('stack-view');
const viewStackBtn = document.getElementById('view-stack');
const backHomeBtn = document.getElementById('back-home');

viewStackBtn.addEventListener('click', () => {
  homeView.classList.add('hidden');
  stackView.classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

backHomeBtn.addEventListener('click', () => {
  stackView.classList.add('hidden');
  homeView.classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

const chatToggle = document.getElementById('chat-toggle');
const chatBox = document.getElementById('chat-box');
const chatClose = document.getElementById('chat-close');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatBody = document.getElementById('chat-body');

chatToggle.addEventListener('click', () => chatBox.classList.toggle('hidden'));
chatClose.addEventListener('click', () => chatBox.classList.add('hidden'));

const responses = [
  { keys: ['project', 'projects'], reply: "I've built an ordering system for a school canteen, a facial-recognition account-recovery feature, and a student document request system — check the Projects section above!" },
  { keys: ['tech', 'stack', 'tools', 'skill'], reply: "On the frontend I use HTML, CSS, and JavaScript, and I work with C++ on the backend. Click 'View Full Stack' to see it all." },
  { keys: ['contact', 'email', 'reach'], reply: "You can reach me at sofhiaalexa22@gmail.com — I'd love to hear from you!" },
  { keys: ['hire', 'internship', 'work', 'available'], reply: "I'm currently open to internships, student projects, and freelance opportunities. Feel free to reach out by email!" }
];

function getReply(message) {
  const lower = message.toLowerCase();
  const match = responses.find(r => r.keys.some(k => lower.includes(k)));
  return match ? match.reply : "Thanks for your message! I'll get back to you soon — or email me directly at sofhiaalexa22@gmail.com.";
}

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage(text, 'user');
  chatInput.value = '';

  setTimeout(() => addMessage(getReply(text), 'bot'), 400);
});

function addMessage(text, sender) {
  const div = document.createElement('div');
  div.className = `chat-msg ${sender}`;
  div.textContent = text;
  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
}