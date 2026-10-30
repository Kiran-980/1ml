// Optional convenience: all content and navigation work without JavaScript.
document.querySelectorAll('pre').forEach((pre) => {
  const code = pre.querySelector('code');
  if (!code || !navigator.clipboard) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy';
  button.textContent = 'Copy';
  button.setAttribute('aria-label', 'Copy installation commands');
  button.addEventListener('click', async () => {
    const status = document.getElementById('copy-status');
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = 'Copied';
      status.textContent = 'Commands copied to clipboard.';
    } catch {
      button.textContent = 'Select to copy';
      status.textContent = 'Clipboard access is unavailable. Select and copy the commands manually.';
    }
    window.setTimeout(() => { button.textContent = 'Copy'; }, 2500);
  });
  pre.appendChild(button);
});
