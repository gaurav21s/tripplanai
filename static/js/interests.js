// Interest selection functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Interests.js loaded - initializing interest selection');
    
    // Initialize interest selection as soon as DOM is loaded
    setupInterestSelection();
    
    // Also set up a mutation observer to handle dynamic changes to the DOM
    // This ensures our functionality works even if the step is loaded dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && 
                mutation.target.id === 'step3' && 
                mutation.target.style.display !== 'none') {
                console.log('Step 3 became visible, ensuring interest selection is working');
                setupInterestSelection();
            }
        });
    });
    
    // Start observing the step3 element for attribute changes
    const step3 = document.getElementById('step3');
    if (step3) {
        observer.observe(step3, { attributes: true });
    }
});

// Define the handler outside any function to avoid recreation
function interestClickHandler() {
    const value = this.getAttribute('data-value');
    console.log('Interests.js: Interest clicked:', value);
    
    // Toggle selected class
    this.classList.toggle('selected');
    
    // Get current selected interests
    const interestsInput = document.getElementById('interests');
    let selectedInterests = interestsInput.value ? interestsInput.value.split(',') : [];
    
    // Update the selected interests array
    if (this.classList.contains('selected')) {
        if (!selectedInterests.includes(value)) {
            selectedInterests.push(value);
        }
    } else {
        selectedInterests = selectedInterests.filter(interest => interest !== value);
    }
    
    // Update hidden input value
    interestsInput.value = selectedInterests.join(',');
    console.log('Interests.js: Updated interests input value:', interestsInput.value);
}

// Main function to set up interest selection
function setupInterestSelection() {
    // Select all interest items and get the hidden input
    const interestItems = document.querySelectorAll('.interest-item');
    const interestsInput = document.getElementById('interests');
    
    console.log(`Interests.js: Found ${interestItems.length} interest items and input field exists: ${!!interestsInput}`);
    
    if (!interestItems.length || !interestsInput) {
        console.log('Interest items or input not found, will try again later');
        return; // Exit if elements aren't found yet
    }
    
    // Array to keep track of selected interests
    let selectedInterests = [];
    
    // Check if there are already selected interests in the hidden input
    if (interestsInput.value) {
        selectedInterests = interestsInput.value.split(',');
        console.log('Interests.js: Pre-existing interests:', selectedInterests);
        
        // Highlight pre-selected interests
        selectedInterests.forEach(interest => {
            const element = document.querySelector(`.interest-item[data-value="${interest}"]`);
            if (element) {
                element.classList.add('selected');
            }
        });
    }
    
    // First remove any existing inline onclick attributes that might interfere
    interestItems.forEach(item => {
        if (item.hasAttribute('onclick')) {
            item.removeAttribute('onclick');
        }
    });
    
    // Then directly set onclick for each item (most reliable cross-browser approach)
    interestItems.forEach(item => {
        item.onclick = interestClickHandler;
    });
    
    // Add direct click handling for any item without the proper CSS
    document.querySelectorAll('.interests-grid div').forEach(item => {
        if (item.classList.contains('interest-item')) {
            // Make sure the item has proper styles for selection
            item.style.cursor = 'pointer';
            
            // Make sure it responds to clicks
            item.onclick = interestClickHandler;
        }
    });
    
    // Setup custom interest functionality
    setupCustomInterests();
}

// Setup custom interest functionality
function setupCustomInterests() {
    const addButton = document.getElementById('add-custom-interest');
    const customInput = document.getElementById('custom-interest');
    const customContainer = document.getElementById('custom-interests-container');
    const interestsInput = document.getElementById('interests');
    
    if (!addButton || !customInput || !customContainer || !interestsInput) {
        return; // Exit if any element isn't found
    }
    
    // Clear any existing handlers by using direct property assignment
    addButton.onclick = function() {
        const interestValue = customInput.value.trim();
        
        if (interestValue) {
            addCustomInterest(interestValue);
            customInput.value = '';
        }
    };
    
    customInput.onkeypress = function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addButton.click();
        }
    };
    
    function addCustomInterest(value) {
        // Create a new custom interest tag
        const tag = document.createElement('div');
        tag.className = 'custom-interest-tag';
        tag.dataset.value = value.toLowerCase();
        
        const tagText = document.createElement('span');
        tagText.textContent = value;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-interest';
        removeBtn.innerHTML = '&times;';
        removeBtn.onclick = function() {
            // Remove from DOM
            tag.remove();
            
            // Remove from hidden input
            const currentInterests = interestsInput.value.split(',');
            const updatedInterests = currentInterests.filter(i => i !== value.toLowerCase());
            interestsInput.value = updatedInterests.join(',');
        };
        
        tag.appendChild(tagText);
        tag.appendChild(removeBtn);
        customContainer.appendChild(tag);
        
        // Add to hidden input
        let currentInterests = interestsInput.value ? interestsInput.value.split(',') : [];
        if (!currentInterests.includes(value.toLowerCase())) {
            currentInterests.push(value.toLowerCase());
            interestsInput.value = currentInterests.join(',');
        }
    }
}

// Add CSS fix to ensure interest items are properly styled when selected
function injectCSSFix() {
    const style = document.createElement('style');
    style.innerHTML = `
        .interest-item {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .interest-item.selected {
            border: 2px solid #4285F4 !important;
            background-color: rgba(66, 133, 244, 0.1) !important;
        }
        .interest-item.selected .interest-icon {
            color: #4285F4 !important;
        }
    `;
    document.head.appendChild(style);
}

// Call the CSS fix injection
injectCSSFix(); 