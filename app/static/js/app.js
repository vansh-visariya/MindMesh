document.addEventListener('DOMContentLoaded', () => {
    const articlesGrid = document.getElementById('articles-grid');
    const sourceFilter = document.getElementById('source-filter');
    const refreshBtn = document.getElementById('refresh-btn');
    const articleModal = document.getElementById('article-modal');
    const articleCloseBtn = document.querySelector('.article-close-btn');
    const articleViewTitle = document.getElementById('article-view-title');
    const articleViewSource = document.getElementById('article-view-source');
    const articleViewDate = document.getElementById('article-view-date');
    const articleViewContent = document.getElementById('article-view-content');
    const articleOriginalLink = document.getElementById('article-original-link');
    const articleDiscussBtn = document.getElementById('article-discuss-btn');

    let currentArticleId = null;
    let allArticles = []; // Store fetched articles to access content easily

    // Fetch articles on load
    fetchArticles();

    // Event Listeners
    sourceFilter.addEventListener('change', () => fetchArticles(sourceFilter.value));
    refreshBtn.addEventListener('click', () => fetchArticles(sourceFilter.value));

    summarizeBtn.addEventListener('click', () => {
        chatInput.value = "Can you summarize this article?";
        sendMessage();
    });

    closeBtn.addEventListener('click', () => {
        chatModal.classList.add('hidden');
        // Don't clear currentArticleId here if we want to keep context, 
        // but usually closing chat means we are done. 
        // However, if we opened chat from article view, we might want to go back?
        // For now, let's keep it simple.
        chatHistory.innerHTML = '';
    });

    articleCloseBtn.addEventListener('click', () => {
        articleModal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        if (e.target === chatModal) {
            chatModal.classList.add('hidden');
            chatHistory.innerHTML = '';
        }
        if (e.target === articleModal) {
            articleModal.classList.add('hidden');
        }
    });

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    articleDiscussBtn.addEventListener('click', () => {
        // Open chat modal from article view
        // articleModal.classList.add('hidden'); // Optional: close article view or keep it open behind?
        // Let's keep article view open behind or close it? 
        // User might want to read while chatting. 
        // But modals on top of modals is bad UI usually.
        // Let's close article view for now to focus on chat.
        articleModal.classList.add('hidden');
        openChat(currentArticleId);
    });

    async function fetchArticles(source = '') {
        articlesGrid.innerHTML = '<div class="loading-spinner">Loading articles...</div>';
        try {
            let url = '/api/articles/';
            if (source) {
                url += `?source=${encodeURIComponent(source)}`;
            }
            const response = await fetch(url);
            const articles = await response.json();
            allArticles = articles; // Store for local access
            renderArticles(articles);
        } catch (error) {
            console.error('Error fetching articles:', error);
            articlesGrid.innerHTML = '<div class="loading-spinner">Error loading articles. Please try again.</div>';
        }
    }

    function renderArticles(articles) {
        articlesGrid.innerHTML = '';
        if (articles.length === 0) {
            articlesGrid.innerHTML = '<div class="loading-spinner">No articles found.</div>';
            return;
        }

        articles.forEach(article => {
            const card = document.createElement('div');
            card.className = 'card';

            const date = new Date(article.published_at).toLocaleDateString();

            card.innerHTML = `
                <div class="card-content">
                    <div class="source-tag">${article.source}</div>
                    <h3><a href="#" class="article-link" data-id="${article.id}">${article.title}</a></h3>
                    <div class="meta">Published: ${date}</div>
                </div>
                <div class="card-actions">
                    <button class="chat-btn" data-id="${article.id}">Discuss with AI</button>
                </div>
            `;

            articlesGrid.appendChild(card);
        });

        // Add event listeners to new chat buttons
        document.querySelectorAll('.chat-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                currentArticleId = e.target.dataset.id;
                openChat(currentArticleId);
            });
        });

        // Add event listeners to article links
        document.querySelectorAll('.article-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const id = e.target.dataset.id;
                const article = allArticles.find(a => a.id == id);
                if (article) {
                    openArticleView(article);
                }
            });
        });
    }

    function openArticleView(article) {
        currentArticleId = article.id;
        articleViewTitle.textContent = article.title;
        articleViewSource.textContent = article.source;
        articleViewDate.textContent = new Date(article.published_at).toLocaleDateString();
        articleViewContent.textContent = article.content || "Content not available.";
        articleOriginalLink.href = article.url;

        articleModal.classList.remove('hidden');
    }

    function openChat(articleId) {
        chatModal.classList.remove('hidden');
        // Add initial greeting if empty
        if (chatHistory.children.length === 0) {
            addMessage('ai', "Hello! I've read this article. What would you like to know?");
        }
    }

    async function sendMessage() {
        const question = chatInput.value.trim();
        if (!question || !currentArticleId) return;

        addMessage('user', question);
        chatInput.value = '';

        // Show loading indicator
        const loadingId = addMessage('ai', 'Thinking...');

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    article_id: currentArticleId,
                    question: question
                })
            });

            const data = await response.json();

            // Remove loading message and add actual response
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) loadingMsg.remove();

            addMessage('ai', data.answer);

        } catch (error) {
            console.error('Error sending message:', error);
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) loadingMsg.remove();
            addMessage('ai', "Sorry, I couldn't process your request.");
        }
    }

    function addMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;

        // Handle typing indicator
        if (text === 'Thinking...') {
            msgDiv.innerHTML = '<span class="typing-indicator">Thinking...</span>';
        } else {
            msgDiv.textContent = text;
        }

        // Generate a unique ID for loading messages
        const id = 'msg-' + Date.now();
        msgDiv.id = id;

        chatHistory.appendChild(msgDiv);

        // Smooth scroll to bottom
        setTimeout(() => {
            chatHistory.scrollTo({
                top: chatHistory.scrollHeight,
                behavior: 'smooth'
            });
        }, 50);

        return id;
    }
});
