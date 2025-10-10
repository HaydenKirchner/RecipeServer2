/**
 * Meal Plan Component
 * Handles the display and interactions for meal plans in the UI.
 */

class MealPlan {
    /**
     * Create a meal plan component
     * @param {Object} mealPlan - The meal plan data
     * @param {Object} options - Optional configuration
     */
    constructor(mealPlan, options = {}) {
        this.mealPlan = mealPlan;
        this.options = Object.assign({
            editable: false,
            recipes: [] // Available recipes for adding
        }, options);
        
        // Define common meal types and days
        this.mealTypes = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];
        this.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    }
    
    /**
     * Initialize the meal plan component with event listeners
     */
    initialize() {
        if (this.options.editable) {
            // Setup add recipe form handlers
            document.querySelectorAll('.add-recipe-form').forEach(form => {
                form.addEventListener('submit', this.handleAddRecipe.bind(this));
            });
            
            // Setup remove recipe buttons
            document.querySelectorAll('.remove-recipe-btn').forEach(button => {
                button.addEventListener('click', this.handleRemoveRecipe.bind(this));
            });
        }
    }
    
    /**
     * Handle adding a recipe to the meal plan
     * @param {Event} event - The form submit event
     */
    handleAddRecipe(event) {
        event.preventDefault();
        const form = event.target;
        const mealPlanId = form.dataset.mealPlanId;
        const day = form.elements.day.value;
        const mealType = form.elements.meal_type.value;
        const recipeId = form.elements.recipe_id.value;
        
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = `<span class="loading-spinner"></span> Adding...`;
        submitButton.disabled = true;
        
        // Submit the form
        fetch(`/meal-plans/${mealPlanId}/add-recipe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(new FormData(form))
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to add recipe to meal plan');
            }
            // Reload the page to show updated meal plan
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            // Show error message
            showToast('Failed to add recipe to meal plan', 'danger');
            // Reset button state
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        });
    }
    
    /**
     * Handle removing a recipe from the meal plan
     * @param {Event} event - The button click event
     */
    handleRemoveRecipe(event) {
        event.preventDefault();
        const button = event.currentTarget;
        const mealPlanId = button.dataset.mealPlanId;
        const recipeId = button.dataset.recipeId;
        const day = button.dataset.day;
        const mealType = button.dataset.mealType;
        
        // Confirm removal
        confirmAction('Are you sure you want to remove this recipe from the meal plan?', () => {
            // Show loading state
            const originalButtonText = button.innerHTML;
            button.innerHTML = `<span class="loading-spinner"></span>`;
            button.disabled = true;
            
            // Create form data
            const formData = new FormData();
            formData.append('recipe_id', recipeId);
            formData.append('day', day);
            formData.append('meal_type', mealType);
            
            // Submit the request
            fetch(`/meal-plans/${mealPlanId}/remove-recipe`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to remove recipe from meal plan');
                }
                // Reload the page to show updated meal plan
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error message
                showToast('Failed to remove recipe from meal plan', 'danger');
                // Reset button state
                button.innerHTML = originalButtonText;
                button.disabled = false;
            });
        });
    }
    
    /**
     * Render the meal plan
     * @return {HTMLElement} The meal plan element
     */
    render() {
        const container = document.createElement('div');
        container.className = 'meal-plan-container';
        
        // Meal plan header
        const header = document.createElement('div');
        header.className = 'meal-plan-header mb-4';
        header.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <h2>${this.mealPlan.name}</h2>
                <div>
                    ${this.options.editable ? 
                        `<a href="/meal-plans/${this.mealPlan.id}/edit" class="btn btn-outline-primary me-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
                                <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                            </svg>
                            Edit
                        </a>` : 
                        ''}
                    <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteMealPlanModal">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                        </svg>
                        Delete
                    </button>
                </div>
            </div>
            <div class="meal-plan-dates mt-2 mb-4">
                <p class="text-muted">
                    ${this.mealPlan.start_date ? 
                        `<span class="me-3">Start: ${formatDate(this.mealPlan.start_date)}</span>` : ''}
                    ${this.mealPlan.end_date ? 
                        `<span>End: ${formatDate(this.mealPlan.end_date)}</span>` : ''}
                </p>
            </div>
        `;
        container.appendChild(header);
        
        // Days container
        const daysContainer = document.createElement('div');
        daysContainer.className = 'meal-plan-days';
        
        // Iterate over each day
        this.days.forEach(day => {
            const dayElement = document.createElement('div');
            dayElement.className = 'meal-plan-day card mb-4';
            
            // Check if this day has any meals
            const dayData = this.mealPlan.days && this.mealPlan.days[day] ? this.mealPlan.days[day] : {};
            
            // Day header
            const dayHeader = document.createElement('div');
            dayHeader.className = 'card-header';
            dayHeader.innerHTML = `<h3 class="h5 mb-0">${day}</h3>`;
            dayElement.appendChild(dayHeader);
            
            // Day content
            const dayContent = document.createElement('div');
            dayContent.className = 'card-body';
            
            // Iterate over meal types
            this.mealTypes.forEach(mealType => {
                const mealElement = document.createElement('div');
                mealElement.className = 'meal-slot mb-3';
                
                // Meal type header
                mealElement.innerHTML = `<h4 class="h6 mb-2">${mealType}</h4>`;
                
                // Recipes for this meal
                const recipes = dayData[mealType] || [];
                
                if (recipes.length > 0) {
                    const recipesContainer = document.createElement('div');
                    recipesContainer.className = 'meal-recipes';
                    
                    recipes.forEach(recipe => {
                        const recipeElement = document.createElement('div');
                        recipeElement.className = 'meal-recipe card mb-2';
                        
                        let recipeActions = '';
                        if (this.options.editable) {
                            recipeActions = `
                                <div class="ms-auto">
                                    <button type="button" class="btn btn-sm btn-outline-danger remove-recipe-btn"
                                            data-meal-plan-id="${this.mealPlan.id}"
                                            data-recipe-id="${recipe.id}"
                                            data-day="${day}"
                                            data-meal-type="${mealType}">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle" viewBox="0 0 16 16">
                                            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                                        </svg>
                                    </button>
                                </div>
                            `;
                        }
                        
                        recipeElement.innerHTML = `
                            <div class="card-body p-2">
                                <div class="d-flex align-items-center">
                                    <a href="/recipes/${recipe.id}" class="text-decoration-none text-body">
                                        <div class="d-flex align-items-center">
                                            ${recipe.image_url ? 
                                                `<img src="${recipe.image_url}" class="me-2" alt="${recipe.title}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">` : 
                                                ''}
                                            <div>
                                                <h5 class="card-title h6 mb-0">${recipe.title}</h5>
                                                ${recipe.nutrition && recipe.nutrition.calories ? 
                                                    `<small class="text-muted">${Math.round(recipe.nutrition.calories)} calories</small>` : 
                                                    ''}
                                            </div>
                                        </div>
                                    </a>
                                    ${recipeActions}
                                </div>
                            </div>
                        `;
                        
                        recipesContainer.appendChild(recipeElement);
                    });
                    
                    mealElement.appendChild(recipesContainer);
                } else if (this.options.editable) {
                    // Empty state with add recipe form for editable meal plans
                    const emptyState = document.createElement('div');
                    emptyState.className = 'empty-meal-slot';
                    emptyState.innerHTML = `
                        <form class="add-recipe-form" data-meal-plan-id="${this.mealPlan.id}">
                            <input type="hidden" name="day" value="${day}">
                            <input type="hidden" name="meal_type" value="${mealType}">
                            <div class="input-group input-group-sm">
                                <select name="recipe_id" class="form-select" required>
                                    <option value="">Select a recipe...</option>
                                    ${this.options.recipes.map(recipe => `
                                        <option value="${recipe.id}">${recipe.title}</option>
                                    `).join('')}
                                </select>
                                <button type="submit" class="btn btn-outline-primary">Add</button>
                            </div>
                        </form>
                    `;
                    mealElement.appendChild(emptyState);
                } else {
                    // Empty state for non-editable meal plans
                    const emptyState = document.createElement('div');
                    emptyState.className = 'empty-meal-slot text-muted small';
                    emptyState.textContent = 'No recipes planned for this meal';
                    mealElement.appendChild(emptyState);
                }
                
                dayContent.appendChild(mealElement);
            });
            
            dayElement.appendChild(dayContent);
            daysContainer.appendChild(dayElement);
        });
        
        container.appendChild(daysContainer);
        
        // Delete confirmation modal
        const deleteModal = document.createElement('div');
        deleteModal.className = 'modal fade';
        deleteModal.id = 'deleteMealPlanModal';
        deleteModal.setAttribute('tabindex', '-1');
        deleteModal.setAttribute('aria-labelledby', 'deleteMealPlanModalLabel');
        deleteModal.setAttribute('aria-hidden', 'true');
        
        deleteModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="deleteMealPlanModalLabel">Confirm Deletion</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to delete the meal plan "${this.mealPlan.name}"?</p>
                        <p class="text-danger">This action cannot be undone.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <form action="/meal-plans/${this.mealPlan.id}/delete" method="post">
                            <button type="submit" class="btn btn-danger">Delete</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(deleteModal);
        
        return container;
    }
}
