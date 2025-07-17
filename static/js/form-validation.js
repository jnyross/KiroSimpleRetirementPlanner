/**
 * Client-side form validation for the retirement calculator
 * Provides real-time feedback and validation before form submission
 */

class FormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.fields = {};
        this.isValid = false;
        this.isInitialized = false;
        
        if (!this.form) {
            console.error(`Form with id '${formId}' not found`);
            return;
        }
        
        this.initializeFields();
        this.attachEventListeners();
        // Don't validate on initial load
        this.isInitialized = true;
        this.updateSubmitButton(false);
    }
    
    /**
     * Initialize form fields and their validation rules
     */
    initializeFields() {
        this.fields = {
            current_age: {
                element: this.form.querySelector('#current_age'),
                rules: {
                    required: true,
                    min: 18,
                    max: 80,
                    type: 'integer'
                },
                messages: {
                    required: 'Current age is required',
                    min: 'Age must be at least 18',
                    max: 'Age must be 80 or less',
                    invalid: 'Please enter a valid age'
                }
            },
            current_savings: {
                element: this.form.querySelector('#current_savings'),
                rules: {
                    required: true,
                    min: 0,
                    max: 10000000,
                    type: 'number'
                },
                messages: {
                    required: 'Current savings amount is required',
                    min: 'Savings cannot be negative',
                    max: 'Amount seems unusually high, please verify',
                    invalid: 'Please enter a valid amount'
                }
            },
            monthly_savings: {
                element: this.form.querySelector('#monthly_savings'),
                rules: {
                    required: true,
                    min: 0,
                    max: 50000,
                    type: 'number'
                },
                messages: {
                    required: 'Monthly savings amount is required',
                    min: 'Monthly savings cannot be negative',
                    max: 'Monthly amount seems unusually high, please verify',
                    invalid: 'Please enter a valid amount'
                }
            },
            desired_annual_income: {
                element: this.form.querySelector('#desired_annual_income'),
                rules: {
                    required: true,
                    min: 1000,
                    max: 500000,
                    type: 'number'
                },
                messages: {
                    required: 'Desired annual income is required',
                    min: 'Annual income must be at least £1,000',
                    max: 'Annual income must be £500,000 or less',
                    invalid: 'Please enter a valid income amount'
                }
            },
            target_success_rate: {
                element: this.form.querySelector('#target_success_rate'),
                rules: {
                    required: true,
                    min: 50,
                    max: 100,
                    type: 'integer'
                },
                messages: {
                    required: 'Target success rate is required',
                    min: 'Success rate must be at least 50%',
                    max: 'Success rate must be 100% or less',
                    invalid: 'Please enter a valid success rate'
                }
            }
        };
    }
    
    /**
     * Attach event listeners to form fields
     */
    attachEventListeners() {
        // Add real-time validation on input
        Object.keys(this.fields).forEach(fieldName => {
            const field = this.fields[fieldName];
            if (field.element) {
                // Track if field has been touched
                field.touched = false;
                
                // Validate on input (real-time) - but only if field has been touched
                field.element.addEventListener('input', () => {
                    if (field.touched || field.element.value.trim() !== '') {
                        this.validateField(fieldName);
                        this.updateSubmitButton();
                    }
                });
                
                // Validate on blur (when user leaves field)
                field.element.addEventListener('blur', () => {
                    field.touched = true;
                    this.validateField(fieldName);
                    this.updateSubmitButton();
                });
                
                // Clear errors on focus
                field.element.addEventListener('focus', () => {
                    // Only clear error if field is empty (to avoid clearing valid errors)
                    if (field.element.value.trim() === '') {
                        this.clearFieldError(fieldName);
                    }
                });
            }
        });
        
        // Prevent form submission if invalid
        this.form.addEventListener('submit', (e) => {
            if (!this.validateAllFields()) {
                e.preventDefault();
                this.showFormErrors();
            }
        });
    }
    
    /**
     * Validate a specific field
     * @param {string} fieldName - Name of the field to validate
     * @returns {boolean} - True if field is valid
     */
    validateField(fieldName) {
        const field = this.fields[fieldName];
        if (!field || !field.element) return false;
        
        const value = field.element.value.trim();
        const rules = field.rules;
        
        // Check if required
        if (rules.required && !value) {
            this.showFieldError(fieldName, field.messages.required);
            return false;
        }
        
        // Skip other validations if field is empty and not required
        if (!value && !rules.required) {
            this.clearFieldError(fieldName);
            return true;
        }
        
        // Type validation
        let numValue;
        if (rules.type === 'number' || rules.type === 'integer') {
            numValue = parseFloat(value);
            if (isNaN(numValue)) {
                this.showFieldError(fieldName, field.messages.invalid);
                return false;
            }
            
            if (rules.type === 'integer' && !Number.isInteger(numValue)) {
                this.showFieldError(fieldName, field.messages.invalid);
                return false;
            }
        }
        
        // Range validation
        if (rules.min !== undefined && numValue < rules.min) {
            this.showFieldError(fieldName, field.messages.min);
            return false;
        }
        
        if (rules.max !== undefined && numValue > rules.max) {
            this.showFieldError(fieldName, field.messages.max);
            return false;
        }
        
        // Custom cross-field validation
        if (fieldName === 'desired_annual_income') {
            const monthlySavings = this.getFieldValue('monthly_savings');
            if (monthlySavings && numValue) {
                const annualSavings = monthlySavings * 12;
                if (numValue > annualSavings * 50) {
                    this.showFieldError(fieldName, 
                        'Desired income seems very high compared to your savings rate. ' +
                        'Consider adjusting either your income goal or savings amount.'
                    );
                    return false;
                }
            }
        }
        
        // Field is valid
        this.clearFieldError(fieldName);
        return true;
    }
    
    /**
     * Validate all form fields
     * @returns {boolean} - True if all fields are valid
     */
    validateAllFields() {
        let allValid = true;
        
        Object.keys(this.fields).forEach(fieldName => {
            if (!this.validateField(fieldName)) {
                allValid = false;
            }
        });
        
        this.isValid = allValid;
        return allValid;
    }
    
    /**
     * Get the numeric value of a field
     * @param {string} fieldName - Name of the field
     * @returns {number|null} - Numeric value or null if invalid
     */
    getFieldValue(fieldName) {
        const field = this.fields[fieldName];
        if (!field || !field.element) return null;
        
        // Use raw value if available (for compatibility)
        const rawValue = field.element.dataset.rawValue;
        const value = rawValue || field.element.value.trim();
        if (!value) return null;
        
        const numValue = parseFloat(value);
        return isNaN(numValue) ? null : numValue;
    }
    
    /**
     * Show error message for a specific field
     * @param {string} fieldName - Name of the field
     * @param {string} message - Error message to display
     */
    showFieldError(fieldName, message) {
        const field = this.fields[fieldName];
        if (!field || !field.element) return;
        
        // Add error class to field
        field.element.classList.add('error');
        
        // Find or create error message element
        let errorElement = field.element.parentNode.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            field.element.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    /**
     * Clear error message for a specific field
     * @param {string} fieldName - Name of the field
     */
    clearFieldError(fieldName) {
        const field = this.fields[fieldName];
        if (!field || !field.element) return;
        
        // Remove error class from field
        field.element.classList.remove('error');
        
        // Hide error message
        const errorElement = field.element.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    /**
     * Show general form errors
     */
    showFormErrors() {
        // Scroll to first error field
        const firstErrorField = this.form.querySelector('.error');
        if (firstErrorField) {
            firstErrorField.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            firstErrorField.focus();
        }
        
        // Show general error message
        this.showGeneralError('Please correct the errors above before submitting.');
    }
    
    /**
     * Show general error message
     * @param {string} message - Error message to display
     */
    showGeneralError(message) {
        let errorContainer = this.form.querySelector('.form-error-message');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.className = 'form-error-message';
            this.form.insertBefore(errorContainer, this.form.firstChild);
        }
        
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    }
    
    /**
     * Clear general error message
     */
    clearGeneralError() {
        const errorContainer = this.form.querySelector('.form-error-message');
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }
    }
    
    /**
     * Update submit button state based on form validity
     */
    updateSubmitButton(validate = true) {
        const submitButton = this.form.querySelector('button[type="submit"]');
        if (!submitButton) return;
        
        // Only validate if requested and form is initialized
        const isFormValid = validate && this.isInitialized ? this.validateAllFields() : false;
        
        if (!validate || isFormValid) {
            submitButton.disabled = false;
            submitButton.classList.remove('disabled');
            submitButton.textContent = 'Calculate My Retirement';
            if (validate) {
                this.clearGeneralError();
            }
        } else {
            submitButton.disabled = true;
            submitButton.classList.add('disabled');
            submitButton.textContent = 'Please Complete Form';
        }
    }
    
    /**
     * Get form data as an object
     * @returns {object} - Form data object
     */
    getFormData() {
        const data = {};
        Object.keys(this.fields).forEach(fieldName => {
            const value = this.getFieldValue(fieldName);
            if (value !== null) {
                data[fieldName] = value;
            }
        });
        return data;
    }
    
    /**
     * Reset form and clear all errors
     */
    reset() {
        this.form.reset();
        Object.keys(this.fields).forEach(fieldName => {
            this.clearFieldError(fieldName);
        });
        this.clearGeneralError();
        this.updateSubmitButton();
    }
}

// Initialize form validation when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the calculator form validator
    window.calculatorFormValidator = new FormValidator('calculator-form');
    
    // Note: Number formatting with commas removed because HTML5 number inputs
    // don't accept formatted values. The browser provides its own number formatting.
});