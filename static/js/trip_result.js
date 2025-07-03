// trip_result.js
// Simple script for displaying trip plans without complex charts

let tripData = null;
let debugMode = false;

// Log function for debugging
function log(message) {
    console.log(message);
    const debugLog = document.getElementById('debug-log');
    if (debugLog) {
        const timestamp = new Date().toISOString().substring(11, 19);
        debugLog.innerHTML += `[${timestamp}] ${message}\n`;
        debugLog.scrollTop = debugLog.scrollHeight;
    }
}

// Function to safely get nested properties
function getNestedProperty(obj, path, defaultValue = null) {
    try {
        const result = path.split('.')
            .reduce((o, key) => (o && o[key] !== undefined && o[key] !== null) ? o[key] : null, obj);
        return result !== null ? result : defaultValue;
    } catch (e) {
        log(`Error accessing property ${path}: ${e.message}`);
        return defaultValue;
    }
}

// Main function to display the trip data
function displayTripPlan(data) {
    log('Displaying trip plan data');
    
    if (!data) {
        log('Error: No trip data provided');
        alert('No trip plan data available.');
        return;
    }
    
    // Store data globally
    tripData = data;
    
    // Determine if we have a nested plan property
    const planData = data.plan || data;
    
    try {
        // Set title and metadata
        const destination = getNestedProperty(planData, 'city_selection.selected_city', 'Your Trip Plan');
        document.getElementById('trip-title').textContent = destination;
        document.getElementById('trip-destination').textContent = destination;
        
        const daysCount = getNestedProperty(planData, 'itinerary.daily_schedules', []).length || 0;
        document.getElementById('trip-duration').textContent = `${daysCount} day${daysCount !== 1 ? 's' : ''}`;
        
        document.getElementById('trip-people').textContent = `${getNestedProperty(data, 'inputs.people', '2')} travelers`;
        document.getElementById('trip-season').textContent = getNestedProperty(data, 'inputs.season', 'Any Season');
        
        // Set summary
        const summaryElem = document.getElementById('trip-summary');
        if (summaryElem) {
            summaryElem.textContent = getNestedProperty(planData, 'overview', 
                'Your personalized travel plan includes all the information you need for a perfect trip.');
        }
        
        // Populate overview information using new structure
        populateOverview(planData);
        
        // Populate highlights
        populateHighlights(getNestedProperty(planData, 'highlights', []));
        
        // Populate itinerary
        populateItinerary(planData);
        
        // Populate budget
        populateBudget(data);
        
        // Show debug information
        log('Trip plan displayed successfully');
        if (debugMode) {
            log('Plan data: ' + JSON.stringify(data, null, 2));
        }
    } catch (error) {
        log(`Error displaying trip plan: ${error.message}`);
        console.error(error);
    }
}

// Function to populate lists
function populateList(listId, items) {
    const listElement = document.getElementById(listId);
    if (!listElement) {
        log(`Error: List element with ID "${listId}" not found`);
        return;
    }
    
    try {
        // Clear existing content
        listElement.innerHTML = '';
        
        if (!items || items.length === 0) {
            const listItem = document.createElement('li');
            listItem.className = 'info-item';
            listItem.textContent = 'Information not available';
            listElement.appendChild(listItem);
            return;
        }
        
        // Add each item
        items.forEach(item => {
            if (item) {
                const listItem = document.createElement('li');
                listItem.className = 'info-item';
                listItem.textContent = item;
                listElement.appendChild(listItem);
            }
        });
    } catch (error) {
        log(`Error populating list ${listId}: ${error.message}`);
        console.error(error);
    }
}

// Function to populate highlights tags
function populateHighlights(highlights) {
    try {
        const container = document.getElementById('highlights-container');
        if (!container) {
            log('Error: Highlights container not found');
            return;
        }
        
        // Clear existing highlights
        container.innerHTML = '';
        
        if (!highlights || highlights.length === 0) {
            // Add default highlight
            const tag = document.createElement('div');
            tag.className = 'highlight-tag';
            tag.textContent = 'Explore local attractions';
            container.appendChild(tag);
            return;
        }
        
        // Add each highlight as a tag
        highlights.forEach(highlight => {
            if (highlight) {
                const tag = document.createElement('div');
                tag.className = 'highlight-tag';
                tag.textContent = highlight;
                container.appendChild(tag);
            }
        });
        
        log(`Populated ${highlights.length} highlights`);
    } catch (error) {
        log(`Error populating highlights: ${error.message}`);
        console.error(error);
    }
}

// Function to populate overview section using budget tab design
function populateOverview(planData) {
    try {
        const breakdownContainer = document.getElementById('overview-breakdown');
        if (!breakdownContainer) {
            log('Error: Overview breakdown container not found');
            return;
        }
        
        // Clear existing content
        breakdownContainer.innerHTML = '';
        
        // Define overview categories
        const overviewCategories = [
            { 
                key: 'attractions', 
                icon: 'fas fa-map-marker-alt', 
                label: 'Top Attractions',
                items: getNestedProperty(planData, 'city_research.attractions', [])
            },
            { 
                key: 'cuisine', 
                icon: 'fas fa-utensils', 
                label: 'Local Cuisine',
                items: getNestedProperty(planData, 'city_research.cuisine', [])
            },
            { 
                key: 'cultural', 
                icon: 'fas fa-hands', 
                label: 'Cultural Tips',
                items: getNestedProperty(planData, 'city_research.cultural_norms', [])
            },
            { 
                key: 'accommodation', 
                icon: 'fas fa-bed', 
                label: 'Accommodation Areas',
                items: getNestedProperty(planData, 'city_research.accommodation_areas', [])
            },
            { 
                key: 'transportation', 
                icon: 'fas fa-bus', 
                label: 'Transportation Tips',
                items: getNestedProperty(planData, 'city_research.transportation_tips', [])
            }
        ];
        
        // Create overview category cards
        overviewCategories.forEach(category => {
            const items = category.items || [];
            
            // Skip categories with no items
            if (items.length === 0) {
                items.push('Information not available');
            }
            
            // Create the overview category card
            const categoryCard = document.createElement('div');
            categoryCard.className = `overview-category ${category.key}`;
            
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'overview-category-header';
            
            const headerLeft = document.createElement('div');
            headerLeft.innerHTML = `<i class="${category.icon}"></i> ${category.label}`;
            
            categoryHeader.appendChild(headerLeft);
            
            const categoryContent = document.createElement('div');
            categoryContent.className = 'overview-category-content';
            
            // Create list of items
            const list = document.createElement('ul');
            list.className = 'overview-list';
            
            items.forEach(item => {
                if (item) {
                    const listItem = document.createElement('li');
                    listItem.textContent = item;
                    list.appendChild(listItem);
                }
            });
            
            categoryContent.appendChild(list);
            
            categoryCard.appendChild(categoryHeader);
            categoryCard.appendChild(categoryContent);
            
            breakdownContainer.appendChild(categoryCard);
        });
        
        log('Overview information populated successfully');
    } catch (error) {
        log(`Error populating overview: ${error.message}`);
        console.error(error);
    }
}

// Function to populate itinerary using budget tab design
function populateItinerary(planData) {
    try {
        const breakdownContainer = document.getElementById('itinerary-breakdown');
        const noItineraryMessage = document.getElementById('no-itinerary-message');
        const totalDaysElement = document.getElementById('total-days');
        
        if (!breakdownContainer) {
            log('Error: Itinerary breakdown container not found');
            return;
        }
        
        // Clear existing content
        breakdownContainer.innerHTML = '';
        
        const dailySchedules = getNestedProperty(planData, 'itinerary.daily_schedules', []);
        
        if (dailySchedules.length === 0) {
            if (noItineraryMessage) {
                noItineraryMessage.style.display = 'block';
                breakdownContainer.appendChild(noItineraryMessage);
            }
            if (totalDaysElement) totalDaysElement.textContent = '0 Days';
            log('No itinerary data available');
            return;
        }
        
        if (noItineraryMessage) noItineraryMessage.style.display = 'none';
        if (totalDaysElement) totalDaysElement.textContent = `${dailySchedules.length} Days`;
        
        // Process each day using the budget tab design structure
        dailySchedules.forEach(day => {
            const activities = day.activities || [];
            
            // Create the day category card
            const dayCard = document.createElement('div');
            dayCard.className = `day-category day-${day.day}`;
            
            const dayHeader = document.createElement('div');
            dayHeader.className = 'day-category-header';
            
            const headerLeft = document.createElement('div');
            headerLeft.innerHTML = `<i class="fas fa-calendar-day"></i> Day ${day.day}`;
            
            const dayPill = document.createElement('div');
            dayPill.className = 'day-pill';
            dayPill.textContent = `${activities.length} Activities`;
            
            dayHeader.appendChild(headerLeft);
            dayHeader.appendChild(dayPill);
            
            const dayContent = document.createElement('div');
            dayContent.className = 'day-category-content';
            
            if (activities.length === 0) {
                dayContent.textContent = 'No activities planned for this day.';
            } else {
                // Create activity list
                const activityList = document.createElement('ul');
                activityList.className = 'activity-list';
                
                activities.forEach(activity => {
                    const activityItem = document.createElement('li');
                    activityItem.className = 'activity-item';
                    
                    const activityTime = document.createElement('div');
                    activityTime.className = 'activity-time';
                    activityTime.textContent = activity.time || 'Flexible';
                    
                    const activityDetails = document.createElement('div');
                    activityDetails.className = 'activity-details';
                    
                    const activityName = document.createElement('div');
                    activityName.className = 'activity-name';
                    activityName.textContent = activity.activity || 'Untitled Activity';
                    activityDetails.appendChild(activityName);
                    
                    if (activity.location) {
                        const activityLocation = document.createElement('div');
                        activityLocation.className = 'activity-location';
                        activityLocation.textContent = activity.location;
                        activityDetails.appendChild(activityLocation);
                    }
                    
                    // Add transportation information if available
                    const transport = activity.transport || activity.transportation || null;
                    if (transport && transport !== 'N/A') {
                        const activityTransport = document.createElement('div');
                        activityTransport.className = 'activity-transport';
                        activityTransport.innerHTML = `🚶 ${transport}`;
                        activityDetails.appendChild(activityTransport);
                    }
                    
                    activityItem.appendChild(activityTime);
                    activityItem.appendChild(activityDetails);
                    
                    activityList.appendChild(activityItem);
                });
                
                dayContent.appendChild(activityList);
            }
            
            dayCard.appendChild(dayHeader);
            dayCard.appendChild(dayContent);
            
            breakdownContainer.appendChild(dayCard);
        });
        
        log(`Populated itinerary with ${dailySchedules.length} days`);
    } catch (error) {
        log(`Error populating itinerary: ${error.message}`);
        console.error(error);
    }
}

// Function to populate budget without chart elements that were causing errors
function populateBudget(data) {
    try {
        const planData = data.plan || data;
        const budget = getNestedProperty(planData, 'budget', {});
        
        const noBudgetMessage = document.getElementById('no-budget-message');
        const budgetBreakdown = document.getElementById('budget-breakdown');
        
        if (!budgetBreakdown) {
            log('Error: Budget breakdown container not found');
            return;
        }
        
        if (Object.keys(budget).length === 0) {
            if (noBudgetMessage) noBudgetMessage.style.display = 'block';
            log('No budget data available');
            return;
        }
        
        if (noBudgetMessage) noBudgetMessage.style.display = 'none';
        
        // Set currency and total - prioritize user's currency selection
        const currency = getNestedProperty(data, 'inputs.budget_currency', 
                        getNestedProperty(budget, 'currency', 'USD'));
        
        document.getElementById('budget-currency').textContent = currency.toUpperCase();
        
        const totalCost = getNestedProperty(budget, 'total_cost', '0');
        document.getElementById('budget-amount').textContent = totalCost;
        
        // Set budget level
        const budgetLevel = getNestedProperty(data, 'inputs.budget', 'Medium');
        document.getElementById('budget-level').textContent = 
            budgetLevel.charAt(0).toUpperCase() + budgetLevel.slice(1);
        
        // Clear existing budget breakdown (except the no-budget-message)
        budgetBreakdown.innerHTML = '';
        if (noBudgetMessage) {
            budgetBreakdown.appendChild(noBudgetMessage);
            noBudgetMessage.style.display = 'none';
        }
        
        // Define expense categories
        const expenseCategories = [
            { key: 'accommodation', icon: 'fas fa-hotel', label: 'Accommodation' },
            { key: 'transportation', icon: 'fas fa-shuttle-van', label: 'Transportation' },
            { key: 'activities', icon: 'fas fa-hiking', label: 'Activities' },
            { key: 'meals', icon: 'fas fa-utensils', label: 'Meals' },
            { key: 'emergency_fund', icon: 'fas fa-first-aid', label: 'Emergency Fund' }
        ];
        
        // Get travel cost if it exists
        let travelCost = null;
        let travelDetails = '';
        if (planData.travel_cost && planData.travel_cost.travel) {
            travelCost = planData.travel_cost.travel.cost;
            console.log("travelCost",travelCost);
            travelDetails = planData.travel_cost.travel.details || '';
        }
        
        // Check if travel is already included in the budget
        const hasTravelInBudget = budget.travel && budget.travel.cost;
        
        if (travelCost && !hasTravelInBudget) {
            expenseCategories.push(
                { key: 'travel', icon: 'fas fa-plane', label: 'Travel', cost: travelCost, details: travelDetails }
            );
        }
        
        // Create budget category cards
        expenseCategories.forEach(category => {
            const categoryData = budget[category.key] || {};
            const cost = category.cost || 
                       (typeof categoryData === 'object' ? categoryData.cost : categoryData) || 0;
            
            // If this category has no cost, skip it
            if (!cost || parseFloat(cost) === 0) return;
            
            // Create the budget category card
            const categoryCard = document.createElement('div');
            categoryCard.className = `budget-category ${category.key}`;
            
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'budget-category-header';
            
            const headerLeft = document.createElement('div');
            headerLeft.innerHTML = `<i class="${category.icon}"></i> ${category.label}`;
            
            const costPill = document.createElement('div');
            costPill.className = 'cost-pill';
            costPill.textContent = `${currency.toUpperCase()} ${cost}`;
            
            categoryHeader.appendChild(headerLeft);
            categoryHeader.appendChild(costPill);
            
            const categoryContent = document.createElement('div');
            categoryContent.className = 'budget-category-content';
            
            const details = category.details || 
                          (typeof categoryData === 'object' ? categoryData.details : '') || '';
            
            categoryContent.textContent = details || 
                                        `Budget allocation for ${category.label.toLowerCase()}.`;
            
            categoryCard.appendChild(categoryHeader);
            categoryCard.appendChild(categoryContent);
            
            budgetBreakdown.appendChild(categoryCard);
        });
        
        // Add note for travel costs if not included in total
        if (travelCost && !hasTravelInBudget) {
            const noteElement = document.createElement('p');
            noteElement.className = 'budget-note';
            noteElement.innerHTML = `<strong>Note:</strong> Travel costs of ${currency.toUpperCase()} ${travelCost} are listed separately and not included in the total budget.`;
            budgetBreakdown.appendChild(noteElement);
        }
        
        log('Budget details populated successfully');
    } catch (error) {
        log(`Error populating budget: ${error.message}`);
        console.error(error);
    }
}

// Initialize event listeners
function initEventListeners() {
    // Toggle debug log visibility
    const debugBtn = document.getElementById('toggle-debug-btn');
    if (debugBtn) {
        debugBtn.addEventListener('click', function() {
            const debugLog = document.getElementById('debug-log');
            debugMode = !debugMode;
            debugLog.style.display = debugMode ? 'block' : 'none';
            log('Debug mode ' + (debugMode ? 'enabled' : 'disabled'));
        });
    }
    
    // Go back to dashboard
    const backBtn = document.getElementById('go-back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            log('Navigating back to dashboard');
            window.location.href = '/dashboard';
        });
    }
    
    // Tab switching functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    if (tabBtns) {
        tabBtns.forEach(button => {
            button.addEventListener('click', function() {
                const tab = this.getAttribute('data-tab');
                log(`Switching to ${tab} tab`);
                
                // Update active button
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                this.classList.add('active');
                
                // Show the correct tab content
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(`${tab}-tab`).classList.add('active');
            });
        });
    }
    
    // Handle PDF download - Fix the element ID to match HTML
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            log('Initiating PDF download');
            const planIdInput = document.getElementById('plan-id-input');
            const tripNameInput = document.getElementById('trip-name-input');
            const tripDescInput = document.getElementById('trip-description-input');
            const planIdValue = document.getElementById('plan-id-value');
            
            if (planIdInput && tripData) {
                // Get the plan ID from the hidden input
                planIdInput.value = planIdValue ? planIdValue.value : '';
                log(`Using plan ID: ${planIdInput.value}`);
                
                const destination = getNestedProperty(tripData, 'plan.city_selection.selected_city', 'Your Trip');
                const duration = getNestedProperty(tripData, 'plan.itinerary.daily_schedules', []).length || '0';
                
                tripNameInput.value = `${destination} - ${duration} Day Trip`;
                tripDescInput.value = getNestedProperty(tripData, 'plan.overview', 'Your custom travel plan');
                
                document.getElementById('pdf-form').submit();
                log('PDF download form submitted');
            } else {
                log('Error: Missing plan ID or trip data for PDF download');
                alert('Unable to download PDF. Missing plan information.');
            }
        });
    }
    
    // Handle "Create New Plan" button
    const newPlanBtn = document.getElementById('newPlanButton');
    if (newPlanBtn) {
        newPlanBtn.addEventListener('click', function() {
            log('Navigating to create new plan');
            window.location.href = '/dashboard';
        });
    }
}

// Initialize page on load
document.addEventListener('DOMContentLoaded', function() {
    log('Page loaded, initializing trip display');
    
    // Set up event listeners
    initEventListeners();
    
    // Check if we have inline trip data
    const tripDataElement = document.getElementById('trip-data-json');
    if (tripDataElement) {
        try {
            const data = JSON.parse(tripDataElement.textContent);
            displayTripPlan(data);
        } catch (error) {
            log(`Error parsing trip data: ${error.message}`);
            console.error(error);
        }
    } else {
        log('No inline trip data element found');
    }
}); 