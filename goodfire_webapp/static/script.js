document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const questionForm = document.getElementById('questionForm');
    const questionInput = document.getElementById('questionInput');
    const generateBtn = document.getElementById('generateBtn');
    const responseContainer = document.getElementById('responseContainer');
    const responseText = document.getElementById('responseText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const featureCategories = document.querySelectorAll('.feature-category');
    const featureCheckboxes = document.querySelectorAll('.feature-checkbox');
    
    // Store state
    let currentFeatures = {};
    let responseCount = 0;
    let currentQuestion = '';
    
    // Hide loading spinner initially
    loadingSpinner.style.display = 'none';
    
    // Event listeners
    questionForm.addEventListener('submit', handleFormSubmit);
    
    // Setup feature checkboxes
    featureCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', toggleFeatureCategory);
    });
    
    // Toggle feature category visibility
    function toggleFeatureCategory(e) {
        const targetId = e.target.getAttribute('data-target');
        const targetCategory = document.getElementById(targetId);
        
        if (targetCategory) {
            if (e.target.checked) {
                targetCategory.classList.remove('hidden');
            } else {
                targetCategory.classList.add('hidden');
            }
        }
    }
    
    // Form submission handler
    function handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate input
        const question = questionInput.value.trim();
        if (!question) {
            showError("Please enter a question.");
            return;
        }
        
        // Show loading state
        generateBtn.disabled = true;
        loadingSpinner.style.display = 'block';
        responseText.innerHTML = '';
        clearFeatures();
        responseContainer.classList.remove('d-none');
        
        // Get selected feature categories
        const selectedCategories = getSelectedCategories();
        
        // Reset response tabs
        responseCount = 0;
        currentFeatures = {};
        currentQuestion = question;
        
        // Send request to backend
        fetchResponse(question, selectedCategories);
    }
    
    // Get the currently selected categories
    function getSelectedCategories() {
        const selected = [];
        featureCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selected.push(checkbox.value);
            }
        });
        return selected;
    }
    
    // Fetch response from the server
    function fetchResponse(question, categories, customWeights = null) {
        const payload = { 
            question: question,
            categories: categories
        };
        
        // Add custom weights if provided
        if (customWeights) {
            payload.custom_weights = customWeights;
        }
        
        // Show loading state
        loadingSpinner.style.display = 'block';
        
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Server error: ' + response.status);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayResponse(data, question);
        })
        .catch(error => {
            // Display the error message to the user
            showError(error.message || "An error occurred while processing your request. Please try again.");
        })
        .finally(() => {
            // Reset UI state
            generateBtn.disabled = false;
            loadingSpinner.style.display = 'none';
        });
    }
    
    // Display the response and features
    function displayResponse(data, question) {
        responseCount++;
        const tabId = `response-tab-${responseCount}`;
        
        // Create tabbed interface if it doesn't exist
        if (responseCount === 1) {
            // Create tabs container
            const tabsContainer = document.createElement('div');
            tabsContainer.id = 'response-tabs';
            tabsContainer.className = 'nav nav-tabs mb-3';
            tabsContainer.role = 'tablist';
            
            // Create tab content container
            const tabContent = document.createElement('div');
            tabContent.id = 'response-tab-content';
            tabContent.className = 'tab-content';
            
            // Add to DOM
            responseText.innerHTML = '';
            responseText.appendChild(tabsContainer);
            responseText.appendChild(tabContent);
        }
        
        // Add new tab button
        const tabsContainer = document.getElementById('response-tabs');
        const tabContent = document.getElementById('response-tab-content');
        
        const tabButton = document.createElement('button');
        tabButton.className = `nav-link ${responseCount === 1 ? 'active' : ''}`;
        tabButton.id = `${tabId}-tab`;
        tabButton.dataset.bsToggle = 'tab';
        tabButton.dataset.bsTarget = `#${tabId}`;
        tabButton.type = 'button';
        tabButton.role = 'tab';
        tabButton.ariaControls = tabId;
        tabButton.ariaSelected = responseCount === 1 ? 'true' : 'false';
        tabButton.textContent = `Response ${responseCount}`;
        
        // Add tab click event handlers manually (for cases where Bootstrap JS might not fully initialize)
        tabButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Deactivate all tabs
            const allTabs = tabsContainer.querySelectorAll('.nav-link');
            allTabs.forEach(tab => {
                tab.classList.remove('active');
                tab.setAttribute('aria-selected', 'false');
            });
            
            // Deactivate all tab panes
            const allTabPanes = tabContent.querySelectorAll('.tab-pane');
            allTabPanes.forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Activate this tab
            tabButton.classList.add('active');
            tabButton.setAttribute('aria-selected', 'true');
            
            // Activate corresponding tab pane
            const targetPane = document.getElementById(tabId);
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
        });
        
        // Add tab button to container
        tabsContainer.appendChild(tabButton);
        
        // Create tab content
        const tabPane = document.createElement('div');
        tabPane.className = `tab-pane fade ${responseCount === 1 ? 'show active' : ''}`;
        tabPane.id = tabId;
        tabPane.role = 'tabpanel';
        tabPane.ariaLabelledby = `${tabId}-tab`;
        
        // Create response text container
        const responseTextContent = document.createElement('div');
        responseTextContent.className = 'response-content';
        responseTextContent.textContent = data.response || "No response generated.";
        
        // Add response to tab pane
        tabPane.appendChild(responseTextContent);
        
        // Add tab content to container
        tabContent.appendChild(tabPane);
        
        // Show response container
        responseContainer.classList.remove('d-none');
        
        // Display features if available
        if (data.features_by_category && Object.keys(data.features_by_category).length > 0) {
            displayFeaturesByCategory(data.features_by_category);
            addRegenerateButton();
        } else {
            showMessage("No features were detected in this response.");
        }
    }
    
    // Add regenerate button
    function addRegenerateButton() {
        // Remove existing button if it exists
        const existingButton = document.getElementById('regenerate-btn');
        if (existingButton) {
            existingButton.remove();
        }
        
        // Create regenerate button
        const regenerateBtn = document.createElement('button');
        regenerateBtn.id = 'regenerate-btn';
        regenerateBtn.className = 'btn btn-primary mt-3';
        regenerateBtn.textContent = 'Regenerate with New Weights';
        
        // Add event listener
        regenerateBtn.addEventListener('click', handleRegenerate);
        
        // Add button below the response box instead of the feature section
        const responseContainer = document.getElementById('responseContainer');
        responseContainer.appendChild(regenerateBtn);
    }
    
    // Handle regenerate button click
    function handleRegenerate() {
        // Get the current custom weights from sliders
        const customWeights = {};
        let hasChangedWeights = false;
        
        console.log("Collecting weights from features...");
        
        // Collect all feature weights
        Object.keys(currentFeatures).forEach(categoryId => {
            console.log(`Category: ${categoryId}`);
            currentFeatures[categoryId].forEach(feature => {
                const sliderId = `feature-slider-${feature.uuid}`;
                const slider = document.getElementById(sliderId);
                if (slider) {
                    const value = parseFloat(slider.value);
                    const initialValue = parseFloat(slider.dataset.initialValue);
                    customWeights[feature.uuid] = value;
                    
                    console.log(`Feature: ${feature.label}, UUID: ${feature.uuid}, Value: ${value}, Initial: ${initialValue}`);
                    
                    // Check if the slider has been moved from its initial position
                    if (value !== initialValue) {
                        hasChangedWeights = true;
                        console.log(`Weight changed for: ${feature.label}`);
                    }
                }
            });
        });
        
        // Check if any weights were changed
        if (!hasChangedWeights) {
            showMessage("Please adjust at least one feature weight before regenerating.");
            return;
        }
        
        // Show loading state
        const regenerateBtn = document.getElementById('regenerate-btn');
        regenerateBtn.disabled = true;
        regenerateBtn.textContent = 'Regenerating...';
        
        // Get selected feature categories
        const selectedCategories = getSelectedCategories();
        
        // Fetch response with custom weights
        fetchResponse(currentQuestion, selectedCategories, customWeights);
        
        // Reset button state after a delay
        setTimeout(() => {
            if (regenerateBtn) {
                regenerateBtn.disabled = false;
                regenerateBtn.textContent = 'Regenerate with New Weights';
            }
        }, 3000);
    }
    
    // Display a message in the response area
    function showMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'alert alert-info mt-3';
        messageElement.textContent = message;
        
        // If there's a tab container, add to the active tab
        if (responseCount > 0) {
            const activeTabPane = document.querySelector('.tab-pane.active');
            if (activeTabPane) {
                activeTabPane.appendChild(messageElement);
                return;
            }
        }
        
        // Otherwise add directly to the response container
        responseText.appendChild(messageElement);
    }
    
    // Display features grouped by category
    function displayFeaturesByCategory(featuresByCategory) {
        // Clear existing features
        clearFeatures();
        
        // Store features with metadata
        currentFeatures = {};
        
        // Process features by category
        Object.keys(featuresByCategory).forEach(category => {
            const features = featuresByCategory[category];
            let categoryId;
            
            // Map category names to their corresponding IDs
            switch(category) {
                case 'philosophy':
                    categoryId = 'philosophyFeatures';
                    break;
                case 'writing style':
                    categoryId = 'writingStyleFeatures';
                    break;
                case 'tone':
                    categoryId = 'toneFeatures';
                    break;
                case 'scientific concepts':
                    categoryId = 'scienceFeatures';
                    break;
                default:
                    return; // Skip unknown categories
            }
            
            // Store features for this category
            currentFeatures[categoryId] = features;
            
            const categoryContainer = document.getElementById(categoryId);
            const categoryParent = document.getElementById(categoryId.replace('Features', 'Category'));
            
            if (categoryContainer && features && features.length > 0) {
                // Show the category container
                categoryParent.classList.remove('hidden');
                
                // Create feature items
                features.forEach((feature, index) => {
                    const featureItem = createFeatureElement(feature, index);
                    categoryContainer.appendChild(featureItem);
                });
                
                // Make sure checkbox is checked
                const checkboxId = categoryId.replace('Features', 'Check');
                const checkbox = document.getElementById(checkboxId);
                if (checkbox) {
                    checkbox.checked = true;
                }
            }
        });
    }
    
    // Create a feature element
    function createFeatureElement(feature, index) {
        const featureItem = document.createElement('div');
        featureItem.className = 'feature-item';
        
        // Feature name and value container
        const featureHeader = document.createElement('div');
        featureHeader.className = 'feature-header';
        
        const featureName = document.createElement('span');
        featureName.className = 'feature-name';
        featureName.textContent = formatFeatureName(feature.label || feature.name);
        
        const featureValue = document.createElement('span');
        featureValue.className = 'feature-value';
        featureValue.textContent = `: ${(feature.activation || feature.value).toFixed(4)}`;
        
        // Add to header
        featureHeader.appendChild(featureName);
        featureHeader.appendChild(featureValue);
        featureItem.appendChild(featureHeader);
        
        // Create slider container
        const sliderContainer = document.createElement('div');
        sliderContainer.className = 'feature-slider-container mt-2';
        
        // Create slider
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '-1';
        slider.max = '1';
        slider.step = '0.1';
        slider.value = '0'; // Default value
        slider.dataset.initialValue = '0'; // Track initial value
        slider.className = 'form-range feature-slider';
        slider.id = `feature-slider-${feature.uuid}`;
        
        // Create slider value display
        const sliderValue = document.createElement('span');
        sliderValue.className = 'feature-slider-value';
        sliderValue.textContent = '0';
        
        // Update slider value display when slider changes
        slider.addEventListener('input', function() {
            sliderValue.textContent = this.value;
            // Add a visual indication that the slider has been changed
            if (this.value !== this.dataset.initialValue) {
                this.classList.add('slider-changed');
            } else {
                this.classList.remove('slider-changed');
            }
        });
        
        // Add to container
        sliderContainer.appendChild(document.createTextNode('Weight: '));
        sliderContainer.appendChild(sliderValue);
        sliderContainer.appendChild(slider);
        
        // Add slider container to feature item
        featureItem.appendChild(sliderContainer);
        
        return featureItem;
    }
    
    // Format feature name for display
    function formatFeatureName(name) {
        return name
            .replace(/_/g, ' ')
            .replace(/\./g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    // Clear all features
    function clearFeatures() {
        featureCategories.forEach(category => {
            category.classList.add('hidden');
            const featuresContainer = category.querySelector('.feature-list');
            if (featuresContainer) {
                featuresContainer.innerHTML = '';
            }
        });
        
        // Remove regenerate button if it exists
        const existingButton = document.getElementById('regenerate-btn');
        if (existingButton) {
            existingButton.remove();
        }
    }
    
    // Show error message
    function showError(message) {
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = message;
        
        responseText.innerHTML = '';
        responseText.appendChild(errorAlert);
        responseContainer.classList.remove('d-none');
    }
}); 