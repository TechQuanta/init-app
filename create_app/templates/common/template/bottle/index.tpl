<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{project_name}} | py-create</title>
    <link rel="stylesheet" href="/static/style.css">
    
    <script>
        (function() {
            const saved = localStorage.getItem('py-create-theme');
            const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', saved || (dark ? 'dark' : 'light'));
        })();
    </script>
</head>
<body class="bottle">

    <nav class="nav">
        <div class="nav-content">
            <span class="logo">🔥 py-create</span>
            <div class="nav-links">
                <a href="https://bottlepy.org/" target="_blank">Docs</a>
                <a href="https://github.com/techquanta/py-create" target="_blank" class="github-link">GitHub</a>
                
                <button id="theme-toggle" class="theme-toggle" aria-label="Toggle Theme">
                    <div class="toggle-circle">
                        <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="5"></circle><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path></svg>
                        <svg class="moon-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                    </div>
                </button>
            </div>
        </div>
    </nav>

    <main class="page">
        <div class="container">
            
            <header class="hero">
                <h1>{{project_name}}<span class="dot">.</span></h1>
                <p class="subtitle">
                    Minimal • Fast • Single-file Micro Framework. 
                    Your lightweight Python backend is ready.
                </p>
            </header>

            <div class="info-grid">
                <div class="card">
                    <strong>Framework</strong>
                    <span>Bottle.py</span>
                    <p class="card-desc">Distributed as a single file module with no dependencies.</p>
                </div>

                <div class="card">
                    <strong>Project Mode</strong>
                    <span>Development</span>
                    <p class="card-desc">Running on the built-in HTTP development server.</p>
                </div>

                <div class="card">
                    <strong>Routing</strong>
                    <span>Dynamic &rarr;</span>
                    <p class="card-desc">Clean URLs with support for dynamic parameters.</p>
                </div>
            </div>

            <section class="stack-section">
                <h2>Tech Stack</h2>
                <div class="tech-stack">
                    <div class="tech">
                        <img src="https://cdn.worldvectorlogo.com/logos/bottle.svg" alt="Bottle">
                        <span>Bottle</span>
                    </div>
                    <div class="tech">
                        <img src="https://cdn.worldvectorlogo.com/logos/python-5.svg" alt="Python">
                        <span>Python</span>
                    </div>
                </div>
            </section>

        </div>
    </main>

    <footer class="footer">
        <p>✨ Created with <strong>py-create</strong> • Bottle Application</p>
    </footer>

    <script src="/static/script.js"></script>
</body>
</html>