/**
 * Filter Utilities
 * Utilities for filtering and sorting recipes.
 */

class FilterUtils {
    /**
     * Initialize filter controls
     * @param {Object} options - Configuration options
     */
    static initializeFilters(options = {}) {
        const defaults = {
            formSelector: '#filter-form',
            resultsContainerSelector: '#recipes-container',
            clearFilterSelector: '#clear-filters',
            sortBySelector: '#sort-by',
            sortDirectionSelector: '#sort-direction',
            searchInputSelector: '#search-input',
            ingredientInputSelector: '#ingredient-input',
            minCaloriesSelector: '#min-calories',
            maxCaloriesSelector: '#max-calories',
            updateCallback: null
        };
        
        const config = { ...defaults, ...options };
        const filterForm = document.querySelector(config.formSelector);
        
        if (!filterForm) return;
        
        // Setup form submission
        filterForm.addEventListener('submit', (event) => {
            event.preventDefault();
            this.applyFilters(config);
        });
        
        // Clear filters button
        const clearFilterBtn = document.querySelector(config.clearFilterSelector);
        if (clearFilterBtn) {
            clearFilterBtn.addEventListener('click', (event) => {
                event.preventDefault();
                this.clearFilters(config);
            });
        }
        
        // Setup instant filtering on sort change
        const sortBySelect = document.querySelector(config.sortBySelector);
        const sortDirectionSelect = document.querySelector(config.sortDirectionSelector);
        
        if (sortBySelect) {
            sortBySelect.addEventListener('change', () => this.applyFilters(config));
        }
        
        if (sortDirectionSelect) {
            sortDirectionSelect.addEventListener('change', () => this.applyFilters(config));
        }
        
        // Setup debounced search
        const searchInput = document.querySelector(config.searchInputSelector);
        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => this.applyFilters(config), 500));
        }
        
        // Load current URL parameters into form
        this.loadFiltersFromUrl(config);
    }
    
    /**
     * Apply filters and update results
     * @param {Object} config - Configuration options
     */
    static applyFilters(config) {
        const filterForm = document.querySelector(config.formSelector);
        const resultsContainer = document.querySelector(config.resultsContainerSelector);
        
        if (!filterForm || !resultsContainer) return;
        
        // Create search params from form data
        const formData = new FormData(filterForm);
        const searchParams = new URLSearchParams();
        
        for (const [key, value] of formData.entries()) {
            if (value) searchParams.append(key, value);
        }
        
        // Update URL with filters
        const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
        window.history.pushState({}, '', newUrl);
        
        // Either use callback or reload page
        if (config.updateCallback && typeof config.updateCallback === 'function') {
            resultsContainer.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            
            // Convert form data to object for the callback
            const filters = {};
            for (const [key, value] of formData.entries()) {
                if (value) filters[key] = value;
            }
            
            config.updateCallback(filters);
        } else {
            // Simple page reload with new filters
            window.location.href = newUrl;
        }
    }
    
    /**
     * Clear all filters
     * @param {Object} config - Configuration options
     */
    static clearFilters(config) {
        const filterForm = document.querySelector(config.formSelector);
        
        if (!filterForm) return;
        
        // Reset form inputs
        const inputs = filterForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = input.defaultChecked;
            } else {
                input.value = input.defaultValue;
            }
        });
        
        // Apply filters (which will now be empty)
        this.applyFilters(config);
    }
    
    /**
     * Load filters from URL parameters
     * @param {Object} config - Configuration options
     */
    static loadFiltersFromUrl(config) {
        const filterForm = document.querySelector(config.formSelector);
        
        if (!filterForm) return;
        
        // Get URL parameters
        const searchParams = new URLSearchParams(window.location.search);
        
        // Update form fields from URL parameters
        searchParams.forEach((value, key) => {
            const input = filterForm.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = (value === 'true' || value === '1');
                } else {
                    input.value = value;
                }
            }
        });
    }
    
    /**
     * Parse filters from URL
     * @return {Object} Parsed filters
     */
    static getFiltersFromUrl() {
        const filters = {};
        const searchParams = new URLSearchParams(window.location.search);
        
        searchParams.forEach((value, key) => {
            filters[key] = value;
        });
        
        return filters;
    }
    
    /**
     * Sort recipes by a specific field
     * @param {Array} recipes - Array of recipes
     * @param {string} field - Field to sort by
     * @param {string} direction - Sort direction ('asc' or 'desc')
     * @return {Array} Sorted recipes
     */
    static sortRecipes(recipes, field, direction = 'asc') {
        if (!field || !recipes || !Array.isArray(recipes)) return recipes;
        
        const sortedRecipes = [...recipes];
        
        sortedRecipes.sort((a, b) => {
            let valueA, valueB;
            
            // Handle nested fields for nutrition
            if (field.startsWith('nutrition.')) {
                const nutritionField = field.split('.')[1];
                valueA = a.nutrition ? a.nutrition[nutritionField] : 0;
                valueB = b.nutrition ? b.nutrition[nutritionField] : 0;
            } else {
                valueA = a[field];
                valueB = b[field];
            }
            
            // Handle nulls and undefined
            if (valueA === null || valueA === undefined) valueA = '';
            if (valueB === null || valueB === undefined) valueB = '';
            
            // Sort based on type
            if (typeof valueA === 'string' && typeof valueB === 'string') {
                return direction === 'asc' ? 
                    valueA.localeCompare(valueB) : 
                    valueB.localeCompare(valueA);
            } else {
                return direction === 'asc' ? valueA - valueB : valueB - valueA;
            }
        });
        
        return sortedRecipes;
    }
    
    /**
     * Filter recipes by search term
     * @param {Array} recipes - Array of recipes
     * @param {string} searchTerm - Search term
     * @return {Array} Filtered recipes
     */
    static filterRecipesBySearch(recipes, searchTerm) {
        if (!searchTerm || !recipes || !Array.isArray(recipes)) return recipes;
        
        const term = searchTerm.toLowerCase().trim();
        
        return recipes.filter(recipe => {
            // Search in title and description
            const title = (recipe.title || '').toLowerCase();
            const description = (recipe.description || '').toLowerCase();
            
            // Search in ingredients
            const ingredientsMatch = recipe.ingredients && recipe.ingredients.some(ingredient => 
                (ingredient.name || '').toLowerCase().includes(term)
            );
            
            return title.includes(term) || description.includes(term) || ingredientsMatch;
        });
    }
    
    /**
     * Filter recipes by ingredient
     * @param {Array} recipes - Array of recipes
     * @param {string} ingredient - Ingredient name
     * @return {Array} Filtered recipes
     */
    static filterRecipesByIngredient(recipes, ingredient) {
        if (!ingredient || !recipes || !Array.isArray(recipes)) return recipes;
        
        const term = ingredient.toLowerCase().trim();
        
        return recipes.filter(recipe => {
            return recipe.ingredients && recipe.ingredients.some(ing => 
                (ing.name || '').toLowerCase().includes(term)
            );
        });
    }
    
    /**
     * Filter recipes by calorie range
     * @param {Array} recipes - Array of recipes
     * @param {number} minCalories - Minimum calories
     * @param {number} maxCalories - Maximum calories
     * @return {Array} Filtered recipes
     */
    static filterRecipesByCalories(recipes, minCalories, maxCalories) {
        if (!recipes || !Array.isArray(recipes)) return recipes;
        
        return recipes.filter(recipe => {
            if (!recipe.nutrition || recipe.nutrition.calories === null || recipe.nutrition.calories === undefined) {
                return false;
            }
            
            const calories = recipe.nutrition.calories;
            
            if (minCalories !== null && minCalories !== undefined && calories < minCalories) {
                return false;
            }
            
            if (maxCalories !== null && maxCalories !== undefined && calories > maxCalories) {
                return false;
            }
            
            return true;
        });
    }
}
