/**
 * Meal Planner View
 * Handles the display and interaction with meal plans.
 */

class MealPlannerView {
    /**
     * Initialize the meal planner view
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = Object.assign({
            containerId: 'meal-plan-container',
            mealPlanId: null,
            editable: false
        }, options);
        
        this.container = document.getElementById(this.options.containerId);
        this.mealPlanId = this.options.mealPlanId || 
                          (this.container ? this.container.dataset.mealPlanId : null);
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the view
     */
    async init() {
        if (!this.container) return;
        
        // If we're creating a new meal plan
        if (this.container.dataset.mode === 'add') {
            this.initAddMealPlanForm();
            return;
        }
        
        // If we're viewing a specific meal plan
        if (this.mealPlanId) {
            await this.loadMealPlan(this.mealPlanId);
            return;
        }
        
        // Otherwise, load all meal plans
        await this.loadMealPlans();
    }
    
    /**
     * Initialize the form for adding a new meal plan
     */
    initAddMealPlanForm() {
        const form = document.getElementById('add-meal-plan-form');
        if (!form) return;
        
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // Disable submit button to prevent double submission
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = `<span class="loading-spinner"></span> Creating...`;
            
            try {
                // Get form data
                const formData = new FormData(form);
                const mealPlanData = {
                    name: formData.get('name'),
                    start_date: formData.get('start_date'),
                    end_date: formData.get('end_date')
                };
                
                // Send API request
                const response = await ApiService.createMealPlan(mealPlanData);
                
                // Redirect to the new meal plan
                window.location.href = `/meal-plans/${response.id}`;
            } catch (error) {
                console.error('Error creating meal plan:', error);
                
                // Show error message
                const errorAlert = document.createElement('div');
                errorAlert.className = 'alert alert-danger alert-dismissible fade show mt-3';
                errorAlert.innerHTML = `
                    <strong>Error!</strong> Failed to create meal plan: ${error.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                form.prepend(errorAlert);
                
                // Reset button
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        });
    }
    
    /**
     * Load a specific meal plan
     * @param {number} mealPlanId - The meal plan ID
     */
    async loadMealPlan(mealPlanId) {
        try {
            // Show loading state
            this.container.innerHTML = `
                <div class="text-center p-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading meal plan...</span>
                    </div>
                    <p class="mt-3">Loading meal plan...</p>
                </div>
            `;
            
            // Load meal plan and recipes if editable
            const [mealPlan, recipes] = await Promise.all([
                ApiService.getMealPlan(mealPlanId),
                this.options.editable ? ApiService.getRecipes() : Promise.resolve([])
            ]);
            
            // Render the meal plan
            const mealPlanComponent = new MealPlan(mealPlan, {
                editable: this.options.editable,
                recipes: recipes
            });
            
            // Clear container and add the meal plan component
            this.container.innerHTML = '';
            this.container.appendChild(mealPlanComponent.render());
            
            // Initialize event handlers
            mealPlanComponent.initialize();
        } catch (error) {
            console.error('Error loading meal plan:', error);
            this.container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Error Loading Meal Plan</h4>
                    <p>${error.message || 'An unknown error occurred.'}</p>
                    <hr>
                    <p class="mb-0">Please try again later or contact support if the problem persists.</p>
                </div>
            `;
        }
    }
    
    /**
     * Load all meal plans
     */
    async loadMealPlans() {
        try {
            // Show loading state
            this.container.innerHTML = `
                <div class="text-center p-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading meal plans...</span>
                    </div>
                    <p class="mt-3">Loading meal plans...</p>
                </div>
            `;
            
            // Fetch meal plans from API
            const mealPlans = await ApiService.getMealPlans();
            
            // Render the meal plans list
            this.renderMealPlansList(mealPlans);
        } catch (error) {
            console.error('Error loading meal plans:', error);
            this.container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Error Loading Meal Plans</h4>
                    <p>${error.message || 'An unknown error occurred.'}</p>
                    <hr>
                    <p class="mb-0">Please try again later or contact support if the problem persists.</p>
                </div>
            `;
        }
    }
    
    /**
     * Render a list of meal plans
     * @param {Array} mealPlans - Array of meal plan objects
     */
    renderMealPlansList(mealPlans) {
        // Clear container
        this.container.innerHTML = '';
        
        if (!mealPlans || mealPlans.length === 0) {
            this.container.innerHTML = `
                <div class="alert alert-info" role="alert">
                    <h4 class="alert-heading">No Meal Plans Found</h4>
                    <p>You haven't created any meal plans yet.</p>
                    <hr>
                    <p class="mb-0"><a href="/meal-plans/add" class="btn btn-primary">Create a Meal Plan</a></p>
                </div>
            `;
            return;
        }
        
        // Create a card for each meal plan
        const row = document.createElement('div');
        row.className = 'row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4';
        
        mealPlans.forEach(mealPlan => {
            const col = document.createElement('div');
            col.className = 'col';
            
            // Count recipes in the meal plan
            let recipeCount = 0;
            if (mealPlan.days) {
                Object.values(mealPlan.days).forEach(day => {
                    Object.values(day).forEach(mealType => {
                        recipeCount += mealType.length;
                    });
                });
            }
            
            // Format date range
            let dateRange = '';
            if (mealPlan.start_date && mealPlan.end_date) {
                dateRange = `${formatDate(mealPlan.start_date)} to ${formatDate(mealPlan.end_date)}`;
            } else if (mealPlan.start_date) {
                dateRange = `From ${formatDate(mealPlan.start_date)}`;
            } else if (mealPlan.end_date) {
                dateRange = `Until ${formatDate(mealPlan.end_date)}`;
            }
            
            // Create the card
            const card = document.createElement('div');
            card.className = 'card h-100 shadow-sm';
            card.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${mealPlan.name}</h5>
                    ${dateRange ? `<p class="card-text"><small class="text-muted">${dateRange}</small></p>` : ''}
                    <p class="card-text">
                        ${recipeCount} recipe${recipeCount !== 1 ? 's' : ''} planned
                    </p>
                </div>
                <div class="card-footer bg-transparent border-top-0">
                    <a href="/meal-plans/${mealPlan.id}" class="btn btn-primary">View Plan</a>
                    <a href="/meal-plans/${mealPlan.id}/edit" class="btn btn-outline-secondary">Edit</a>
                </div>
            `;
            
            col.appendChild(card);
            row.appendChild(col);
        });
        
        // Add a "Create New" card
        const createCol = document.createElement('div');
        createCol.className = 'col';
        
        const createCard = document.createElement('div');
        createCard.className = 'card h-100 border-dashed shadow-sm';
        createCard.innerHTML = `
            <div class="card-body d-flex flex-column align-items-center justify-content-center text-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-plus-circle text-primary mb-3" viewBox="0 0 16 16">
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                    <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                </svg>
                <h5 class="card-title">Create New Meal Plan</h5>
                <p class="card-text">Plan your meals for the week or a special occasion</p>
                <a href="/meal-plans/add" class="btn btn-primary mt-3">Create Plan</a>
            </div>
        `;
        
        createCol.appendChild(createCard);
        row.appendChild(createCol);
        
        this.container.appendChild(row);
    }
}
