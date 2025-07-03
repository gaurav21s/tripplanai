// API Key Manager
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const manageApiKeyBtn = document.getElementById('manageApiKey');
    const apiKeyModal = document.getElementById('apiKeyModal');
    const closeApiKeyModal = document.getElementById('closeApiKeyModal');
    const apiKeyInput = document.getElementById('openai-api-key-input');
    const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
    const clearApiKeyBtn = document.getElementById('clearApiKeyBtn');
    const toggleApiKeyBtn = document.getElementById('toggleApiKeyVisibility');
    
    // Initialize - fetch existing API key
    if (apiKeyInput) {
        fetch('/get_api_key')
            .then(response => response.json())
            .then(data => {
                if (data.api_key) {
                    apiKeyInput.value = data.api_key;
                }
            })
            .catch(error => console.error('Error fetching API key:', error));
    }
    
    // Open modal when "Manage API Key" is clicked
    if (manageApiKeyBtn && apiKeyModal) {
        manageApiKeyBtn.addEventListener('click', function(e) {
            e.preventDefault();
            apiKeyModal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
        });
    }
    
    // Close modal functions
    function closeModal() {
        if (apiKeyModal) {
            apiKeyModal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scrolling
        }
    }
    
    // Close when X is clicked
    if (closeApiKeyModal) {
        closeApiKeyModal.addEventListener('click', closeModal);
    }
    
    // Close when clicking outside the modal
    window.addEventListener('click', function(event) {
        if (event.target === apiKeyModal) {
            closeModal();
        }
    });
    
    // Toggle API key visibility (show/hide password)
    if (toggleApiKeyBtn && apiKeyInput) {
        toggleApiKeyBtn.addEventListener('click', function() {
            const type = apiKeyInput.type === 'password' ? 'text' : 'password';
            apiKeyInput.type = type;
            toggleApiKeyBtn.innerHTML = type === 'password' ? 
                '<i class="fas fa-eye"></i>' : 
                '<i class="fas fa-eye-slash"></i>';
        });
    }
    
    // Save API key
    if (saveApiKeyBtn && apiKeyInput) {
        saveApiKeyBtn.addEventListener('click', function() {
            const apiKey = apiKeyInput.value.trim();
            if (!apiKey) {
                alert('Please enter your OpenAI API key');
                return;
            }
            
            fetch('/save_api_key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('API key saved successfully!');
                    closeModal();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error saving API key:', error);
                alert('Error saving API key');
            });
        });
    }
    
    // Clear API key
    if (clearApiKeyBtn) {
        clearApiKeyBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear your API key?')) {
                fetch('/clear_api_key', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (apiKeyInput) apiKeyInput.value = '';
                        alert('API key cleared successfully!');
                    } else {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error clearing API key:', error);
                    alert('Error clearing API key');
                });
            }
        });
    }
}); 