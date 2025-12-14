document.addEventListener('DOMContentLoaded', () => {
    const resultsArea = document.getElementById('resultsArea');
    const moodGrid = document.getElementById('moodGrid');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalBody = document.getElementById('modalBody');
    const closeModal = document.getElementById('closeModal');

    // Only run if we are on the dashboard
    if (moodGrid) {
        initDashboard();
    }

    if (closeModal) {
        closeModal.addEventListener('click', () => {
            modalOverlay.classList.remove('active');
            setTimeout(() => modalOverlay.classList.add('hidden'), 300);
        });
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal.click();
        });
    }

    const surpriseBtn = document.getElementById('surpriseBtn');
    if (surpriseBtn) {
        surpriseBtn.addEventListener('click', async () => {
            // Add loading animation to button
            surpriseBtn.textContent = '🎲 Picking...';
            try {
                const response = await fetch('/api/surprise');
                if (response.ok) {
                    const food = await response.json();
                    openDetailModal(food);
                } else {
                    console.error('Surprise failed');
                }
            } catch (error) {
                console.error('Error:', error);
            } finally {
                surpriseBtn.textContent = '🎲 Surprise Me!';
            }
        });
    }

    async function initDashboard() {
        // Fetch Moods
        try {
            const response = await fetch('/api/moods');
            const moods = await response.json();
            renderMoods(moods);
        } catch (error) {
            console.error('Failed to load moods', error);
        }
    }

    function renderMoods(moods) {
        moodGrid.innerHTML = '';
        moods.forEach(mood => {
            const chip = document.createElement('div');
            chip.className = 'mood-chip';
            chip.textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
            chip.addEventListener('click', () => {
                // Remove active from others
                document.querySelectorAll('.mood-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                searchByMood(mood);
            });
            moodGrid.appendChild(chip);
        });
    }

    window.toggleFavorite = async function (foodId, btn) {
        // Optimistic UI update
        const isActive = btn.classList.toggle('active');

        try {
            const response = await fetch(`/api/favorite/${foodId}`, { method: 'POST' });
            if (!response.ok) {
                // Revert if failed
                btn.classList.toggle('active');
                console.error('Failed to toggle favorite');
            }
        } catch (error) {
            btn.classList.toggle('active');
            console.error('Error:', error);
        }
    };

    async function searchByMood(mood) {
        setLoading(true);
        try {
            const response = await fetch(`/api/search?mood=${encodeURIComponent(mood)}`);
            const data = await response.json();
            renderResults(data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    }

    function renderResults(foods) {
        resultsArea.innerHTML = '';
        if (!foods || foods.length === 0) {
            resultsArea.innerHTML = '<p style="text-align:center;width:100%;color:var(--text-dim)">No matches found.</p>';
            return;
        }

        foods.forEach((food, index) => {
            const card = document.createElement('div');
            card.className = `eatery-card animate-enter stagger-${(index % 3) + 1}`;

            // Create tags HTML
            const tagHtml = food.keywords.slice(0, 3).map(k => `<span class="tag">#${k}</span>`).join('');

            card.style.position = 'relative'; // Ensure button positioning works

            // Dynamic Image URL
            const imageUrl = `https://image.pollinations.ai/prompt/delicious ${food.name} food photography?width=400&height=300&nologo=true`;

            // Check if favorited (this needs to be passed in food object or checked separately)
            // For now, we will handle the visual state via separate call or assume passed
            const isFav = food.is_favorite ? 'active' : '';

            card.innerHTML = `
                <img src="${imageUrl}" class="card-image" alt="${food.name}" loading="lazy">
                <button class="fav-btn ${isFav}" onclick="event.stopPropagation(); toggleFavorite(${food.id}, this)">
                    ♥
                </button>
                <div class="card-content">
                    <span class="eatery-name">${food.name}</span>
                    <div class="tags">${tagHtml}</div>
                </div>
            `;

            card.addEventListener('click', () => openDetailModal(food));
            resultsArea.appendChild(card);
        });
    }

    function openDetailModal(food) {
        modalBody.innerHTML = `
            <h2 style="font-size: 2rem; margin-bottom: 1rem; color: var(--text-light);">${food.name}</h2>
            <p style="color:var(--text-dim); margin-bottom: 2rem;">Perfect for this mood because it is:</p>
            <div class="tags" style="justify-content:center; margin-bottom:2rem;">
                ${food.keywords.map(k => `<span class="tag" style="background:var(--accent); color:white;">#${k}</span>`).join('')}
            </div>
            <button class="cta-btn" style="width:100%; border-radius:12px;" onclick="window.location.href='/order/${food.id}'">Order Now</button>
        `;
        modalOverlay.classList.remove('hidden');
        requestAnimationFrame(() => modalOverlay.classList.add('active'));
    }

    function setLoading(isLoading) {
        if (isLoading) {
            resultsArea.innerHTML = '<div style="text-align:center;width:100%;padding:2rem;"><span style="font-size:2rem;animation:spin 1s infinite linear;display:inline-block;">⏳</span></div>';
        }
    }
});
