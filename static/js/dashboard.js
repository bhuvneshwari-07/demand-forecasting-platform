/* ==========================================================================
   AI Demand Forecasting & Inventory Intelligence Platform - Dashboard Logic JS
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------
    // 1. Drag & Drop CSV Uploader
    // ----------------------------------------------
    const uploadZone = document.getElementById('upload-zone');
    const csvFileInput = document.getElementById('csv-file-input');
    const uploadProgressContainer = document.getElementById('upload-progress-container');
    const uploadProgressBar = document.getElementById('upload-progress-bar');
    const uploadStatusText = document.getElementById('upload-status-text');
    if (uploadZone && csvFileInput) {
        uploadZone.addEventListener('click', () => csvFileInput.click());
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            }, false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
            }, false);
        });
        uploadZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                csvFileInput.files = files;
                handleCSVUpload(files[0]);
            }
        });
        csvFileInput.addEventListener('change', (e) => {
            if (csvFileInput.files.length > 0) {
                handleCSVUpload(csvFileInput.files[0]);
            }
        });
    }
    function handleCSVUpload(file) {
        // Validation
        if (!file.name.endsWith('.csv')) {
            alert('Invalid file format. Please upload a valid CSV file.');
            return;
        }
        // Show progress UI
        uploadProgressContainer.classList.remove('d-none');
        uploadStatusText.textContent = `Uploading ${file.name}...`;
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            uploadProgressBar.style.width = `${progress}%`;
            uploadProgressBar.setAttribute('aria-valuenow', progress);
            
            if (progress >= 100) {
                clearInterval(interval);
                uploadStatusText.textContent = "Processing and running AI predictions...";
                // Submit form
                document.getElementById('csv-upload-form').submit();
            }
        }, 150);
    }
    // ----------------------------------------------
    // 2. Multi-Step Manual Forecasting Wizard
    // ----------------------------------------------
    const wizardForm = document.getElementById('manual-forecast-wizard');
    if (wizardForm) {
        let currentStep = 1;
        const totalSteps = 4;
        const showStep = (step) => {
            document.querySelectorAll('.wizard-step-content').forEach(el => el.classList.add('d-none'));
            document.getElementById(`step-content-${step}`).classList.remove('d-none');
            // Update Nodes
            document.querySelectorAll('.wizard-step-node').forEach((node, idx) => {
                const nodeStep = idx + 1;
                node.classList.remove('active', 'completed');
                if (nodeStep === step) {
                    node.classList.add('active');
                } else if (nodeStep < step) {
                    node.classList.add('completed');
                }
            });
            // Update buttons
            const prevBtn = document.getElementById('btn-prev');
            const nextBtn = document.getElementById('btn-next');
            const submitBtn = document.getElementById('btn-submit');
            if (prevBtn) prevBtn.classList.toggle('d-none', step === 1);
            if (nextBtn) nextBtn.classList.toggle('d-none', step === totalSteps);
            if (submitBtn) submitBtn.classList.toggle('d-none', step !== totalSteps);
        };
        const validateStep = (step) => {
            const container = document.getElementById(`step-content-${step}`);
            const inputs = container.querySelectorAll('[required]');
            let isValid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });
            return isValid;
        };
        const nextBtn = document.getElementById('btn-next');
        const prevBtn = document.getElementById('btn-prev');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (validateStep(currentStep)) {
                    currentStep++;
                    showStep(currentStep);
                } else {
                    alert("Please fill in all required fields before proceeding.");
                }
            });
        }
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                currentStep--;
                showStep(currentStep);
            });
        }
        // Init Wizard View
        showStep(1);
    }
    let simTimeout;
    const sliders = document.querySelectorAll('.cyber-range');
    if (sliders.length > 0) {
        sliders.forEach(slider => {
            slider.addEventListener('input', (e) => {
                const valSpan = document.getElementById(`${e.target.id}-val`);
                if (valSpan) {
                    // format percentages or currencies
                    if (e.target.id === 'sim-discount') {
                        valSpan.textContent = `${e.target.value}%`;
                    } else if (e.target.id === 'sim-price' || e.target.id === 'sim-mkt') {
                        valSpan.textContent = `$${parseFloat(e.target.value).toLocaleString()}`;
                    } else {
                        valSpan.textContent = e.target.value;
                    }
                }
                
                // Debounce real-time API query to prevent network spam
                clearTimeout(simTimeout);
                simTimeout = setTimeout(runSimulation, 100);
            });
        });
    }
    // Bind dropdowns & checkboxes to trigger real-time recalculations
    const simTriggers = ['sim-model-select', 'sim-promo', 'sim-weather', 'sim-season', 'sim-festival', 'sim-economy'];
    simTriggers.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', runSimulation);
        }
    });
    function runSimulation() {
        const payload = {
            product_id: document.getElementById('sim-product-select')?.value || 'PRD-1024',
            selling_price: document.getElementById('sim-price')?.value || 100.0,
            discount_percentage: document.getElementById('sim-discount')?.value || 0.0,
            promotion_active: document.getElementById('sim-promo')?.checked ? 1 : 0,
            marketing_spend: document.getElementById('sim-mkt')?.value || 0.0,
            previous_month_sales: document.getElementById('sim-prev-sales')?.value || 150.0,
            current_inventory_level: document.getElementById('sim-inventory')?.value || 200.0,
            units_ordered: document.getElementById('sim-ordered')?.value || 0.0,
            safety_stock: document.getElementById('sim-safety')?.value || 30.0,
            lead_time: document.getElementById('sim-lead-time')?.value || 7.0,
            supplier_reliability: document.getElementById('sim-reliability')?.value || 0.95,
            weather_condition: document.getElementById('sim-weather')?.value || 'Sunny',
            season: document.getElementById('sim-season')?.value || 'Summer',
            festival_holiday: document.getElementById('sim-festival')?.checked ? 1 : 0,
            inflation_rate: document.getElementById('sim-inflation')?.value || 3.0,
            fuel_price_index: document.getElementById('sim-fuel')?.value || 3.5,
            economic_condition: document.getElementById('sim-economy')?.value || 'Average',
            model_used: document.getElementById('sim-model-select')?.value || 'LightGBM'
        };
        const resultDemandVal = document.getElementById('sim-result-demand');
        const resultRevVal = document.getElementById('sim-result-revenue');
        const resultRiskVal = document.getElementById('sim-result-risk');
        const resultReorderVal = document.getElementById('sim-result-reorder');
        if (resultDemandVal) {
            resultDemandVal.textContent = "...";
            resultRevVal.textContent = "...";
            resultRiskVal.textContent = "...";
            resultReorderVal.textContent = "...";
        }
        fetch('/ai-insights/simulate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Update UI elements with slide effects or direct values
                animateValue('sim-result-demand', 0, data.forecasted_demand, 300);
                animateValue('sim-result-revenue', 0, data.revenue_forecast, 300, '$');
                
                resultRiskVal.textContent = data.stockout_risk;
                resultRiskVal.className = 'kpi-value text-' + (data.stockout_risk === 'High' ? 'danger' : (data.stockout_risk === 'Medium' ? 'warning' : 'success'));
                
                animateValue('sim-result-reorder', 0, data.suggested_reorder_quantity, 300);
            }
        })
        .catch(err => console.error("Scenario simulation error:", err));
    }
    function animateValue(id, start, end, duration, prefix = '') {
        const obj = document.getElementById(id);
        if (!obj) return;
        
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const val = progress * (end - start) + start;
            
            if (prefix === '$') {
                obj.textContent = prefix + parseFloat(val).toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2});
            } else {
                obj.textContent = Math.floor(val).toLocaleString();
            }
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                if (prefix === '$') {
                    obj.textContent = prefix + parseFloat(end).toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2});
                } else {
                    obj.textContent = Math.floor(end).toLocaleString();
                }
            }
        };
        window.requestAnimationFrame(step);
    }
    // Trigger initial simulation values if simulator components exist
    const simProductSelect = document.getElementById('sim-product-select');
    if (simProductSelect) {
        // Automatically sync inputs when changing product selection
        simProductSelect.addEventListener('change', () => {
            const selectedOption = simProductSelect.options[simProductSelect.selectedIndex];
            if (selectedOption) {
                const stock = selectedOption.dataset.stock;
                const ordered = selectedOption.dataset.ordered;
                const safety = selectedOption.dataset.safety;
                const leadtime = selectedOption.dataset.leadtime;
                const rel = selectedOption.dataset.reliability;
                
                if (document.getElementById('sim-inventory')) document.getElementById('sim-inventory').value = stock;
                if (document.getElementById('sim-inventory-val')) document.getElementById('sim-inventory-val').textContent = stock;
                
                if (document.getElementById('sim-ordered')) document.getElementById('sim-ordered').value = ordered;
                if (document.getElementById('sim-ordered-val')) document.getElementById('sim-ordered-val').textContent = ordered;
                
                if (document.getElementById('sim-safety')) document.getElementById('sim-safety').value = safety;
                if (document.getElementById('sim-safety-val')) document.getElementById('sim-safety-val').textContent = safety;
                
                if (document.getElementById('sim-lead-time')) document.getElementById('sim-lead-time').value = leadtime;
                if (document.getElementById('sim-lead-time-val')) document.getElementById('sim-lead-time-val').textContent = leadtime;
                
                if (document.getElementById('sim-reliability')) document.getElementById('sim-reliability').value = rel;
                if (document.getElementById('sim-reliability-val')) document.getElementById('sim-reliability-val').textContent = rel;
                runSimulation();
            }
        });
        runSimulation();
    }
    // ----------------------------------------------
    // 4. AI Chatbot Assistant Client
    // ----------------------------------------------
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatMessages = document.getElementById('chat-messages');
    if (chatInput && sendChatBtn && chatMessages) {
        const addMessage = (sender, text) => {
            const bubble = document.createElement('div');
            bubble.className = `chat-bubble ${sender}`;
            bubble.textContent = text;
            chatMessages.appendChild(bubble);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };
        const sendMessage = () => {
            const query = chatInput.value.trim();
            if (!query) return;
            addMessage('user', query);
            chatInput.value = '';
            // Add typing placeholder
            const typingBubble = document.createElement('div');
            typingBubble.className = 'chat-bubble bot typing-indicator';
            typingBubble.textContent = "AI is typing...";
            chatMessages.appendChild(typingBubble);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            fetch('/ai-insights/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ query: query })
            })
            .then(res => res.json())
            .then(data => {
                // Remove typing indicator
                typingBubble.remove();
                addMessage('bot', data.response);
            })
            .catch(err => {
                typingBubble.remove();
                addMessage('bot', "Apologies, I encountered a communication error with the core AI forecasting service.");
                console.error(err);
            });
        };
        sendChatBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});
