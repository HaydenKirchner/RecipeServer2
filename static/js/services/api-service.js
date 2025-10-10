/**
 * API Service
 * Handles API communication with the backend.
 */

class ApiService {
    /**
     * Fetch recipes from the API
     * @param {Object} filters - Optional filters to apply
     * @return {Promise} Promise that resolves to the recipes
     */
    static async getRecipes(filters = {}) {
        try {
            // Build the query string from filters
            const queryParams = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    queryParams.append(key, value);
                }
            });
            
            const response = await fetch(`/api/recipes?${queryParams.toString()}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch recipes: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching recipes:', error);
            throw error;
        }
    }
    
    /**
     * Fetch a single recipe by ID
     * @param {number} recipeId - The recipe ID
     * @return {Promise} Promise that resolves to the recipe
     */
    static async getRecipe(recipeId) {
        try {
            const response = await fetch(`/api/recipes/${recipeId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch recipe: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error fetching recipe ${recipeId}:`, error);
            throw error;
        }
    }
    
    /**
     * Create a new recipe
     * @param {Object} recipeData - The recipe data
     * @return {Promise} Promise that resolves to the created recipe
     */
    static async createRecipe(recipeData) {
        try {
            const response = await fetch('/api/recipes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(recipeData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create recipe: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating recipe:', error);
            throw error;
        }
    }
    
    /**
     * Update an existing recipe
     * @param {number} recipeId - The recipe ID
     * @param {Object} recipeData - The updated recipe data
     * @return {Promise} Promise that resolves to the updated recipe
     */
    static async updateRecipe(recipeId, recipeData) {
        try {
            const response = await fetch(`/api/recipes/${recipeId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(recipeData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to update recipe: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error updating recipe ${recipeId}:`, error);
            throw error;
        }
    }
    
    /**
     * Delete a recipe
     * @param {number} recipeId - The recipe ID
     * @return {Promise} Promise that resolves to the deletion result
     */
    static async deleteRecipe(recipeId) {
        try {
            const response = await fetch(`/api/recipes/${recipeId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to delete recipe: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error deleting recipe ${recipeId}:`, error);
            throw error;
        }
    }
    
    /**
     * Generate a PDF for a recipe
     * @param {number} recipeId - The recipe ID
     * @return {Promise} Promise that resolves to the PDF path
     */
    static async generateRecipePdf(recipeId) {
        try {
            const response = await fetch(`/api/recipes/${recipeId}/pdf`);
            
            if (!response.ok) {
                throw new Error(`Failed to generate PDF: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error generating PDF for recipe ${recipeId}:`, error);
            throw error;
        }
    }
    
    /**
     * Scrape a recipe from a URL
     * @param {string} url - The recipe URL
     * @return {Promise} Promise that resolves to the scraped recipe data
     */
    static async scrapeRecipe(url) {
        try {
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to scrape recipe: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error scraping recipe:', error);
            throw error;
        }
    }
    
    /**
     * Fetch meal plans
     * @return {Promise} Promise that resolves to the meal plans
     */
    static async getMealPlans() {
        try {
            const response = await fetch('/api/meal-plans');
            
            if (!response.ok) {
                throw new Error(`Failed to fetch meal plans: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching meal plans:', error);
            throw error;
        }
    }
    
    /**
     * Fetch a single meal plan by ID
     * @param {number} mealPlanId - The meal plan ID
     * @return {Promise} Promise that resolves to the meal plan
     */
    static async getMealPlan(mealPlanId) {
        try {
            const response = await fetch(`/api/meal-plans/${mealPlanId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch meal plan: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error fetching meal plan ${mealPlanId}:`, error);
            throw error;
        }
    }
    
    /**
     * Create a new meal plan
     * @param {Object} mealPlanData - The meal plan data
     * @return {Promise} Promise that resolves to the created meal plan
     */
    static async createMealPlan(mealPlanData) {
        try {
            const response = await fetch('/api/meal-plans', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(mealPlanData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create meal plan: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating meal plan:', error);
            throw error;
        }
    }
    
    /**
     * Update an existing meal plan
     * @param {number} mealPlanId - The meal plan ID
     * @param {Object} mealPlanData - The updated meal plan data
     * @return {Promise} Promise that resolves to the updated meal plan
     */
    static async updateMealPlan(mealPlanId, mealPlanData) {
        try {
            const response = await fetch(`/api/meal-plans/${mealPlanId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(mealPlanData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to update meal plan: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error updating meal plan ${mealPlanId}:`, error);
            throw error;
        }
    }
    
    /**
     * Delete a meal plan
     * @param {number} mealPlanId - The meal plan ID
     * @return {Promise} Promise that resolves to the deletion result
     */
    static async deleteMealPlan(mealPlanId) {
        try {
            const response = await fetch(`/api/meal-plans/${mealPlanId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to delete meal plan: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error deleting meal plan ${mealPlanId}:`, error);
            throw error;
        }
    }
    
    /**
     * Add a recipe to a meal plan
     * @param {number} mealPlanId - The meal plan ID
     * @param {Object} recipeData - The recipe data including recipe_id, day, and meal_type
     * @return {Promise} Promise that resolves to the updated meal plan
     */
    static async addRecipeToMealPlan(mealPlanId, recipeData) {
        try {
            const response = await fetch(`/api/meal-plans/${mealPlanId}/recipes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(recipeData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to add recipe to meal plan: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error adding recipe to meal plan ${mealPlanId}:`, error);
            throw error;
        }
    }
    
    /**
     * Remove a recipe from a meal plan
     * @param {number} mealPlanId - The meal plan ID
     * @param {number} recipeId - The recipe ID
     * @param {string} day - Optional day
     * @param {string} mealType - Optional meal type
     * @return {Promise} Promise that resolves to the updated meal plan
     */
    static async removeRecipeFromMealPlan(mealPlanId, recipeId, day = null, mealType = null) {
        try {
            const url = `/api/meal-plans/${mealPlanId}/recipes/${recipeId}`;
            const body = {};
            
            if (day) body.day = day;
            if (mealType) body.meal_type = mealType;
            
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: Object.keys(body).length ? JSON.stringify(body) : undefined
            });
            
            if (!response.ok) {
                throw new Error(`Failed to remove recipe from meal plan: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error removing recipe from meal plan ${mealPlanId}:`, error);
            throw error;
        }
    }
    
    /**
     * Calculate nutrition information for ingredients
     * @param {Array} ingredients - List of ingredients
     * @return {Promise} Promise that resolves to the nutrition information
     */
    static async calculateNutrition(ingredients) {
        try {
            const response = await fetch('/api/nutrition/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ingredients })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to calculate nutrition: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error calculating nutrition:', error);
            throw error;
        }
    }
}
