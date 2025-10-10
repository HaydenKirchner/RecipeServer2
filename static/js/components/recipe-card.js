/**
 * Recipe Card Component
 * Handles the display and interactions for recipe cards in the UI.
 */

class RecipeCard {
    /**
     * Create a recipe card component
     * @param {Object} recipe - The recipe data
     * @param {Object} options - Optional configuration
     */
    constructor(recipe, options = {}) {
        this.recipe = recipe;
        this.options = Object.assign({
            showActions: true,
            clickable: true,
            showNutrition: true
        }, options);
    }
    
    /**
     * Render the recipe card
     * @return {HTMLElement} The card element
     */
    render() {
        const card = document.createElement('div');
        card.className = 'card recipe-card h-100 shadow-sm';
        
        // Add click handler if clickable
        if (this.options.clickable) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', (e) => {
                // Don't navigate if clicking a button inside the card
                if (!e.target.closest('button')) {
                    window.location.href = `/recipes/${this.recipe.id}`;
                }
            });
        }
        
        // Image
        let imageHtml = '';
        if (this.recipe.image_url) {
            imageHtml = `<img src="${this.recipe.image_url}" class="card-img-top" alt="${this.recipe.title}">`;
        } else {
            // Placeholder image
            imageHtml = `
                <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="bi bi-image text-light" viewBox="0 0 16 16">
                        <path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
                        <path d="M2.002 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2h-12zm12 1a1 1 0 0 1 1 1v6.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12V3a1 1 0 0 1 1-1h12z"/>
                    </svg>
                </div>
            `;
        }
        
        // Recipe info
        let timeInfo = '';
        if (this.recipe.prep_time || this.recipe.cook_time) {
            const totalTime = (this.recipe.prep_time || 0) + (this.recipe.cook_time || 0);
            if (totalTime > 0) {
                timeInfo = `
                    <div class="recipe-info-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clock" viewBox="0 0 16 16">
                            <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                            <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                        </svg>
                        ${formatDuration(totalTime)}
                    </div>
                `;
            }
        }
        
        // Nutrition badges
        let nutritionBadges = '';
        if (this.options.showNutrition && this.recipe.nutrition) {
            nutritionBadges = `
                <div class="mt-2">
                    ${this.recipe.nutrition.calories ? 
                        `<span class="badge bg-primary nutrition-badge">${Math.round(this.recipe.nutrition.calories)} cal</span>` : ''}
                    ${this.recipe.nutrition.protein ? 
                        `<span class="badge bg-success nutrition-badge">${Math.round(this.recipe.nutrition.protein)}g protein</span>` : ''}
                    ${this.recipe.nutrition.carbs ? 
                        `<span class="badge bg-info nutrition-badge">${Math.round(this.recipe.nutrition.carbs)}g carbs</span>` : ''}
                    ${this.recipe.nutrition.fat ? 
                        `<span class="badge bg-warning nutrition-badge">${Math.round(this.recipe.nutrition.fat)}g fat</span>` : ''}
                </div>
            `;
        }
        
        // Action buttons
        let actionButtons = '';
        if (this.options.showActions) {
            actionButtons = `
                <div class="card-footer bg-transparent border-top-0">
                    <div class="d-flex justify-content-between">
                        <a href="/recipes/${this.recipe.id}/edit" class="btn btn-sm btn-outline-secondary" 
                           onclick="event.stopPropagation();">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
                                <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                            </svg>
                            Edit
                        </a>
                        <a href="/recipes/${this.recipe.id}/pdf" class="btn btn-sm btn-outline-primary" 
                           onclick="event.stopPropagation();">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-pdf" viewBox="0 0 16 16">
                                <path d="M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H4zm0 1h8a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1z"/>
                                <path d="M4.603 12.087a.81.81 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.102.198-.307.526-.568.897-.787a7.68 7.68 0 0 1 1.482-.645 19.701 19.701 0 0 0 1.062-2.227 7.269 7.269 0 0 1-.43-1.295c-.086-.4-.119-.796-.046-1.136.075-.354.274-.672.65-.823.192-.077.4-.12.602-.077a.7.7 0 0 1 .477.365c.088.164.12.356.127.538.007.187-.012.395-.047.614-.084.51-.27 1.134-.52 1.794a10.954 10.954 0 0 0 .98 1.686 5.753 5.753 0 0 1 1.334.05c.364.065.734.195.96.465.12.144.193.32.2.518.007.192-.047.382-.138.563a1.04 1.04 0 0 1-.354.416.856.856 0 0 1-.51.138c-.331-.014-.654-.196-.933-.417a5.716 5.716 0 0 1-.911-.95 11.642 11.642 0 0 0-1.997.406 11.311 11.311 0 0 1-1.021 1.51c-.29.35-.608.655-.926.787a.793.793 0 0 1-.58.029zm1.379-1.901c-.166.076-.32.156-.459.238-.328.194-.541.383-.647.547-.094.145-.096.25-.04.361.01.022.02.036.026.044a.27.27 0 0 0 .035-.012c.137-.056.355-.235.635-.572a8.18 8.18 0 0 0 .45-.606zm1.64-1.33a12.647 12.647 0 0 1 1.01-.193 11.666 11.666 0 0 1-.51-.858 20.741 20.741 0 0 1-.5 1.05zm2.446.45c.15.162.296.3.435.41.24.19.407.253.498.256a.107.107 0 0 0 .07-.015.307.307 0 0 0 .094-.125.436.436 0 0 0 .059-.2.095.095 0 0 0-.026-.063c-.052-.062-.2-.152-.518-.209a3.881 3.881 0 0 0-.612-.053zM8.078 5.8a6.7 6.7 0 0 0 .2-.828c.031-.188.043-.343.038-.465a.613.613 0 0 0-.032-.198.517.517 0 0 0-.145.04c-.087.035-.158.106-.196.283-.04.192-.03.469.046.822.024.111.054.227.09.346z"/>
                            </svg>
                            PDF
                        </a>
                    </div>
                </div>
            `;
        }
        
        // Assemble the card
        card.innerHTML = `
            ${imageHtml}
            <div class="card-body">
                <h5 class="card-title">${this.recipe.title}</h5>
                <p class="card-text small text-truncate">${this.recipe.description || ''}</p>
                <div class="d-flex flex-wrap">
                    ${timeInfo}
                    ${this.recipe.servings ? 
                        `<div class="recipe-info-item">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-people" viewBox="0 0 16 16">
                                <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816zM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275zM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/>
                            </svg>
                            ${this.recipe.servings} servings
                        </div>` : 
                        ''}
                </div>
                ${nutritionBadges}
            </div>
            ${actionButtons}
        `;
        
        return card;
    }
    
    /**
     * Render the recipe card as HTML string
     * @return {string} HTML string
     */
    renderToString() {
        const tempContainer = document.createElement('div');
        tempContainer.appendChild(this.render());
        return tempContainer.innerHTML;
    }
}
