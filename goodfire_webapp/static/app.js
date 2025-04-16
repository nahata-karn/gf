// Goodfire Feature Explorer - Main Application Logic

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const questionInput = document.getElementById('questionInput');
    const generateBtn = document.getElementById('generateBtn');
    const responseText = document.getElementById('responseText');
    const featureContainer = document.getElementById('featureContainer');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    
    // Feature category containers
    const philosophyFeatures = document.getElementById('philosophyFeatures');
    const writingStyleFeatures = document.getElementById('writingStyleFeatures');
    const scienceFeatures = document.getElementById('scienceFeatures');
    const toneFeatures = document.getElementById('toneFeatures');
    
    // Event listeners
    generateBtn.addEventListener('click', generateResponse);
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateResponse();
        }
    });
    
    // Toggle feature categories when checkbox state changes
    document.querySelectorAll('.feature-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const targetId = this.getAttribute('data-target');
            const container = document.getElementById(targetId);
            
            if (this.checked) {
                container.classList.remove('d-none');
            } else {
                container.classList.add('d-none');
            }
        });
    });
    
    // Main function to generate response and analyze features
    function generateResponse() {
        const question = questionInput.value.trim();
        
        if (!question) {
            errorMessage.textContent = 'Please enter a question or statement to analyze.';
            errorMessage.classList.remove('d-none');
            return;
        }
        
        errorMessage.classList.add('d-none');
        loadingSpinner.classList.remove('d-none');
        responseText.classList.add('d-none');
        featureContainer.classList.add('d-none');
        
        // Get selected feature categories
        const selectedFeatures = Array.from(document.querySelectorAll('.feature-checkbox:checked'))
            .map(checkbox => checkbox.value);
            
        // Mock API call - replace with actual fetch to backend
        setTimeout(() => {
            // This would be replaced with actual API call
            const mockResponse = getMockResponse(question);
            
            // Display the response
            responseText.textContent = mockResponse.response;
            responseText.classList.remove('d-none');
            
            // Clear previous feature results
            clearFeatureContainers();
            
            // Display features based on selected categories
            displayFeatures(mockResponse.features, selectedFeatures);
            
            // Hide loading spinner
            loadingSpinner.classList.add('d-none');
            featureContainer.classList.remove('d-none');
        }, 1500); // Simulate API delay
    }
    
    function clearFeatureContainers() {
        philosophyFeatures.innerHTML = '';
        writingStyleFeatures.innerHTML = '';
        scienceFeatures.innerHTML = '';
        toneFeatures.innerHTML = '';
    }
    
    function displayFeatures(features, selectedCategories) {
        if (selectedCategories.includes('philosophy')) {
            renderFeatureSet(features.philosophy, philosophyFeatures);
        }
        
        if (selectedCategories.includes('writing')) {
            renderFeatureSet(features.writing, writingStyleFeatures);
        }
        
        if (selectedCategories.includes('science')) {
            renderFeatureSet(features.science, scienceFeatures);
        }
        
        if (selectedCategories.includes('tone')) {
            renderFeatureSet(features.tone, toneFeatures);
        }
    }
    
    function renderFeatureSet(featureSet, container) {
        featureSet.forEach(feature => {
            const featureItem = document.createElement('div');
            featureItem.className = 'feature-item mb-3';
            
            const featureName = document.createElement('div');
            featureName.className = 'feature-name';
            featureName.textContent = feature.name;
            
            const strengthBar = document.createElement('div');
            strengthBar.className = 'progress';
            
            const strengthFill = document.createElement('div');
            strengthFill.className = 'progress-bar feature-strength';
            strengthFill.style.width = '0%';
            strengthFill.setAttribute('role', 'progressbar');
            strengthFill.setAttribute('aria-valuenow', feature.strength);
            strengthFill.setAttribute('aria-valuemin', '0');
            strengthFill.setAttribute('aria-valuemax', '100');
            
            const strengthValue = document.createElement('span');
            strengthValue.className = 'strength-value ms-2';
            strengthValue.textContent = feature.strength + '%';
            
            // Animation delay for visual effect
            setTimeout(() => {
                strengthFill.style.width = feature.strength + '%';
            }, 100);
            
            strengthBar.appendChild(strengthFill);
            featureItem.appendChild(featureName);
            featureItem.appendChild(strengthBar);
            featureItem.appendChild(strengthValue);
            
            container.appendChild(featureItem);
        });
    }
    
    // Mock response generator - replace with actual API call in production
    function getMockResponse(question) {
        return {
            response: `This is a simulated response to your question: "${question}". In a real implementation, this would be generated by an AI model based on your input.`,
            features: {
                philosophy: [
                    { name: 'Logic', strength: Math.floor(Math.random() * 100) },
                    { name: 'Ethics', strength: Math.floor(Math.random() * 100) },
                    { name: 'Metaphysics', strength: Math.floor(Math.random() * 100) },
                    { name: 'Epistemology', strength: Math.floor(Math.random() * 100) }
                ],
                writing: [
                    { name: 'Clarity', strength: Math.floor(Math.random() * 100) },
                    { name: 'Coherence', strength: Math.floor(Math.random() * 100) },
                    { name: 'Structure', strength: Math.floor(Math.random() * 100) },
                    { name: 'Persuasiveness', strength: Math.floor(Math.random() * 100) }
                ],
                science: [
                    { name: 'Hypothesis Testing', strength: Math.floor(Math.random() * 100) },
                    { name: 'Data Analysis', strength: Math.floor(Math.random() * 100) },
                    { name: 'Empirical Evidence', strength: Math.floor(Math.random() * 100) },
                    { name: 'Method Rigor', strength: Math.floor(Math.random() * 100) }
                ],
                tone: [
                    { name: 'Formality', strength: Math.floor(Math.random() * 100) },
                    { name: 'Humor', strength: Math.floor(Math.random() * 100) },
                    { name: 'Sentiment', strength: Math.floor(Math.random() * 100) },
                    { name: 'Confidence', strength: Math.floor(Math.random() * 100) }
                ]
            }
        };
    }
}); 