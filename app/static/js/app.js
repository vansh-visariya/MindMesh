document.addEventListener('DOMContentLoaded', () => {
    const articlesGrid = document.getElementById('articles-grid');
    const sourceFilter = document.getElementById('source-filter');
    const refreshBtn = document.getElementById('refresh-btn');
    const chatModal = document.getElementById('chat-modal');
    const closeBtn = document.querySelector('.close-btn');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');

    let currentArticleId = null;

    // Fetch articles on load
    fetchArticles();

    // Event Listeners
    sourceFilter.addEventListener('change', () => fetchArticles(sourceFilter.value));
    refreshBtn.addEventListener('click', () => fetchArticles(sourceFilter.value));
    
    closeBtn.addEventListener('click', () => {
        chatModal.classList.add('hidden');
        currentArticleId = null;
        chatHistory.innerHTML = '';
    });

    window.addEventListener('click', (e) => {
        if (e.target === chatModal) {
            chatModal.classList.add('hidden');
            currentArticleId = null;
            chatHistory.innerHTML = '';
        }
    });

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function fetchArticles(source = '') {
        articlesGrid.innerHTML = '<p>Loading articles...</p>';
        try {
            let url = '/api/articles';
            if (source) {
                url += `?source=${encodeURIComponent(source)}`;
            }
            const response = await fetch(url);
            const articles = await response.json();
            renderArticles(articles);
        } catch (error) {
            console.error('Error fetching articles:', error);
            articlesGrid.innerHTML = '<p>Error loading articles. Please try again.</p>';
        }
    }

    function renderArticles(articles) {
        articlesGrid.innerHTML = '';
        if (articles.length === 0) {
            articlesGrid.innerHTML = '<p>No articles found.</p>';
            return;
        }

        articles.forEach(article => {
            const card = document.createElement('div');
            card.className = 'card';
            
            const date = new Date(article.published_at).toLocaleDateString();
            
            card.innerHTML = `
                <div class="card-content">
                    <div class="source-tag">${article.source}</div>
                    <h3><a href="${article.url}" target="_blank">${article.title}</a></h3>
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
    }

    function openChat(articleId) {
        chatModal.classList.remove('hidden');
        // Add initial greeting
        addMessage('ai', "Hello! I've read this article. What would you like to know?");
    }

    async function sendMessage() {
        const question = chatInput.value.trim();
        if (!question || !currentArticleId) return;

        addMessage('user', question);
        chatInput.value = '';
        
        // Show loading indicator
        const loadingId = addMessage('ai', 'Thinking...');

        try {
            const response = await fetch('/api/chat', {
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
        msgDiv.textContent = text;
        
        // Generate a unique ID for loading messages
        const id = 'msg-' + Date.now();
        msgDiv.id = id;
        
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return id;
    }
});
