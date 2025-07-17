/**
 * Results display and user interface handler for the retirement calculator
 * Handles dynamic results population, chart rendering, and navigation
 */

class ResultsHandler {
    constructor() {
        this.currentResults = null;
        this.currentCharts = null;
        this.isCalculating = false;
        this.calculationId = null;
        this.savedScenarios = this.loadSavedScenarios();
        
        this.initializeElements();
        this.attachEventListeners();
        this.setupActionButtons();
        this.setupScenarioComparison();
    }
    
    /**
     * Initialize DOM elements and references
     */
    initializeElements() {
        // Form elements
        this.form = document.getElementById('calculator-form');
        this.calculateBtn = document.getElementById('calculate-btn');
        this.modifyInputsBtn = document.getElementById('modify-inputs-btn');
        
        // Progress bar elements
        this.progressContainer = document.getElementById('progress-container');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.progressStatus = document.getElementById('progress-status');
        this.progressPortfolio = document.getElementById('progress-portfolio');
        
        // Results section elements
        this.resultsSection = document.getElementById('results');
        this.recommendedPortfolio = document.getElementById('recommended-portfolio');
        this.recommendedName = document.getElementById('recommended-name');
        this.recommendedAge = document.getElementById('recommended-age');
        this.recommendedSuccess = document.getElementById('recommended-success');
        this.resultsTableBody = document.getElementById('results-tbody');
        this.portfolioSelect = document.getElementById('portfolio-select');
        this.chartDisplay = document.getElementById('chart-display');
        
        // Button text elements
        this.btnText = this.calculateBtn?.querySelector('.btn-text');
        this.btnLoading = this.calculateBtn?.querySelector('.btn-loading');
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Form submission
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleCalculation();
            });
        }
        
        // Modify inputs button
        if (this.modifyInputsBtn) {
            this.modifyInputsBtn.addEventListener('click', () => {
                this.showInputForm();
            });
        }
        
        // Quick edit button
        const quickEditBtn = document.getElementById('quick-edit-btn');
        if (quickEditBtn) {
            quickEditBtn.addEventListener('click', () => {
                this.showQuickEditModal();
            });
        }
        
        // Quick edit modal handlers
        this.setupQuickEditModal();
        
        // Portfolio selector for charts
        if (this.portfolioSelect) {
            this.portfolioSelect.addEventListener('change', (e) => {
                this.displayChart(e.target.value);
            });
        }
        
        // Handle browser back/forward navigation
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.section) {
                if (e.state.section === 'results') {
                    this.showResults();
                } else {
                    this.showInputForm();
                }
            }
        });
    }
    
    /**
     * Handle form submission and calculation
     */
    async handleCalculation() {
        if (this.isCalculating) return;
        
        // Validate form first
        if (window.calculatorFormValidator && !window.calculatorFormValidator.validateAllFields()) {
            return;
        }
        
        try {
            this.setCalculatingState(true);
            this.showProgressBar();
            
            // Get form data
            const formData = this.getFormData();
            
            // Submit calculation request
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentResults = result;
                this.currentCharts = result.charts;
                this.calculationId = result.calculation_id;
                
                // Final progress update
                this.updateProgress(100, 'Complete', 'Preparing results...');
                
                // Small delay to show completion
                await new Promise(resolve => setTimeout(resolve, 500));
                
                this.displayResults(result);
                this.showResults();
                this.hideProgressBar();
                
                // Update browser history
                history.pushState({ section: 'results' }, 'Results', '#results');
                
            } else {
                this.handleCalculationError(result.error || 'Calculation failed', result.errors);
            }
            
        } catch (error) {
            console.error('Calculation error:', error);
            this.handleCalculationError('Network error occurred. Please try again.');
        } finally {
            this.setCalculatingState(false);
            this.hideProgressBar();
        }
    }
    
    /**
     * Get form data as object
     */
    getFormData() {
        if (window.calculatorFormValidator) {
            return window.calculatorFormValidator.getFormData();
        }
        
        // Fallback manual form data collection
        const formData = new FormData(this.form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = parseFloat(value) || 0;
        }
        return data;
    }
    
    /**
     * Set calculating state (loading/normal)
     */
    setCalculatingState(calculating) {
        this.isCalculating = calculating;
        
        if (this.calculateBtn) {
            this.calculateBtn.disabled = calculating;
            
            if (this.btnText && this.btnLoading) {
                if (calculating) {
                    this.btnText.style.display = 'none';
                    this.btnLoading.style.display = 'flex';
                } else {
                    this.btnText.style.display = 'inline';
                    this.btnLoading.style.display = 'none';
                }
            } else {
                // Fallback if loading elements don't exist
                this.calculateBtn.textContent = calculating ? 'Calculating...' : 'Calculate My Retirement';
            }
        }
    }
    
    /**
     * Show progress bar
     */
    showProgressBar() {
        if (this.progressContainer) {
            this.progressContainer.style.display = 'block';
            this.updateProgress(0, 'Starting calculation...', 'Initializing Monte Carlo simulation...');
            
            // Start simulated progress updates
            this.startProgressSimulation();
        }
    }
    
    /**
     * Hide progress bar
     */
    hideProgressBar() {
        if (this.progressContainer) {
            this.progressContainer.style.display = 'none';
        }
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }
    
    /**
     * Update progress bar
     */
    updateProgress(percentage, status, portfolioInfo) {
        if (this.progressFill) {
            this.progressFill.style.width = `${percentage}%`;
        }
        
        if (this.progressText) {
            this.progressText.textContent = `${Math.round(percentage)}%`;
        }
        
        if (this.progressStatus) {
            this.progressStatus.textContent = status;
        }
        
        if (this.progressPortfolio) {
            this.progressPortfolio.textContent = portfolioInfo;
        }
    }
    
    /**
     * Start progress simulation
     */
    startProgressSimulation() {
        let progress = 0;
        const portfolios = [
            'Cash Only',
            '100% Bonds',
            '25% Equities/75% Bonds',
            '50% Equities/50% Bonds',
            '75% Equities/25% Bonds',
            '100% Equities'
        ];
        
        let currentPortfolio = 0;
        
        this.progressInterval = setInterval(() => {
            progress += Math.random() * 15; // Random progress increment
            
            if (progress > 90) {
                progress = 90; // Cap at 90% until real completion
            }
            
            // Update current portfolio being processed
            const portfolioIndex = Math.floor((progress / 90) * portfolios.length);
            if (portfolioIndex < portfolios.length) {
                currentPortfolio = portfolioIndex;
            }
            
            let status = 'Running Monte Carlo simulations...';
            if (progress > 80) {
                status = 'Generating charts and analysis...';
            } else if (progress > 50) {
                status = 'Analyzing portfolio performance...';
            }
            
            this.updateProgress(
                progress,
                status,
                `Processing ${portfolios[currentPortfolio]} portfolio...`
            );
            
            // Stop the simulation when we reach 90%
            if (progress >= 90) {
                clearInterval(this.progressInterval);
                this.progressInterval = null;
            }
        }, 300); // Update every 300ms
    }
    
    /**
     * Display calculation results
     */
    displayResults(result) {
        // Display recommended portfolio
        this.displayRecommendedPortfolio(result);
        
        // Display results table
        this.displayResultsTable(result.results, result.user_input.target_success_rate);
        
        // Setup chart selector and display first chart
        this.setupChartSelector(result.results, result.charts);
        
        // Display first available chart
        this.displayFirstChart(result.charts);
        
        // Populate input summary
        this.displayInputSummary(result.user_input);
        
        // Display calculation details
        this.displayCalculationDetails(result);
    }
    
    /**
     * Display recommended portfolio section
     */
    displayRecommendedPortfolio(result) {
        const recommendationCard = document.getElementById('recommendation-card');
        const noRecommendationCard = document.getElementById('no-recommendation-card');
        
        if (result.recommended_portfolio && result.recommended_age) {
            // Find the recommended portfolio details
            const recommendedResult = result.results.find(r => 
                r.portfolio_name === result.recommended_portfolio
            );
            
            if (recommendedResult) {
                // Show recommendation card
                if (recommendationCard) {
                    recommendationCard.style.display = 'flex';
                }
                if (noRecommendationCard) {
                    noRecommendationCard.style.display = 'none';
                }
                
                // Populate recommendation details
                if (this.recommendedName) {
                    this.recommendedName.textContent = recommendedResult.portfolio_allocation.name;
                }
                if (this.recommendedAge) {
                    this.recommendedAge.textContent = result.recommended_age;
                }
                if (this.recommendedSuccess) {
                    this.recommendedSuccess.textContent = `${Math.round(recommendedResult.success_rate * 100)}%`;
                }
                
                // Additional details
                const recommendedValue = document.getElementById('recommended-value');
                const recommendedYears = document.getElementById('recommended-years');
                
                if (recommendedValue && recommendedResult.final_portfolio_value > 0) {
                    recommendedValue.textContent = `£${recommendedResult.final_portfolio_value.toLocaleString('en-GB', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    })}`;
                }
                
                if (recommendedYears && result.user_input) {
                    const yearsToRetirement = result.recommended_age - result.user_input.current_age;
                    recommendedYears.textContent = `${yearsToRetirement} years`;
                }
            }
        } else {
            // No portfolio achieves 99% confidence
            if (recommendationCard) {
                recommendationCard.style.display = 'none';
            }
            if (noRecommendationCard) {
                noRecommendationCard.style.display = 'flex';
            }
        }
    }
    
    /**
     * Display results table
     */
    displayResultsTable(results, targetSuccessRate) {
        if (!this.resultsTableBody) return;
        
        // Clear existing rows
        this.resultsTableBody.innerHTML = '';
        
        // Sort results by retirement age (successful ones first, then by age)
        const sortedResults = [...results].sort((a, b) => {
            // Successful portfolios first
            if (a.success_rate >= targetSuccessRate && b.success_rate < targetSuccessRate) return -1;
            if (b.success_rate >= targetSuccessRate && a.success_rate < targetSuccessRate) return 1;
            
            // Among successful portfolios, sort by retirement age
            if (a.success_rate >= targetSuccessRate && b.success_rate >= targetSuccessRate) {
                if (a.retirement_age === null) return 1;
                if (b.retirement_age === null) return -1;
                return a.retirement_age - b.retirement_age;
            }
            
            // Among unsuccessful portfolios, sort by success rate (descending)
            return b.success_rate - a.success_rate;
        });
        
        sortedResults.forEach((result, index) => {
            const row = this.createResultRow(result, index === 0 && result.success_rate >= targetSuccessRate);
            this.resultsTableBody.appendChild(row);
        });
    }
    
    /**
     * Create a table row for a result
     */
    createResultRow(result, isRecommended) {
        const row = document.createElement('tr');
        
        if (isRecommended) {
            row.classList.add('recommended-row');
        }
        
        // Portfolio name
        const nameCell = document.createElement('td');
        nameCell.textContent = result.portfolio_allocation.name;
        if (isRecommended) {
            nameCell.innerHTML += ' <span style="color: #27ae60; font-weight: bold;">★ Recommended</span>';
        }
        row.appendChild(nameCell);
        
        // Portfolio allocation
        const allocationCell = document.createElement('td');
        const allocation = result.portfolio_allocation;
        const allocationBreakdown = this.createAllocationBreakdown(allocation);
        allocationCell.appendChild(allocationBreakdown);
        row.appendChild(allocationCell);
        
        // Retirement age
        const ageCell = document.createElement('td');
        if (result.retirement_age !== null) {
            ageCell.textContent = result.retirement_age;
        } else {
            ageCell.textContent = 'Not achievable';
            ageCell.style.color = '#e74c3c';
            ageCell.style.fontStyle = 'italic';
        }
        row.appendChild(ageCell);
        
        // Success rate
        const successCell = document.createElement('td');
        const successRate = Math.round(result.success_rate * 100);
        successCell.textContent = `${successRate}%`;
        
        if (successRate >= 99) {
            successCell.style.color = '#27ae60';
            successCell.style.fontWeight = 'bold';
        } else if (successRate >= 90) {
            successCell.style.color = '#f39c12';
        } else {
            successCell.style.color = '#e74c3c';
        }
        row.appendChild(successCell);
        
        // Portfolio value
        const valueCell = document.createElement('td');
        if (result.final_portfolio_value > 0) {
            valueCell.textContent = `£${result.final_portfolio_value.toLocaleString('en-GB', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            })}`;
        } else {
            valueCell.textContent = 'N/A';
            valueCell.style.color = '#7f8c8d';
        }
        row.appendChild(valueCell);
        
        return row;
    }
    
    /**
     * Setup chart selector dropdown
     */
    setupChartSelector(results, charts) {
        if (!this.portfolioSelect || !charts || !charts.portfolio_charts) return;
        
        // Clear existing options
        this.portfolioSelect.innerHTML = '';
        
        // Add options for each portfolio with charts
        Object.keys(charts.portfolio_charts).forEach(portfolioName => {
            const option = document.createElement('option');
            option.value = portfolioName;
            option.textContent = portfolioName;
            this.portfolioSelect.appendChild(option);
        });
        
        // Add comparison chart option if available
        if (charts.comparison_chart) {
            const option = document.createElement('option');
            option.value = 'comparison';
            option.textContent = 'Compare All Portfolios';
            this.portfolioSelect.appendChild(option);
        }
    }
    
    /**
     * Display the first available chart
     */
    displayFirstChart(charts) {
        if (!charts || !charts.portfolio_charts) return;
        
        const firstPortfolio = Object.keys(charts.portfolio_charts)[0];
        if (firstPortfolio) {
            this.portfolioSelect.value = firstPortfolio;
            this.displayChart(firstPortfolio);
        }
    }
    
    /**
     * Display a specific chart
     */
    displayChart(portfolioName) {
        if (!this.chartDisplay || !this.currentCharts) return;
        
        try {
            let chartData;
            
            if (portfolioName === 'comparison' && this.currentCharts.comparison_chart) {
                chartData = JSON.parse(this.currentCharts.comparison_chart);
            } else if (this.currentCharts.portfolio_charts[portfolioName]) {
                chartData = JSON.parse(this.currentCharts.portfolio_charts[portfolioName]);
            } else {
                this.showChartError('Chart data not available');
                return;
            }
            
            // Configure chart for responsive display
            const config = {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                displaylogo: false,
                toImageButtonOptions: {
                    format: 'png',
                    filename: `retirement-projection-${portfolioName}`,
                    height: 500,
                    width: 800,
                    scale: 1
                }
            };
            
            // Render the chart
            Plotly.newPlot(this.chartDisplay, chartData.data, chartData.layout, config);
            
        } catch (error) {
            console.error('Error displaying chart:', error);
            this.showChartError('Error loading chart');
        }
    }
    
    /**
     * Show chart error message
     */
    showChartError(message) {
        if (this.chartDisplay) {
            this.chartDisplay.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 300px; color: #7f8c8d;">
                    <p>${message}</p>
                </div>
            `;
        }
    }
    
    /**
     * Show results section and hide form
     */
    showResults() {
        // Hide input section
        const inputSection = document.querySelector('.input-section');
        if (inputSection) {
            inputSection.style.display = 'none';
        }
        
        // Show results section
        if (this.resultsSection) {
            this.resultsSection.style.display = 'block';
            
            // Smooth scroll to results
            this.resultsSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }
    
    /**
     * Show input form and hide results
     */
    showInputForm() {
        // Show input section
        const inputSection = document.querySelector('.input-section');
        if (inputSection) {
            inputSection.style.display = 'block';
        }
        
        // Hide results section
        if (this.resultsSection) {
            this.resultsSection.style.display = 'none';
        }
        
        // Scroll to top of form
        if (this.form) {
            this.form.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
        
        // Update browser history
        history.pushState({ section: 'form' }, 'Calculator', '#calculator');
    }
    
    /**
     * Handle calculation errors
     */
    handleCalculationError(message, fieldErrors = null) {
        // Show general error message
        this.showGeneralError(message);
        
        // Show field-specific errors if provided
        if (fieldErrors && window.calculatorFormValidator) {
            Object.keys(fieldErrors).forEach(fieldName => {
                const errors = fieldErrors[fieldName];
                if (Array.isArray(errors) && errors.length > 0) {
                    window.calculatorFormValidator.showFieldError(fieldName, errors[0]);
                }
            });
        }
        
        // Scroll to form to show errors
        if (this.form) {
            this.form.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    }
    
    /**
     * Show general error message
     */
    showGeneralError(message) {
        // Create or update error container
        let errorContainer = document.querySelector('.calculation-error-message');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.className = 'calculation-error-message';
            errorContainer.style.cssText = `
                background: #f8d7da;
                color: #721c24;
                padding: 1rem;
                border: 1px solid #f5c6cb;
                border-radius: 8px;
                margin: 1rem 0;
                font-weight: 500;
            `;
            
            // Insert before form
            if (this.form && this.form.parentNode) {
                this.form.parentNode.insertBefore(errorContainer, this.form);
            }
        }
        
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (errorContainer) {
                errorContainer.style.display = 'none';
            }
        }, 10000);
    }
    
    /**
     * Clear all error messages
     */
    clearErrors() {
        // Clear general error
        const errorContainer = document.querySelector('.calculation-error-message');
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }
        
        // Clear form validation errors
        if (window.calculatorFormValidator) {
            window.calculatorFormValidator.clearGeneralError();
        }
    }
    
    /**
     * Display input summary section
     */
    displayInputSummary(userInput) {
        if (!userInput) return;
        
        const summaryAge = document.getElementById('summary-age');
        const summarySavings = document.getElementById('summary-savings');
        const summaryMonthly = document.getElementById('summary-monthly');
        const summaryIncome = document.getElementById('summary-income');
        
        if (summaryAge) {
            summaryAge.textContent = `${userInput.current_age} years`;
        }
        
        if (summarySavings) {
            summarySavings.textContent = `£${userInput.current_savings.toLocaleString('en-GB', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            })}`;
        }
        
        if (summaryMonthly) {
            summaryMonthly.textContent = `£${userInput.monthly_savings.toLocaleString('en-GB', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            })}`;
        }
        
        if (summaryIncome) {
            summaryIncome.textContent = `£${userInput.desired_annual_income.toLocaleString('en-GB', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            })}`;
        }
    }
    
    /**
     * Display calculation details section
     */
    displayCalculationDetails(result) {
        const calcTime = document.getElementById('calc-time');
        
        if (calcTime && result.calculation_time) {
            const timeInSeconds = Math.round(result.calculation_time * 10) / 10;
            calcTime.textContent = `${timeInSeconds} seconds`;
        }
        
        // Add additional calculation metadata if available
        if (result.metadata) {
            const metadata = result.metadata;
            
            // Update simulations count if different from default
            if (metadata.simulations_per_portfolio) {
                const simulationsElement = document.querySelector('.detail-value:contains("2,000")');
                if (simulationsElement) {
                    simulationsElement.textContent = metadata.simulations_per_portfolio.toLocaleString('en-GB');
                }
            }
            
            // Update data period if available
            if (metadata.data_period) {
                const dataPeriodElement = document.querySelector('.detail-value:contains("1900-2023")');
                if (dataPeriodElement) {
                    dataPeriodElement.textContent = metadata.data_period;
                }
            }
        }
    }
    
    /**
     * Handle additional action buttons
     */
    setupActionButtons() {
        // Save results button
        const saveResultsBtn = document.getElementById('save-results-btn');
        if (saveResultsBtn) {
            saveResultsBtn.addEventListener('click', () => {
                this.saveResults();
            });
        }
        
        // Print results button
        const printResultsBtn = document.getElementById('print-results-btn');
        if (printResultsBtn) {
            printResultsBtn.addEventListener('click', () => {
                this.printResults();
            });
        }
        
        // Fullscreen chart button
        const fullscreenChartBtn = document.getElementById('fullscreen-chart-btn');
        if (fullscreenChartBtn) {
            fullscreenChartBtn.addEventListener('click', () => {
                this.toggleFullscreenChart();
            });
        }
        
        // Download chart button
        const downloadChartBtn = document.getElementById('download-chart-btn');
        if (downloadChartBtn) {
            downloadChartBtn.addEventListener('click', () => {
                this.downloadChart();
            });
        }
    }
    
    /**
     * Save results as JSON file
     */
    saveResults() {
        if (!this.currentResults) {
            alert('No results to save');
            return;
        }
        
        try {
            const dataStr = JSON.stringify(this.currentResults, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `retirement-calculation-${new Date().toISOString().split('T')[0]}.json`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(link.href);
        } catch (error) {
            console.error('Error saving results:', error);
            alert('Error saving results. Please try again.');
        }
    }
    
    /**
     * Print results
     */
    printResults() {
        // Hide non-printable elements temporarily
        const nonPrintElements = document.querySelectorAll('.chart-controls, .results-actions, .form-actions');
        const originalDisplay = [];
        
        nonPrintElements.forEach((element, index) => {
            originalDisplay[index] = element.style.display;
            element.style.display = 'none';
        });
        
        // Print
        window.print();
        
        // Restore elements
        nonPrintElements.forEach((element, index) => {
            element.style.display = originalDisplay[index];
        });
    }
    
    /**
     * Toggle fullscreen chart display
     */
    toggleFullscreenChart() {
        const chartContainer = document.getElementById('chart-container');
        if (!chartContainer) return;
        
        if (chartContainer.classList.contains('fullscreen')) {
            // Exit fullscreen
            chartContainer.classList.remove('fullscreen');
            document.body.style.overflow = '';
            
            // Update button text
            const btn = document.getElementById('fullscreen-chart-btn');
            if (btn) {
                btn.innerHTML = '<span class="btn-icon">⛶</span>Fullscreen';
            }
        } else {
            // Enter fullscreen
            chartContainer.classList.add('fullscreen');
            document.body.style.overflow = 'hidden';
            
            // Update button text
            const btn = document.getElementById('fullscreen-chart-btn');
            if (btn) {
                btn.innerHTML = '<span class="btn-icon">✕</span>Exit Fullscreen';
            }
            
            // Re-render chart for fullscreen
            if (this.portfolioSelect && this.portfolioSelect.value) {
                setTimeout(() => {
                    this.displayChart(this.portfolioSelect.value);
                }, 100);
            }
        }
    }
    
    /**
     * Download current chart as image
     */
    downloadChart() {
        const chartDisplay = document.getElementById('chart-display');
        if (!chartDisplay || !this.portfolioSelect) return;
        
        const portfolioName = this.portfolioSelect.value || 'chart';
        const filename = `retirement-chart-${portfolioName}-${new Date().toISOString().split('T')[0]}.png`;
        
        // Use Plotly's built-in download functionality
        if (window.Plotly && chartDisplay.data) {
            Plotly.downloadImage(chartDisplay, {
                format: 'png',
                filename: filename,
                height: 600,
                width: 1000,
                scale: 2
            }).catch(error => {
                console.error('Error downloading chart:', error);
                alert('Error downloading chart. Please try again.');
            });
        } else {
            alert('Chart not ready for download. Please wait for the chart to load.');
        }
    }
    
    /**
     * Handle allocation breakdown display in table
     */
    createAllocationBreakdown(allocation) {
        const breakdown = document.createElement('div');
        breakdown.className = 'allocation-breakdown';
        
        // Create items array with proper property names
        const items = [];
        
        if (allocation.equity_percentage && allocation.equity_percentage > 0) {
            items.push({ 
                label: 'Equity', 
                value: allocation.equity_percentage,
                color: '#3498db'
            });
        }
        
        if (allocation.bond_percentage && allocation.bond_percentage > 0) {
            items.push({ 
                label: 'Bonds', 
                value: allocation.bond_percentage,
                color: '#e74c3c'
            });
        }
        
        if (allocation.cash_percentage && allocation.cash_percentage > 0) {
            items.push({ 
                label: 'Cash', 
                value: allocation.cash_percentage,
                color: '#95a5a6'
            });
        }
        
        // Create visual bars for each allocation
        items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'allocation-item';
            
            const barContainer = document.createElement('div');
            barContainer.className = 'allocation-bar-container';
            
            const bar = document.createElement('div');
            bar.className = 'allocation-bar';
            bar.style.width = `${item.value}%`;
            bar.style.backgroundColor = item.color;
            
            const label = document.createElement('span');
            label.className = 'allocation-label';
            label.textContent = `${item.label}: ${item.value}%`;
            
            barContainer.appendChild(bar);
            itemDiv.appendChild(label);
            itemDiv.appendChild(barContainer);
            breakdown.appendChild(itemDiv);
        });
        
        return breakdown;
    }
    
    /**
     * Format currency values consistently
     */
    formatCurrency(value, options = {}) {
        const defaultOptions = {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
            ...options
        };
        
        return `£${value.toLocaleString('en-GB', defaultOptions)}`;
    }
    
    /**
     * Format percentage values consistently
     */
    formatPercentage(value, decimals = 0) {
        return `${(value * 100).toFixed(decimals)}%`;
    }
    
    /**
     * Show loading state for charts
     */
    showChartLoading() {
        const chartLoading = document.getElementById('chart-loading');
        const chartDisplay = document.getElementById('chart-display');
        const chartError = document.getElementById('chart-error');
        
        if (chartLoading) chartLoading.style.display = 'flex';
        if (chartDisplay) chartDisplay.style.display = 'none';
        if (chartError) chartError.style.display = 'none';
    }
    
    /**
     * Hide loading state for charts
     */
    hideChartLoading() {
        const chartLoading = document.getElementById('chart-loading');
        const chartDisplay = document.getElementById('chart-display');
        
        if (chartLoading) chartLoading.style.display = 'none';
        if (chartDisplay) chartDisplay.style.display = 'block';
    }
    
    /**
     * Get current calculation results
     */
    getCurrentResults() {
        return this.currentResults;
    }
    
    /**
     * Check if results are currently displayed
     */
    isShowingResults() {
        return this.resultsSection && this.resultsSection.style.display !== 'none';
    }
    
    /**
     * Setup scenario comparison functionality
     */
    setupScenarioComparison() {
        // Save scenario button
        const saveScenarioBtn = document.getElementById('save-scenario-btn');
        if (saveScenarioBtn) {
            saveScenarioBtn.addEventListener('click', () => {
                this.saveCurrentScenario();
            });
        }
        
        // Load scenario button
        const loadScenarioBtn = document.getElementById('load-scenario-btn');
        if (loadScenarioBtn) {
            loadScenarioBtn.addEventListener('click', () => {
                this.toggleScenarioList();
            });
        }
        
        // Compare scenarios button
        const compareBtn = document.getElementById('compare-scenarios-btn');
        if (compareBtn) {
            compareBtn.addEventListener('click', () => {
                this.showScenarioComparison();
            });
        }
        
        // Close comparison button
        const closeComparisonBtn = document.getElementById('close-comparison-btn');
        if (closeComparisonBtn) {
            closeComparisonBtn.addEventListener('click', () => {
                this.closeScenarioComparison();
            });
        }
        
        // Initialize scenario list
        this.updateScenarioList();
    }
    
    /**
     * Save current scenario to localStorage
     */
    saveCurrentScenario() {
        if (!this.currentResults) {
            alert('No results to save');
            return;
        }
        
        const scenarioName = prompt('Enter a name for this scenario:');
        if (!scenarioName) return;
        
        const scenario = {
            id: Date.now().toString(),
            name: scenarioName,
            timestamp: new Date().toISOString(),
            userInput: this.currentResults.user_input,
            results: this.currentResults.results,
            recommendedPortfolio: this.currentResults.recommended_portfolio,
            recommendedAge: this.currentResults.recommended_age
        };
        
        this.savedScenarios.push(scenario);
        this.saveScenariosToStorage();
        this.updateScenarioList();
        
        // Show confirmation
        const message = document.createElement('div');
        message.className = 'scenario-saved-message';
        message.textContent = `Scenario "${scenarioName}" saved successfully!`;
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 1rem;
            border-radius: 4px;
            z-index: 10000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        `;
        
        document.body.appendChild(message);
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 3000);
    }
    
    /**
     * Load saved scenarios from localStorage
     */
    loadSavedScenarios() {
        try {
            const saved = localStorage.getItem('retirementCalculatorScenarios');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading saved scenarios:', error);
            return [];
        }
    }
    
    /**
     * Save scenarios to localStorage
     */
    saveScenariosToStorage() {
        try {
            localStorage.setItem('retirementCalculatorScenarios', JSON.stringify(this.savedScenarios));
        } catch (error) {
            console.error('Error saving scenarios:', error);
            alert('Error saving scenario. Storage may be full.');
        }
    }
    
    /**
     * Update the scenario list display
     */
    updateScenarioList() {
        const scenarioList = document.getElementById('scenario-list');
        if (!scenarioList) return;
        
        scenarioList.innerHTML = '';
        
        if (this.savedScenarios.length === 0) {
            const emptyMessage = document.createElement('p');
            emptyMessage.textContent = 'No saved scenarios yet.';
            emptyMessage.style.color = '#7f8c8d';
            emptyMessage.style.fontStyle = 'italic';
            scenarioList.appendChild(emptyMessage);
            return;
        }
        
        this.savedScenarios.forEach(scenario => {
            const scenarioItem = document.createElement('div');
            scenarioItem.className = 'scenario-item';
            
            const scenarioInfo = document.createElement('div');
            scenarioInfo.className = 'scenario-info';
            
            const scenarioName = document.createElement('h5');
            scenarioName.textContent = scenario.name;
            scenarioName.style.margin = '0 0 0.25rem 0';
            
            const scenarioDetails = document.createElement('p');
            scenarioDetails.style.margin = '0';
            scenarioDetails.style.fontSize = '0.875rem';
            scenarioDetails.style.color = '#5a6c7d';
            scenarioDetails.textContent = `Age ${scenario.userInput.current_age}, £${scenario.userInput.current_savings.toLocaleString('en-GB')} savings`;
            
            const scenarioDate = document.createElement('p');
            scenarioDate.style.margin = '0';
            scenarioDate.style.fontSize = '0.75rem';
            scenarioDate.style.color = '#95a5a6';
            scenarioDate.textContent = new Date(scenario.timestamp).toLocaleDateString();
            
            scenarioInfo.appendChild(scenarioName);
            scenarioInfo.appendChild(scenarioDetails);
            scenarioInfo.appendChild(scenarioDate);
            
            const scenarioActions = document.createElement('div');
            scenarioActions.className = 'scenario-actions';
            
            const loadBtn = document.createElement('button');
            loadBtn.className = 'btn btn-sm btn-primary';
            loadBtn.textContent = 'Load';
            loadBtn.addEventListener('click', () => {
                this.loadScenario(scenario);
            });
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm btn-danger';
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => {
                this.deleteScenario(scenario.id);
            });
            
            scenarioActions.appendChild(loadBtn);
            scenarioActions.appendChild(deleteBtn);
            
            scenarioItem.appendChild(scenarioInfo);
            scenarioItem.appendChild(scenarioActions);
            
            scenarioList.appendChild(scenarioItem);
        });
    }
    
    /**
     * Toggle scenario list visibility
     */
    toggleScenarioList() {
        const savedScenarios = document.getElementById('saved-scenarios');
        if (savedScenarios) {
            const isVisible = savedScenarios.style.display !== 'none';
            savedScenarios.style.display = isVisible ? 'none' : 'block';
        }
    }
    
    /**
     * Load a specific scenario
     */
    loadScenario(scenario) {
        // Create a mock result structure
        const mockResult = {
            success: true,
            user_input: scenario.userInput,
            results: scenario.results,
            recommended_portfolio: scenario.recommendedPortfolio,
            recommended_age: scenario.recommendedAge,
            charts: null, // Charts would need to be regenerated
            calculation_id: 'loaded-scenario-' + scenario.id,
            calculation_time: 0
        };
        
        // Update current results
        this.currentResults = mockResult;
        this.currentCharts = null;
        
        // Display the loaded scenario
        this.displayResults(mockResult);
        
        // Hide scenario list
        this.toggleScenarioList();
        
        // Show message
        const message = document.createElement('div');
        message.className = 'scenario-loaded-message';
        message.textContent = `Scenario "${scenario.name}" loaded successfully!`;
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #3498db;
            color: white;
            padding: 1rem;
            border-radius: 4px;
            z-index: 10000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        `;
        
        document.body.appendChild(message);
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 3000);
    }
    
    /**
     * Delete a saved scenario
     */
    deleteScenario(scenarioId) {
        if (confirm('Are you sure you want to delete this scenario?')) {
            this.savedScenarios = this.savedScenarios.filter(s => s.id !== scenarioId);
            this.saveScenariosToStorage();
            this.updateScenarioList();
        }
    }
    
    /**
     * Show scenario comparison chart
     */
    showScenarioComparison() {
        if (this.savedScenarios.length === 0) {
            alert('No saved scenarios to compare. Save some scenarios first.');
            return;
        }
        
        const comparisonContainer = document.getElementById('comparison-chart-container');
        if (!comparisonContainer) return;
        
        comparisonContainer.style.display = 'block';
        
        // Create comparison chart data
        this.generateComparisonChart();
        
        // Scroll to comparison chart
        comparisonContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    /**
     * Close scenario comparison
     */
    closeScenarioComparison() {
        const comparisonContainer = document.getElementById('comparison-chart-container');
        if (comparisonContainer) {
            comparisonContainer.style.display = 'none';
        }
    }
    
    /**
     * Generate comparison chart for saved scenarios
     */
    generateComparisonChart() {
        const comparisonChart = document.getElementById('comparison-chart');
        if (!comparisonChart) return;
        
        // Prepare data for comparison
        const scenarios = this.savedScenarios;
        const scenarioNames = scenarios.map(s => s.name);
        const currentAge = scenarios.map(s => s.userInput.current_age);
        const currentSavings = scenarios.map(s => s.userInput.current_savings);
        const monthlyContributions = scenarios.map(s => s.userInput.monthly_savings);
        const desiredIncome = scenarios.map(s => s.userInput.desired_annual_income);
        const recommendedAges = scenarios.map(s => s.recommendedAge || 'N/A');
        
        // Create traces for different metrics
        const traces = [
            {
                x: scenarioNames,
                y: currentAge,
                name: 'Current Age',
                type: 'bar',
                marker: { color: '#3498db' }
            },
            {
                x: scenarioNames,
                y: currentSavings,
                name: 'Current Savings (£)',
                type: 'bar',
                yaxis: 'y2',
                marker: { color: '#e74c3c' }
            },
            {
                x: scenarioNames,
                y: monthlyContributions,
                name: 'Monthly Savings (£)',
                type: 'bar',
                yaxis: 'y3',
                marker: { color: '#2ecc71' }
            },
            {
                x: scenarioNames,
                y: desiredIncome,
                name: 'Desired Income (£)',
                type: 'bar',
                yaxis: 'y4',
                marker: { color: '#f39c12' }
            }
        ];
        
        // Layout with multiple y-axes
        const layout = {
            title: 'Scenario Comparison',
            xaxis: { title: 'Scenarios' },
            yaxis: { 
                title: 'Age',
                side: 'left',
                range: [0, 100]
            },
            yaxis2: {
                title: 'Savings (£)',
                side: 'right',
                overlaying: 'y',
                position: 0.85
            },
            yaxis3: {
                title: 'Monthly (£)',
                side: 'right',
                overlaying: 'y',
                position: 0.95
            },
            yaxis4: {
                title: 'Income (£)',
                side: 'right',
                overlaying: 'y',
                position: 1.05
            },
            showlegend: true,
            height: 500,
            margin: { r: 100 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };
        
        Plotly.newPlot(comparisonChart, traces, layout, config);
    }
    
    /**
     * Setup quick edit modal functionality
     */
    setupQuickEditModal() {
        const quickEditModal = document.getElementById('quick-edit-modal');
        const modalOverlay = document.getElementById('modal-overlay');
        const closeButton = document.getElementById('close-quick-edit');
        const cancelButton = document.getElementById('cancel-quick-edit');
        const quickEditForm = document.getElementById('quick-edit-form');
        
        // Close modal handlers
        const closeModal = () => {
            if (quickEditModal) {
                quickEditModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        };
        
        if (modalOverlay) {
            modalOverlay.addEventListener('click', closeModal);
        }
        
        if (closeButton) {
            closeButton.addEventListener('click', closeModal);
        }
        
        if (cancelButton) {
            cancelButton.addEventListener('click', closeModal);
        }
        
        // Form submission handler
        if (quickEditForm) {
            quickEditForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleQuickEditSubmission();
            });
        }
        
        // ESC key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && quickEditModal && quickEditModal.style.display !== 'none') {
                closeModal();
            }
        });
    }
    
    /**
     * Show quick edit modal
     */
    showQuickEditModal() {
        const quickEditModal = document.getElementById('quick-edit-modal');
        if (!quickEditModal || !this.currentResults) return;
        
        // Populate form with current values
        const userInput = this.currentResults.user_input;
        if (userInput) {
            document.getElementById('quick-current-age').value = userInput.current_age || '';
            document.getElementById('quick-current-savings').value = userInput.current_savings || '';
            document.getElementById('quick-monthly-savings').value = userInput.monthly_savings || '';
            document.getElementById('quick-desired-income').value = userInput.desired_annual_income || '';
        }
        
        // Show modal
        quickEditModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        const firstInput = document.getElementById('quick-current-age');
        if (firstInput) {
            firstInput.focus();
        }
    }
    
    /**
     * Handle quick edit form submission
     */
    async handleQuickEditSubmission() {
        const submitButton = document.getElementById('quick-edit-submit');
        const btnText = submitButton?.querySelector('.btn-text');
        const btnLoading = submitButton?.querySelector('.btn-loading');
        
        // Set loading state
        if (submitButton) {
            submitButton.disabled = true;
            if (btnText) btnText.style.display = 'none';
            if (btnLoading) btnLoading.style.display = 'flex';
        }
        
        try {
            // Get form data
            const formData = {
                current_age: parseInt(document.getElementById('quick-current-age').value),
                current_savings: parseFloat(document.getElementById('quick-current-savings').value),
                monthly_savings: parseFloat(document.getElementById('quick-monthly-savings').value),
                desired_annual_income: parseFloat(document.getElementById('quick-desired-income').value)
            };
            
            // Validate data
            if (!this.validateQuickEditData(formData)) {
                return;
            }
            
            // Submit calculation request
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update current results
                this.currentResults = result;
                this.currentCharts = result.charts;
                this.calculationId = result.calculation_id;
                
                // Display updated results
                this.displayResults(result);
                
                // Close modal
                document.getElementById('quick-edit-modal').style.display = 'none';
                document.body.style.overflow = '';
                
                // Show success message
                this.showQuickEditSuccess();
                
            } else {
                this.handleCalculationError(result.error || 'Calculation failed', result.errors);
            }
            
        } catch (error) {
            console.error('Quick edit calculation error:', error);
            this.handleCalculationError('Network error occurred. Please try again.');
        } finally {
            // Reset loading state
            if (submitButton) {
                submitButton.disabled = false;
                if (btnText) btnText.style.display = 'inline';
                if (btnLoading) btnLoading.style.display = 'none';
            }
        }
    }
    
    /**
     * Validate quick edit form data
     */
    validateQuickEditData(data) {
        const errors = [];
        
        if (!data.current_age || data.current_age < 18 || data.current_age > 100) {
            errors.push('Current age must be between 18 and 100');
        }
        
        if (!data.current_savings || data.current_savings < 0) {
            errors.push('Current savings must be 0 or greater');
        }
        
        if (!data.monthly_savings || data.monthly_savings < 0) {
            errors.push('Monthly savings must be 0 or greater');
        }
        
        if (!data.desired_annual_income || data.desired_annual_income <= 0) {
            errors.push('Desired annual income must be greater than 0');
        }
        
        if (errors.length > 0) {
            alert('Please fix the following errors:\n\n' + errors.join('\n'));
            return false;
        }
        
        return true;
    }
    
    /**
     * Show success message for quick edit
     */
    showQuickEditSuccess() {
        const message = document.createElement('div');
        message.className = 'quick-edit-success-message';
        message.textContent = 'Inputs updated and recalculated successfully!';
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 1rem;
            border-radius: 4px;
            z-index: 10000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-weight: 500;
        `;
        
        document.body.appendChild(message);
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 4000);
    }
}

// Initialize results handler when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.resultsHandler = new ResultsHandler();
});

// Initialize calculator form function for backward compatibility
function initializeCalculatorForm() {
    // This function is called from the template
    // The actual initialization happens in DOMContentLoaded event above
    console.log('Calculator form initialized');
}