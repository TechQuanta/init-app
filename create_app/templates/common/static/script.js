console.log("🚀 py-create UI loaded");

document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("loaded");
});
/**
 * py-create Interaction System
 */

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            // Apply theme
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('py-create-theme', newTheme);
            
            // Subtle Haptic Feedback / Console log
            console.log(`%c Theme: ${newTheme.toUpperCase()} `, `background: #222; color: #bada55`);
        });
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('py-create-theme', next);
        });
    }
});