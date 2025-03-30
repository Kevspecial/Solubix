// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    // Initialize application state
    let systemSolvents = new Set();
    let solutes = {};
    let solvents = {};

    // DOM Elements
    const elements = {
        soluteSelect: document.getElementById("solute-select"),
        solventSelect: document.getElementById("solvents"),
        soluteD: document.getElementById("solute-d"),
        soluteP: document.getElementById("solute-p"),
        soluteH: document.getElementById("solute-h"),
        soluteRo: document.getElementById("solute-ro"),
        solventSearch: document.getElementById("solvent-search"),
        searchResults: document.getElementById("search-results"),
        calculateBtn: document.getElementById("calculate"),
        resultsTable: document.getElementById("results"),
        message: document.getElementById("message"),
        loading: document.getElementById("loading"),
        plotContainer: document.getElementById("plot-container")
    };

    // Initialize event listeners
    function initEventListeners() {
        elements.soluteSelect.addEventListener('change', handleSoluteSelect);
        elements.solventSearch.addEventListener('input', handleSolventSearch);
        elements.calculateBtn.addEventListener('click', calculateSolubility);
        document.addEventListener('click', handleDocumentClick);
    }

    // Initialize data
    async function initData() {
        try {
            const [solutesRes, solventsRes] = await Promise.all([
                fetch('/api/SOLUTES').then(res => res.json()),
                fetch('/api/SOLVENTS').then(res => res.json())
            ]);

            solutes = solutesRes;
            solvents = solventsRes;
            systemSolvents = new Set(Object.keys(solvents));

            populateSelects();
        } catch (error) {
            console.error('Error initializing data:', error);
            showMessage('Failed to load application data');
        }
    }

    // Populate select elements
    function populateSelects() {
        // Populate solute select
        Object.entries(solutes).forEach(([name, values]) => {
            const option = new Option(name, name);
            option.dataset.d = values.d;
            option.dataset.p = values.p;
            option.dataset.h = values.h;
            option.dataset.ro = values.ro;
            elements.soluteSelect.add(option);
        });

        // Populate solvent select
        Object.keys(solvents).forEach(name => {
            const option = new Option(name, name);
            elements.solventSelect.add(option);
        });
    }

    // Event handlers
    function handleSoluteSelect() {
        const selectedOption = this.options[this.selectedIndex];
        if (!selectedOption.value) {
            elements.soluteD.value = '';
            elements.soluteP.value = '';
            elements.soluteH.value = '';
            elements.soluteRo.value = '';
            return;
        }

        elements.soluteD.value = selectedOption.dataset.d;
        elements.soluteP.value = selectedOption.dataset.p;
        elements.soluteH.value = selectedOption.dataset.h;
        elements.soluteRo.value = selectedOption.dataset.ro;
    }

    async function handleSolventSearch(e) {
        const query = e.target.value.trim();
        elements.searchResults.innerHTML = '';
        
        if (query.length < 1) {
            elements.searchResults.classList.remove('active');
            return;
        }

        try {
            const response = await fetch(`/api/search_solvents?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.length === 0) {
                elements.searchResults.innerHTML = '<div>No solvents found</div>';
                elements.searchResults.classList.add('active');
                return;
            }

            data.forEach(solvent => {
                const div = document.createElement('div');
                div.textContent = solvent.name;
                div.onclick = () => addSolvent(solvent.name);
                elements.searchResults.appendChild(div);
            });
            
            elements.searchResults.classList.add('active');
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    function handleDocumentClick(e) {
        if (e.target !== elements.solventSearch && !elements.searchResults.contains(e.target)) {
            elements.searchResults.classList.remove('active');
        }
    }

    // Core functionality
    async function calculateSolubility() {
        const params = {
            solute_d: elements.soluteD.value,
            solute_p: elements.soluteP.value,
            solute_h: elements.soluteH.value,
            solute_ro: elements.soluteRo.value,
            solvents: Array.from(elements.solventSelect.selectedOptions).map(opt => opt.value)
        };

        if (!validateInputs(params)) return;

        showLoading();

        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });

            if (!response.ok) throw new Error('Calculation failed');
            
            const data = await response.json();
            handleCalculationResponse(data);
        } catch (error) {
            handleCalculationError(error);
        } finally {
            hideLoading();
        }
    }

    // Helper functions
    function validateInputs(params) {
        if (!params.solute_d || !params.solute_p || !params.solute_h || !params.solute_ro) {
            showMessage('Please enter all solute HSP parameters and Ro.');
            return false;
        }
        if (params.solvents.length === 0) {
            showMessage('Please select at least one solvent.');
            return false;
        }
        return true;
    }

    function handleCalculationResponse(data) {
        if (data.error) {
            showMessage(data.error);
            return;
        }

        if (data.plot_json) {
            try {
                const plotData = JSON.parse(data.plot_json);
                Plotly.newPlot(elements.plotContainer, plotData.data, plotData.layout);
            } catch (error) {
                console.error('Plot error:', error);
            }
        }

        updateResultsTable(data.results);
        updateLastUpdated();
    }

    function handleCalculationError(error) {
        console.error('Calculation error:', error);
        showMessage('Failed to calculate. Please try again.');
    }

    function updateResultsTable(results) {
        elements.resultsTable.innerHTML = Object.entries(results).map(([solvent, res]) => `
            <tr>
                <td>${solvent}</td>
                <td>${res.d}</td>
                <td>${res.p}</td>
                <td>${res.h}</td>
                <td>${res.ra}</td>
                <td>${res.red}</td>
                <td><span class="solubility ${res.solubility.toLowerCase()}">${res.solubility}</span></td>
            </tr>
        `).join('');
    }

    function addSolvent(name) {
        if (!systemSolvents.has(name)) return;

        const options = Array.from(elements.solventSelect.options);
        const existing = options.find(opt => opt.value === name);
        
        if (existing) {
            existing.selected = true;
            elements.solventSearch.value = '';
            elements.searchResults.innerHTML = '';
            elements.searchResults.classList.remove('active');
        }
    }

    function showLoading() {
        elements.resultsTable.innerHTML = '';
        elements.message.style.display = 'none';
        elements.loading.style.display = 'block';
        elements.plotContainer.innerHTML = '';
    }

    function hideLoading() {
        elements.loading.style.display = 'none';
    }

    function showMessage(text) {
        elements.message.textContent = text;
        elements.message.style.display = 'block';
    }

    function updateLastUpdated() {
        const now = new Date();
        document.getElementById('last-updated').textContent = 
            `Last updated: ${now.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit', 
                hour12: false 
            })}`;
    }

    // Start the application
    initEventListeners();
    initData();
});