// Trip Display Functions
// Contains improved functions for showing trip details

let currentTripData = null;

// Function to load plans from the generated_plans.json file
async function loadSavedPlans() {
    try {
        // Show loading indicator
        document.getElementById('loading-overlay').style.display = 'block';
        
        // Fetch the saved plans
        const response = await fetch('/load_saved_plans');
        const data = await response.json();
        
        if (data.success) {
            displayPlanSelector(data.plans);
        } else {
            alert('Error loading saved plans: ' + data.error);
            document.getElementById('loading-overlay').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading saved plans:', error);
        alert('Failed to load saved plans. Please check the console for details.');
        document.getElementById('loading-overlay').style.display = 'none';
    }
}

// Function to display the plan selector modal
function displayPlanSelector(plans) {
    // Hide loading indicator
    document.getElementById('loading-overlay').style.display = 'none';
    
    // Create modal if it doesn't exist
    let planSelectorModal = document.getElementById('planSelectorModal');
    if (!planSelectorModal) {
        planSelectorModal = document.createElement('div');
        planSelectorModal.id = 'planSelectorModal';
        planSelectorModal.className = 'modal';
        
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        
        const modalHeader = document.createElement('div');
        modalHeader.className = 'modal-header';
        modalHeader.innerHTML = '<h2 class="modal-title">Select a Saved Plan</h2><span class="modal-close">&times;</span>';
        
        const modalBody = document.createElement('div');
        modalBody.className = 'modal-body';
        modalBody.id = 'planSelectorModalBody';
        
        modalContent.appendChild(modalHeader);
        modalContent.appendChild(modalBody);
        planSelectorModal.appendChild(modalContent);
        document.body.appendChild(planSelectorModal);
        
        // Add event listener to close button
        const closeButton = modalHeader.querySelector('.modal-close');
        closeButton.addEventListener('click', function() {
            planSelectorModal.style.display = 'none';
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target === planSelectorModal) {
                planSelectorModal.style.display = 'none';
            }
        });
    }
    
    // Populate the modal with plan options
    const modalBody = document.getElementById('planSelectorModalBody');
    modalBody.innerHTML = '';
    
    if (Object.keys(plans).length === 0) {
        modalBody.innerHTML = '<p>No saved plans found.</p>';
    } else {
        const planList = document.createElement('div');
        planList.className = 'plan-list';
        
        Object.keys(plans).forEach(planId => {
            const plan = plans[planId];
            const destination = plan.plan?.city_selection?.selected_city || 'Unknown Destination';
            const duration = plan.plan?.itinerary?.daily_schedules?.length || 'Unknown';
            const season = plan.inputs?.season || 'Unknown';
            
            const planCard = document.createElement('div');
            planCard.className = 'plan-card';
            planCard.innerHTML = `
                <div class="plan-card-header">
                    <h3>${destination}</h3>
                    <span class="plan-id">${planId}</span>
                </div>
                <div class="plan-card-body">
                    <div class="plan-detail"><i class="fas fa-calendar-alt"></i> ${duration} day${duration !== 1 ? 's' : ''}</div>
                    <div class="plan-detail"><i class="fas fa-cloud-sun"></i> ${season}</div>
                    <div class="plan-detail"><i class="fas fa-users"></i> ${plan.inputs?.people || '2'} travelers</div>
                </div>
                <button class="load-plan-btn">Load This Plan</button>
            `;
            
            // Add event listener to load button
            const loadButton = planCard.querySelector('.load-plan-btn');
            loadButton.addEventListener('click', function() {
                loadSpecificPlan(planId, plan);
                planSelectorModal.style.display = 'none';
            });
            
            planList.appendChild(planCard);
        });
        
        modalBody.appendChild(planList);
    }
    
    // Show the modal
    planSelectorModal.style.display = 'block';
}

// Function to load and display a specific plan
function loadSpecificPlan(planId, planData) {
    // Add the plan_id to the data for PDF download
    const completeData = {
        ...planData,
        plan_id: planId
    };
    
    // Display the plan
    displayTripDetails(completeData);
}

function displayTripDetails(data) {
    // Clear previous trip data
    clearTripDetails();
    
    // Enable result tabs
    const resultTabs = document.getElementById('result-tabs');
    if (resultTabs) {
        resultTabs.style.display = 'flex';
    }
    
    const noItineraryMessage = document.getElementById('no-itinerary-message');
    if (noItineraryMessage) {
        noItineraryMessage.style.display = 'none';
    }
    
    // Set active tab to overview
    setActiveTab('overview');
    
    // Parse the data if it's a string
    const tripData = typeof data === 'string' ? JSON.parse(data) : data;
    
    // Store the data globally
    currentTripData = tripData;
    
    // Display overview
    populateOverview(tripData);
    
    // Display details for each day
    populateItinerary(tripData);
    
    // Display budget
    populateBudget(tripData);
    
    // Display accommodation
    populateAccommodation(tripData);
    
    // Update title and plan ID
    const resultTitle = document.getElementById('result-title');
    if (resultTitle) {
        resultTitle.innerText = tripData.plan?.city_selection?.selected_city || 'Your Itinerary';
    }
    
    const resultDescription = document.getElementById('result-description');
    if (resultDescription) {
        resultDescription.innerText = tripData.plan?.overview || 'Your personalized travel plan is ready!';
    }
    
    // Set days count
    const daysCount = tripData.plan?.itinerary?.daily_schedules?.length || 0;
    const daysCountElement = document.getElementById('days-count');
    if (daysCountElement) {
        daysCountElement.innerText = daysCount;
    }
    
    // Store plan ID for downloads
    const planIdInput = document.getElementById('plan-id-input');
    if (planIdInput && tripData.plan_id) {
        planIdInput.value = tripData.plan_id;
    }
    
    // Show the result
    const itineraryResult = document.getElementById('itineraryResult');
    if (itineraryResult) {
        itineraryResult.style.display = 'block';
    }
    
    // Hide loading
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

function populateOverview(data) {
    const planData = data.plan || data;
    
    // Set the description
    const overviewText = planData.overview || 'Discover the perfect balance of adventure, culture and relaxation in this destination.';
    const summaryTextElement = document.querySelector('.summary-text');
    if (summaryTextElement) {
        summaryTextElement.innerText = overviewText;
    }
    
    // Populate highlights
    const highlights = planData.highlights || [];
    populateHighlights(highlights);
    
    // Create a 2-column layout for info cards
    const infoGrid = document.querySelector('.info-grid');
    if (!infoGrid) return;
    
    infoGrid.innerHTML = ''; // Clear existing content
    infoGrid.style.display = 'flex';
    infoGrid.style.flexWrap = 'wrap';
    infoGrid.style.gap = '25px';
    
    // Create an array of card data
    const cardData = [
        {
            icon: 'fas fa-map-marker-alt',
            title: 'Top Attractions',
            items: planData.city_research?.attractions || [],
            id: 'attractions-list'
        },
        {
            icon: 'fas fa-utensils',
            title: 'Local Cuisine',
            items: planData.city_research?.cuisine || [],
            id: 'cuisine-list'
        },
        {
            icon: 'fas fa-hands',
            title: 'Cultural Tips',
            items: planData.city_research?.cultural_norms || [],
            id: 'cultural-list'
        },
        {
            icon: 'fas fa-bed',
            title: 'Accommodation Areas',
            items: planData.city_research?.accommodation_areas || planData.accommodation?.recommendations || [],
            id: 'accommodation-list'
        },
        {
            icon: 'fas fa-bus',
            title: 'Transportation Tips',
            items: planData.city_research?.transportation_tips || planData.city_research?.transportation || [],
            id: 'transportation-list'
        }
    ];
    
    // Create the info cards in a flex layout (two columns)
    cardData.forEach(card => {
        const cardElement = createInfoCard(
            card.icon,
            card.title,
            card.items,
            card.id
        );
        cardElement.style.flex = '1 0 45%'; // Make each card take roughly half the width
        infoGrid.appendChild(cardElement);
    });
}

function createInfoCard(icon, title, items, listId) {
    const card = document.createElement('div');
    card.className = 'info-card';
    
    const cardHeader = document.createElement('div');
    cardHeader.className = 'info-card-header';
    
    const iconElement = document.createElement('i');
    iconElement.className = icon;
    
    const titleElement = document.createElement('h4');
    titleElement.innerText = title;
    
    cardHeader.appendChild(iconElement);
    cardHeader.appendChild(titleElement);
    
    const cardContent = document.createElement('div');
    cardContent.className = 'info-card-content';
    
    const list = document.createElement('ul');
    list.className = 'info-list';
    list.id = listId;
    
    // Add items to the list
    if (items && items.length > 0) {
        items.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'info-item';
            listItem.innerText = item;
            list.appendChild(listItem);
        });
    } else {
        const listItem = document.createElement('li');
        listItem.className = 'info-item';
        listItem.innerText = 'Information not available';
        list.appendChild(listItem);
    }
    
    cardContent.appendChild(list);
    
    card.appendChild(cardHeader);
    card.appendChild(cardContent);
    
    return card;
}

function populateItinerary(data) {
    const planData = data.plan || data;
    const container = document.getElementById('itinerary-container');
    if (!container) return;
    
    container.innerHTML = ''; // Clear existing content
    
    // Get daily schedules
    const dailySchedules = planData.itinerary?.daily_schedules || [];
    
    if (dailySchedules.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'empty-itinerary';
        emptyMessage.innerHTML = '<p>No itinerary details available.</p>';
        container.appendChild(emptyMessage);
        return;
    }
    
    // Create a container for each day
    dailySchedules.forEach(day => {
        const dayContainer = document.createElement('div');
        dayContainer.className = 'day-container';
        
        // Day header
        const dayHeader = document.createElement('div');
        dayHeader.className = 'day-header';
        dayHeader.innerHTML = `<h3>Day ${day.day}</h3>`;
        
        dayContainer.appendChild(dayHeader);
        
        // Activities
        const activities = day.activities || [];
        
        if (activities.length === 0) {
            const emptyDayMessage = document.createElement('p');
            emptyDayMessage.className = 'empty-day-message';
            emptyDayMessage.innerText = 'No activities planned for this day.';
            dayContainer.appendChild(emptyDayMessage);
        } else {
            activities.forEach(activity => {
                const activityItem = document.createElement('div');
                activityItem.className = 'activity-item';
                
                const activityTime = document.createElement('div');
                activityTime.className = 'activity-time';
                activityTime.innerText = activity.time || '';
                
                const activityDetails = document.createElement('div');
                activityDetails.className = 'activity-details';
                
                const activityName = document.createElement('div');
                activityName.className = 'activity-name';
                activityName.innerText = activity.activity || '';
                
                activityDetails.appendChild(activityName);
                
                if (activity.location) {
                    const activityLocation = document.createElement('div');
                    activityLocation.className = 'activity-location';
                    activityLocation.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${activity.location}`;
                    activityDetails.appendChild(activityLocation);
                }
                
                // Add transportation info if available
                if (activity.transportation && activity.transportation !== 'N/A') {
                    const activityTransport = document.createElement('div');
                    activityTransport.className = 'activity-transport';
                    activityTransport.innerHTML = `<i class="fas fa-route"></i> ${activity.transportation}`;
                    activityDetails.appendChild(activityTransport);
                }
                
                activityItem.appendChild(activityTime);
                activityItem.appendChild(activityDetails);
                
                dayContainer.appendChild(activityItem);
            });
        }
        
        container.appendChild(dayContainer);
    });
}

function populateBudget(data) {
    const planData = data.plan || data;
    const budget = planData.budget || {};
    
    // Set currency display
            const currencyElement = document.getElementById('budget-currency-display') || document.getElementById('budget-currency');
    if (currencyElement) {
        const currency = data.inputs?.budget_currency || budget.currency || 'USD';
        currencyElement.innerText = currency.toUpperCase();
    }
    
    // Set total cost
    const budgetAmountElement = document.getElementById('budget-amount');
    if (budgetAmountElement) {
        const totalCost = budget.total_cost || '0';
        budgetAmountElement.innerText = totalCost;
    }
    
    // Set budget level
    const budgetLevelElement = document.getElementById('budget-level');
    if (budgetLevelElement) {
        const budgetLevel = data.inputs?.budget || 'Medium';
        budgetLevelElement.innerText = budgetLevel.charAt(0).toUpperCase() + budgetLevel.slice(1);
    }
    
    // Clear existing breakdown
    const breakdownContainer = document.getElementById('budget-breakdown');
    if (!breakdownContainer) return;
    
    breakdownContainer.innerHTML = '';
    
    // Get travel cost if it exists
    let travelCost = null;
    let travelDetails = '';
    if (planData.travel_cost && planData.travel_cost.travel) {
        travelCost = planData.travel_cost.travel.cost;
        travelDetails = planData.travel_cost.travel.details || '';
    }
    
    // Create expense categories array
    const expenseCategories = [
        { key: 'accommodation', icon: 'fas fa-hotel', label: 'Accommodation' },
        { key: 'transportation', icon: 'fas fa-shuttle-van', label: 'Transportation' },
        { key: 'activities', icon: 'fas fa-hiking', label: 'Activities' },
        { key: 'meals', icon: 'fas fa-utensils', label: 'Meals' },
        { key: 'emergency_fund', icon: 'fas fa-first-aid', label: 'Emergency' }
    ];
    
    // Add travel as an additional category if it exists in budget or travel_cost
    const hasTravelInBudget = budget.travel && budget.travel.cost;
    
    if (travelCost && !hasTravelInBudget) {
        expenseCategories.push(
            { key: 'travel', icon: 'fas fa-plane', label: 'Travel', cost: travelCost, details: travelDetails }
        );
    }
    
    // Calculate total for percentage calculation
    let categoryTotal = 0;
    expenseCategories.forEach(category => {
        const categoryData = budget[category.key] || {};
        const cost = category.cost || (typeof categoryData === 'object' ? categoryData.cost : categoryData) || 0;
        categoryTotal += parseFloat(cost) || 0;
    });
    
    // If we have no total, use the total_cost instead
    if (categoryTotal === 0 && budget.total_cost) {
        categoryTotal = parseFloat(budget.total_cost) || 0;
    }
    
    // Create budget chart container if it doesn't exist
    let chartContainer = document.querySelector('.budget-chart-container');
    if (!chartContainer) {
        chartContainer = document.createElement('div');
        chartContainer.className = 'budget-chart-container';
        chartContainer.innerHTML = '<h4>Budget Breakdown</h4><div class="budget-chart"></div>';
        breakdownContainer.appendChild(chartContainer);
    }
    
    const budgetChart = chartContainer.querySelector('.budget-chart');
    if (!budgetChart) return;
    
    // Clear existing chart
    budgetChart.innerHTML = '';
    
    // Create new chart bars
    expenseCategories.forEach(category => {
        const categoryData = budget[category.key] || {};
        const cost = category.cost || (typeof categoryData === 'object' ? categoryData.cost : categoryData) || 0;
        
        // If this category has no cost, skip it
        if (!cost || parseFloat(cost) === 0) return;
        
        // Calculate percentage for the chart
        const percentage = categoryTotal > 0 ? (parseFloat(cost) / categoryTotal * 100) : 0;
        
        // Create chart bar element
        const chartBar = document.createElement('div');
        chartBar.id = `chart-${category.key}`;
        chartBar.className = 'chart-bar';
        
        // Set a gradient background based on the category
        let gradientColor;
        switch (category.key) {
            case 'accommodation':
                gradientColor = 'linear-gradient(to right, #3498db, #2980b9)';
                break;
            case 'transportation':
                gradientColor = 'linear-gradient(to right, #2ecc71, #27ae60)';
                break;
            case 'activities':
                gradientColor = 'linear-gradient(to right, #9b59b6, #8e44ad)';
                break;
            case 'meals':
                gradientColor = 'linear-gradient(to right, #e74c3c, #c0392b)';
                break;
            case 'emergency_fund':
                gradientColor = 'linear-gradient(to right, #f39c12, #d35400)';
                break;
            case 'travel':
                gradientColor = 'linear-gradient(to right, #1abc9c, #16a085)';
                break;
            default:
                gradientColor = 'linear-gradient(to right, #1e73be, #135e9e)';
        }
        
        chartBar.style.background = gradientColor;
        chartBar.style.width = Math.max(5, percentage) + '%';
        
        // Create chart label
        const chartLabel = document.createElement('div');
        chartLabel.className = 'chart-label';
        chartLabel.innerText = category.label;
        
        // Create chart value
        const chartValue = document.createElement('div');
        chartValue.className = 'chart-value';
        
        const currency = data.inputs?.budget_currency || budget.currency || 'USD';
        chartValue.innerText = `${currency.toUpperCase()} ${cost}`;
        
        // Add elements to the chart bar
        chartBar.appendChild(chartLabel);
        chartBar.appendChild(chartValue);
        
        // Add to the chart
        budgetChart.appendChild(chartBar);
        
        // Create a budget category card
        const categoryCard = document.createElement('div');
        categoryCard.className = `budget-category ${category.key}`;
        
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'budget-category-header';
        
        const headerLeft = document.createElement('div');
        headerLeft.innerHTML = `<i class="${category.icon}"></i> ${category.label}`;
        
        const costPill = document.createElement('div');
        costPill.className = 'cost-pill';
        costPill.innerText = `${currency.toUpperCase()} ${cost}`;
        costPill.style.backgroundColor = category.key === 'accommodation' ? '#3498db' : 
                                        category.key === 'transportation' ? '#2ecc71' :
                                        category.key === 'activities' ? '#9b59b6' :
                                        category.key === 'meals' ? '#e74c3c' :
                                        category.key === 'emergency_fund' ? '#f39c12' :
                                        category.key === 'travel' ? '#1abc9c' : '#1e73be';
        
        categoryHeader.appendChild(headerLeft);
        categoryHeader.appendChild(costPill);
        
        const categoryContent = document.createElement('div');
        categoryContent.className = 'budget-category-content';
        
        const details = category.details || (typeof categoryData === 'object' ? categoryData.details : '') || '';
        categoryContent.innerText = details || `Budget allocation for ${category.label.toLowerCase()}.`;
        
        categoryCard.appendChild(categoryHeader);
        categoryCard.appendChild(categoryContent);
        
        breakdownContainer.appendChild(categoryCard);
    });
    
    // Add special note for travel costs if they aren't included in the total
    if (travelCost && !hasTravelInBudget) {
        const noteElement = document.createElement('p');
        noteElement.className = 'budget-note';
        
        const currency = data.inputs?.budget_currency || budget.currency || 'USD';
        noteElement.innerHTML = `<strong>Note:</strong> Travel costs of ${currency.toUpperCase()} ${travelCost} are listed separately and not included in the total budget.`;
        
        breakdownContainer.appendChild(noteElement);
    }
}

function populateAccommodation(data) {
    // This is a placeholder function for future accommodation details
    // You can expand this as needed
}

function populateHighlights(items) {
    const container = document.getElementById('highlights-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (items && items.length > 0) {
        items.forEach(item => {
            const tag = document.createElement('span');
            tag.className = 'highlight-tag';
            tag.innerText = item;
            container.appendChild(tag);
        });
    } else {
        const tag = document.createElement('span');
        tag.className = 'highlight-tag';
        tag.innerText = 'Custom travel experience';
        container.appendChild(tag);
    }
}

function clearTripDetails() {
    // Reset all content containers
    const elements = [
        'highlights-container',
        'attractions-list',
        'cuisine-list',
        'cultural-list',
        'transportation-list',
        'accommodation-list',
        'itinerary-container',
        'budget-breakdown'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = '';
        }
    });
    
    // Hide the result container
    const itineraryResult = document.getElementById('itineraryResult');
    if (itineraryResult) {
        itineraryResult.style.display = 'none';
    }
}

function setActiveTab(tabName) {
    // Get all tab content elements
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Hide all tab contents
    tabContents.forEach(tab => {
        tab.style.display = 'none';
        tab.classList.remove('active');
    });
    
    // Show the selected tab content
    const selectedTab = document.getElementById(tabName + '-tab');
    if (selectedTab) {
        selectedTab.style.display = 'block';
        selectedTab.classList.add('active');
    }
    
    // Update active tab indicator
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        if (tab.getAttribute('data-tab') === tabName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
}

// Add CSS for plan selector
document.addEventListener('DOMContentLoaded', function() {
    // Create stylesheet for plan selector
    const style = document.createElement('style');
    style.textContent = `
        .plan-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .plan-card {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .plan-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        
        .plan-card-header {
            padding: 15px;
            background-color: #1e73be;
            color: white;
            position: relative;
        }
        
        .plan-card-header h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        
        .plan-id {
            font-size: 12px;
            opacity: 0.8;
            display: block;
            margin-top: 5px;
        }
        
        .plan-card-body {
            padding: 15px;
        }
        
        .plan-detail {
            margin-bottom: 8px;
            font-size: 14px;
            display: flex;
            align-items: center;
        }
        
        .plan-detail i {
            margin-right: 8px;
            color: #1e73be;
            width: 20px;
            text-align: center;
        }
        
        .load-plan-btn {
            background-color: #1e73be;
            color: white;
            border: none;
            padding: 10px 15px;
            width: 100%;
            cursor: pointer;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        
        .load-plan-btn:hover {
            background-color: #0e5da0;
        }
        
        /* Improved chart styles */
        .budget-chart-container {
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px dashed #e6f0ff;
        }
        
        .budget-chart-container h4 {
            color: #1e73be;
            font-size: 18px;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .budget-chart {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        .chart-bar {
            position: relative;
            height: 40px;
            border-radius: 20px;
            color: white;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            padding-left: 15px;
            transition: all 0.3s ease-in-out;
            min-width: 5%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }
        
        .chart-bar:hover {
            transform: translateX(5px);
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        }
        
        .chart-label {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            z-index: 2;
        }
        
        .chart-value {
            position: absolute;
            right: 15px;
            font-weight: 600;
        }
    `;
    
    document.head.appendChild(style);
}); 