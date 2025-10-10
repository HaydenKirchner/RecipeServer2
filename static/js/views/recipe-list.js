/**
 * Recipe List View
 * Handles the display and filtering of recipe lists.
 */

class RecipeListView {
    /**
     * Initialize the recipe list view
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = Object.assign({
            containerId: 'recipes-container',
            filterFormId: 'filter-form',
            recipeCardOptions: {}
        }, options);
        
        this.container = document.getElementById(this.options.containerId);
        this.filterForm = document.getElementById(this.options.filterFormId);
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the view
     */
    init() {
        if (!this.container) return;
        
        // Initialize filter controls
        FilterUtils.initializeFilters({
            formSelector: `#${this.options.filterFormId}`,
            resultsContainerSelector: `#${this.options.containerId}`,
            updateCallback: this.updateRecipes.bind(this)
        });
        
        // Initial load of recipes from data attribute if available
        const recipesData = this.container.dataset.recipes;
        if (recipesData) {
            try {
                const recipes = JSON.parse(recipesData);
                this.renderRecipes(recipes);
            } catch (error) {
                console.error('Error parsing recipe data:', error);
            }
        } else {
            // Load recipes from API
            this.loadRecipes();
        }
    }
    
    /**
     * Load recipes from API
     * @param {Object} filters - Optional filters to apply
     */
    async loadRecipes(filters = {}) {
        if (!this.container) return;
        
        try {
            // Show loading state
            this.container.innerHTML = `
                <div class="text-center p-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading recipes...</span>
                    </div>
                    <p class="mt-3">Loading recipes...</p>
                </div>
            `;
            
            // If no filters provided, get them from the URL
            if (Object.keys(filters).length === 0) {
                filters = FilterUtils.getFiltersFromUrl();
            }
            
            // Fetch recipes from API
            const recipes = await ApiService.getRecipes(filters);
            
            // Render the recipes
            this.renderRecipes(recipes);
        } catch (error) {
            console.error('Error loading recipes:', error);
            this.container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Error Loading Recipes</h4>
                    <p>${error.message || 'An unknown error occurred while loading recipes.'}</p>
                    <hr>
                    <p class="mb-0">Please try again later or contact support if the problem persists.</p>
                </div>
            `;
        }
    }
    
    /**
     * Update recipes based on filters
     * @param {Object} filters - Filters to apply
     */
    updateRecipes(filters) {
        this.loadRecipes(filters);
    }
    
    /**
     * Render recipes to the container
     * @param {Array} recipes - Array of recipe objects
     */
    renderRecipes(recipes) {
        if (!this.container) return;
        
        // Clear container
        this.container.innerHTML = '';
        
        if (!recipes || recipes.length === 0) {
            this.container.innerHTML = `
                <div class="alert alert-info" role="alert">
                    <h4 class="alert-heading">No Recipes Found</h4>
                    <p>No recipes match your search criteria.</p>
                    <hr>
                    <p class="mb-0">Try adjusting your filters or <a href="/recipes/add" class="alert-link">add a new recipe</a>.</p>
                </div>
            `;
            return;
        }
        
        // Create row for grid layout
        const row = document.createElement('div');
        row.className = 'row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4';
        
        // Add recipe cards to the row
        recipes.forEach(recipe => {
            const col = document.createElement('div');
            col.className = 'col';
            
            const recipeCard = new RecipeCard(recipe, this.options.recipeCardOptions);
            col.appendChild(recipeCard.render());
            
            row.appendChild(col);
        });
        
        this.container.appendChild(row);
    }
}
