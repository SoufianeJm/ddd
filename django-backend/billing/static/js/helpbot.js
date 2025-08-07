// HelpBot JavaScript functionality with localStorage persistence
function toggleHelpBot() {
    const helpWindow = document.getElementById('helpWindow');
    const helpNotification = document.getElementById('helpNotification');
    
    helpWindow.classList.toggle('open');
    
    // Hide notification when opened
    if (helpWindow.classList.contains('open')) {
        helpNotification.style.display = 'none';
        loadHelpHistory();
    } else {
        saveHelpHistory();
    }
}

function clearHelpHistory() {
    const helpMessages = document.getElementById('helpMessages');
    
    // Clear localStorage
    localStorage.removeItem('helpbot_messages');
    
    // Reset to initial welcome message with 7 buttons
    helpMessages.innerHTML = `
        <div class="help-message bot-message">
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p>Comment puis-je t'aider ?</p>
                <div class="help-quick-buttons">
                    <button class="help-quick-btn" onclick="window.open('/facturation/slr/','_blank')">💾 Importer</button>
                    <button class="help-quick-btn" onclick="addQuickMessage('💰 Calculer')">💰 Calculer</button>
                    <button class="help-quick-btn" onclick="addQuickMessage('📊 Résultats')">📊 Résultats</button>
                    <button class="help-quick-btn" onclick="window.open('/resources/create/', '_blank')">➕ Ajouter ressource</button>
                    <button class="help-quick-btn" onclick="addQuickMessage('🔍 Rechercher')">🔍 Rechercher</button>
                    <button class="help-quick-btn" onclick="window.open('/missions/create/', '_blank')">📋 Nouvelle mission</button>
                    <button class="help-quick-btn" onclick="addQuickMessage('🎯 Statut missions')">🎯 Statut missions</button>
                    <button class="help-quick-btn" onclick="window.open('/resources/','_blank')">👥 Liste ressources</button>
                    <button class="help-quick-btn" onclick="window.open('/missions/','_blank')">📋 Liste missions</button>
                    <button class="help-quick-btn" onclick="window.open('/dashboard/','_blank')">📈 Dashboard missions</button>
                    <button class="help-quick-btn" onclick="window.open('/dashboard/resources/','_blank')">📊 Dashboard ressources</button>
                </div>
            </div>
        </div>
    `;
    
    // Scroll to bottom
    helpMessages.scrollTop = helpMessages.scrollHeight;
    
    // Save the reset state
    saveHelpHistory();
}

function addQuickMessage(message) {
    const helpMessages = document.getElementById('helpMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'help-message bot-message';
    
    let response = '';
    
    if (message === '💰 Calculer') {
        response = `
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p>Pour calculer une facture, tu dois :</p>
                <p>1. Importer le fichier MAFE (.xlsx)</p>
                <p>2. Importer le fichier Heures IBM (.xlsx)</p>
                <p>3. Cliquer sur "Générer le Rapport"</p>
                <button class="help-quick-btn" onclick="window.open('/facturation/slr/','_blank')">Aller à la facturation</button>
            </div>
        `;
    } else if (message === '📊 Résultats') {
        response = `
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p>Les résultats de calcul s'affichent après génération du rapport. Tu peux les télécharger ou les ajuster si nécessaire.</p>
            </div>
        `;
    } else if (message === '🔍 Rechercher') {
        response = `
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p>Utilise la barre de recherche en haut de la liste des ressources pour filtrer par nom ou compétences.</p>
            </div>
        `;
    } else if (message === '🎯 Statut missions') {
        response = `
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p>Tu peux voir le statut de chaque mission dans la liste : En cours, Terminée, En attente, etc.</p>
            </div>
        `;
    } else {
        response = `
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p>${message}</p>
            </div>
        `;
    }
    
    messageDiv.innerHTML = response;
    helpMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    helpMessages.scrollTop = helpMessages.scrollHeight;
    
    // Save to localStorage
    saveHelpHistory();
}

// Save conversation to localStorage
function saveHelpHistory() {
    const helpMessages = document.getElementById('helpMessages');
    if (helpMessages) {
        localStorage.setItem('helpbot_messages', helpMessages.innerHTML);
    }
}

// Load conversation from localStorage
function loadHelpHistory() {
    const helpMessages = document.getElementById('helpMessages');
    const savedMessages = localStorage.getItem('helpbot_messages');
    
    if (savedMessages && helpMessages) {
        helpMessages.innerHTML = savedMessages;
        // Scroll to bottom
        helpMessages.scrollTop = helpMessages.scrollHeight;
    } else {
        // Initialize with welcome message if no history
        initializeHelpBot();
    }
}

// Initialize HelpBot with welcome message
function initializeHelpBot() {
    const helpMessages = document.getElementById('helpMessages');
    if (helpMessages && helpMessages.children.length === 0) {
        helpMessages.innerHTML = `
            <div class="help-message bot-message">
                <div class="help-message-avatar bot-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="help-message-content bot-content">
                    <p>Comment puis-je t'aider ?</p>
                        <div class="help-quick-buttons">
                            <button class="help-quick-btn" onclick="window.open('/facturation/slr/','_blank')">💾 Importer</button>
                            <button class="help-quick-btn" onclick="addQuickMessage('💰 Calculer')">💰 Calculer</button>
                            <button class="help-quick-btn" onclick="addQuickMessage('📊 Résultats')">📊 Résultats</button>
                            <button class="help-quick-btn" onclick="window.open('/resources/create/', '_blank')">➕ Ajouter ressource</button>
                            <button class="help-quick-btn" onclick="addQuickMessage('🔍 Rechercher')">🔍 Rechercher</button>
                            <button class="help-quick-btn" onclick="window.open('/missions/create/', '_blank')">📋 Nouvelle mission</button>
                            <button class="help-quick-btn" onclick="addQuickMessage('🎯 Statut missions')">🎯 Statut missions</button>
                            <button class="help-quick-btn" onclick="window.open('/resources/','_blank')">👥 Liste ressources</button>
                            <button class="help-quick-btn" onclick="window.open('/missions/','_blank')">📋 Liste missions</button>
                            <button class="help-quick-btn" onclick="window.open('/dashboard/','_blank')">📈 Dashboard projets</button>
                            <button class="help-quick-btn" onclick="window.open('/dashboard/resources/','_blank')">📊 Dashboard ressources</button>
                        </div>
                </div>
            </div>
        `;
        saveHelpHistory();
    }
}

// Extract KPI values from the dashboard page
function extractDashboardKPIs() {
    const kpis = {};
    
    // Try to find KPI cards and extract values
    const kpiCards = document.querySelectorAll('.kpi-card');
    
    kpiCards.forEach(card => {
        const valueElement = card.querySelector('h3');
        const labelElement = card.querySelector('p');
        
        if (valueElement && labelElement) {
            const value = valueElement.textContent.trim();
            const label = labelElement.textContent.trim();
            
            // Map labels to our KPI names
            if (label.includes('Écart Final')) kpis.ecartFinal = value;
            else if (label.includes('Coût DES')) kpis.coutDES = value;
            else if (label.includes('Marge DES')) kpis.margeDES = value;
            else if (label.includes('Taux de Dépassement')) kpis.tauxDepassement = value;
            else if (label.includes('Projets Déficitaires')) kpis.projetsDeficitaires = value;
            else if (label.includes('Budget Total')) kpis.budgetTotal = value;
            else if (label.includes('Économies Réalisées')) kpis.economiesRealisees = value;
            else if (label.includes('Taux d\'Optimisation')) kpis.tauxOptimisation = value;
        }
    });
    
    return kpis;
}

// Add explanations specifically for the dashboard
function addDashboardExplanation() {
    const helpMessages = document.getElementById('helpMessages');
    const explanationDiv = document.createElement('div');
    explanationDiv.className = 'help-message bot-message';
    
    // Extract current KPI values
    const kpis = extractDashboardKPIs();
    
    // Generate analysis based on actual values
    let analysisText = '';
    const ecartValue = parseFloat(kpis.ecartFinal?.replace(/[^-\d.]/g, '') || '0');
    const tauxValue = parseFloat(kpis.tauxDepassement?.replace(/[^-\d.]/g, '') || '0');
    const projetsDefValue = parseInt(kpis.projetsDeficitaires || '0');
    
    if (ecartValue < 0) {
        analysisText = `<strong>🚨 Situation Critique :</strong> Vos projets montrent un dépassement de ${Math.abs(ecartValue).toLocaleString()}€. Une action immédiate est nécessaire.`;
    } else if (ecartValue > 0) {
        analysisText = `<strong>✅ Situation Positive :</strong> Vos projets génèrent un bénéfice de ${ecartValue.toLocaleString()}€.`;
    } else {
        analysisText = `<strong>⚠️ Attention :</strong> Consultez les graphiques pour analyser la performance de vos projets.`;
    }

    explanationDiv.innerHTML = `
        <div class="help-message-avatar bot-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="help-message-content bot-content">
            <p><strong>📊 Analyse de la Performance de vos Projets</strong></p>
            <p>Voici l'analyse de vos indicateurs actuels :</p>
            <ul>
                <li><strong>💼 Écart Final Projet :</strong> ${kpis.ecartFinal || 'N/A'} - Différence entre prévu et réel</li>
                <li><strong>💼 Coût DES Projet :</strong> ${kpis.coutDES || 'N/A'} - Coût total calculé par le système</li>
                <li><strong>💰 Marge DES :</strong> ${kpis.margeDES || 'N/A'} - Bénéfice ou perte calculé</li>
                <li><strong>📈 Taux de Dépassement :</strong> ${kpis.tauxDepassement || 'N/A'} - Pourcentage de dépassement budgétaire</li>
                <li><strong>⚠️ Projets Déficitaires :</strong> ${kpis.projetsDeficitaires || 'N/A'} projet(s) qui perdent de l'argent</li>
                <li><strong>📋 Budget Total Missions :</strong> ${kpis.budgetTotal || 'N/A'} - Budget total alloué</li>
                <li><strong>💰 Économies Réalisées :</strong> ${kpis.economiesRealisees || 'N/A'} - Argent économisé</li>
                <li><strong>⚡ Taux d'Optimisation :</strong> ${kpis.tauxOptimisation || 'N/A'} - Amélioration de l'efficacité</li>
            </ul>
            <p>${analysisText}</p>
        </div>
    `;

    helpMessages.appendChild(explanationDiv);
    helpMessages.scrollTop = helpMessages.scrollHeight;
    saveHelpHistory();
}

// Update dashboard explanation when project selection changes
function updateDashboardAnalysis() {
    if (window.location.pathname === '/dashboard/') {
        // Find the last bot message and update it
        const helpMessages = document.getElementById('helpMessages');
        const botMessages = helpMessages.querySelectorAll('.help-message.bot-message');
        
        // Find the last dashboard explanation message
        let lastDashboardMessage = null;
        for (let i = botMessages.length - 1; i >= 0; i--) {
            const messageContent = botMessages[i].querySelector('.help-message-content');
            if (messageContent && messageContent.innerHTML.includes('📊 Analyse de la Performance')) {
                lastDashboardMessage = botMessages[i];
                break;
            }
        }
        
        if (lastDashboardMessage) {
            // Extract current KPI values
            const kpis = extractDashboardKPIs();
            
            // Generate analysis based on actual values
            let analysisText = '';
            const ecartValue = parseFloat(kpis.ecartFinal?.replace(/[^-\d.]/g, '') || '0');
            const projetsDefValue = parseInt(kpis.projetsDeficitaires || '0');
            
            if (ecartValue < 0) {
                analysisText = `<strong>🚨 Situation Critique :</strong> Ce projet montre un dépassement de ${Math.abs(ecartValue).toLocaleString()}€. Une action immédiate est nécessaire.`;
            } else if (ecartValue > 0) {
                analysisText = `<strong>✅ Situation Positive :</strong> Ce projet génère un bénéfice de ${ecartValue.toLocaleString()}€.`;
            } else {
                analysisText = `<strong>⚠️ Attention :</strong> Consultez les graphiques pour analyser la performance de ce projet.`;
            }
            
            // Get selected project name
            const selectedProject = document.querySelector('.project-item.active .project-name');
            const projectName = selectedProject ? selectedProject.textContent.trim() : 'Tous les projets';
            
            // Update the message content
            const messageContent = lastDashboardMessage.querySelector('.help-message-content');
            messageContent.innerHTML = `
                <p><strong>📊 Analyse - ${projectName}</strong></p>
                <p>Voici l'analyse des indicateurs pour cette sélection :</p>
                <ul>
                    <li><strong>💼 Écart Final Projet :</strong> ${kpis.ecartFinal || 'N/A'} - Différence entre prévu et réel</li>
                    <li><strong>💼 Coût DES Projet :</strong> ${kpis.coutDES || 'N/A'} - Coût total calculé par le système</li>
                    <li><strong>💰 Marge DES :</strong> ${kpis.margeDES || 'N/A'} - Bénéfice ou perte calculé</li>
                    <li><strong>📈 Taux de Dépassement :</strong> ${kpis.tauxDepassement || 'N/A'} - Pourcentage de dépassement budgétaire</li>
                    <li><strong>⚠️ Projets Déficitaires :</strong> ${kpis.projetsDeficitaires || 'N/A'} projet(s) qui perdent de l'argent</li>
                    <li><strong>📋 Budget Total Missions :</strong> ${kpis.budgetTotal || 'N/A'} - Budget total alloué</li>
                    <li><strong>💰 Économies Réalisées :</strong> ${kpis.economiesRealisees || 'N/A'} - Argent économisé</li>
                    <li><strong>⚡ Taux d'Optimisation :</strong> ${kpis.tauxOptimisation || 'N/A'} - Amélioration de l'efficacité</li>
                </ul>
                <p>${analysisText}</p>
                <small style="color: #666; font-style: italic;">🔄 Mise à jour automatique à ${new Date().toLocaleTimeString()}</small>
            `;
            
            // Save updated history
            saveHelpHistory();
        }
    }
}

// Add a new mission analysis message when mission selection changes
function addNewMissionAnalysis() {
    if (window.location.pathname === '/dashboard/') {
        const helpMessages = document.getElementById('helpMessages');
        const explanationDiv = document.createElement('div');
        explanationDiv.className = 'help-message bot-message';
        
        // Extract current KPI values
        const kpis = extractDashboardKPIs();
        
        // Get selected mission name
        const selectedMission = document.querySelector('.project-item.active .project-name');
        const missionName = selectedMission ? selectedMission.textContent.trim() : 'Toutes les missions';
        
        // Generate analysis based on actual values
        let analysisText = '';
        let statusIcon = '';
        const ecartValue = parseFloat(kpis.ecartFinal?.replace(/[^-\d.]/g, '') || '0');
        const projetsDefValue = parseInt(kpis.projetsDeficitaires || '0');
        
        if (ecartValue < 0) {
            analysisText = `<strong>🚨 Situation Critique :</strong> Cette mission montre un dépassement de ${Math.abs(ecartValue).toLocaleString()}€. Une action immédiate est nécessaire.`;
            statusIcon = '🚨';
        } else if (ecartValue > 0) {
            analysisText = `<strong>✅ Situation Positive :</strong> Cette mission génère un bénéfice de ${ecartValue.toLocaleString()}€.`;
            statusIcon = '✅';
        } else {
            analysisText = `<strong>⚠️ Attention :</strong> Consultez les graphiques pour analyser la performance de cette mission.`;
            statusIcon = '⚠️';
        }
        
        // Create detailed recommendations
        let recommendations = '';
        if (ecartValue < -10000) {
            recommendations = `
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin-top: 10px;">
                    <strong>📝 Recommandations urgentes :</strong><br>
                    • Analyser les causes du dépassement<br>
                    • Réduire les heures non essentielles<br>
                    • Revoir l'allocation des ressources
                </div>
            `;
        } else if (ecartValue > 5000) {
            recommendations = `
                <div style="background: #d4edda; border: 1px solid #a3cfbb; border-radius: 8px; padding: 12px; margin-top: 10px;">
                    <strong>🎆 Excellente performance !</strong><br>
                    • Mission rentable et bien gérée<br>
                    • Modèle à reproduire sur d'autres missions
                </div>
            `;
        }
        
        explanationDiv.innerHTML = `
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p><strong>${statusIcon} ${missionName}</strong></p>
                <p><strong>💼 Écart:</strong> ${kpis.ecartFinal || 'N/A'} | <strong>💰 Marge:</strong> ${kpis.margeDES || 'N/A'} | <strong>📈 Dépassement:</strong> ${kpis.tauxDepassement || 'N/A'}</p>
                <p>${analysisText}</p>
                ${recommendations}
                <small style="color: #666; font-style: italic;">🕒 ${new Date().toLocaleTimeString()}</small>
            </div>
        `;
        
        helpMessages.appendChild(explanationDiv);
        helpMessages.scrollTop = helpMessages.scrollHeight;
        saveHelpHistory();
    }
}

// Set up project selection change listeners
function setupProjectChangeListeners() {
    if (window.location.pathname === '/dashboard/') {
        // Monitor for clicks on project items
        const projectItems = document.querySelectorAll('.project-item');
        
        projectItems.forEach(item => {
            item.addEventListener('click', function() {
                // Wait a bit for the UI to update, then add a new analysis message
                setTimeout(() => {
                    addNewMissionAnalysis();
                }, 500);
            });
        });
        
        // Also monitor for any dynamic changes to KPI values using MutationObserver
        const kpiContainer = document.querySelector('.kpi-cards-grid');
        if (kpiContainer) {
            const observer = new MutationObserver(function(mutations) {
                let shouldUpdate = false;
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' || 
                        (mutation.type === 'attributes' && mutation.attributeName === 'class') ||
                        (mutation.target.tagName === 'H3')) {
                        shouldUpdate = true;
                    }
                });
                
                if (shouldUpdate) {
                    setTimeout(() => {
                        updateDashboardAnalysis();
                    }, 300);
                }
            });
            
            observer.observe(kpiContainer, {
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            });
        }
    }
}

// Check if we're on dashboard page and add automatic explanation
function checkPageAndAddExplanation() {
    const currentPath = window.location.pathname;
    
    if (currentPath === '/dashboard/') {
        setTimeout(() => {
            addDashboardExplanation();
            // Set up listeners for project changes
            setTimeout(() => {
                setupProjectChangeListeners();
            }, 500);
        }, 1000);
    } else if (currentPath === '/dashboard/resources/') {
        setTimeout(() => {
            addResourcesDashboardExplanation();
            // Set up listeners for employee changes
            setTimeout(() => {
                setupResourcesChangeListeners();
            }, 500);
        }, 1000);
    }
}

// Extract KPI values from the resources dashboard page
function extractResourcesKPIs() {
    const kpis = {};
    
    // Try to find specific KPI cards and extract values
    const totalBudgetEl = document.getElementById('totalBudgetValue');
    const maxHoursEl = document.getElementById('maxHoursToRemoveValue');
    const removeProjectEl = document.getElementById('removeFromProjectValue');
    const missionBudgetEl = document.getElementById('missionBudgetValue');
    const savingsEl = document.getElementById('potentialSavingsValue');
    const impactEl = document.getElementById('employeeImpactValue');
    
    // Extract descriptions too
    const totalBudgetDesc = document.getElementById('totalBudgetDesc');
    const maxHoursDesc = document.getElementById('maxHoursToRemoveDesc');
    const removeProjectDesc = document.getElementById('removeFromProjectDesc');
    const missionBudgetDesc = document.getElementById('missionBudgetDesc');
    const savingsDesc = document.getElementById('potentialSavingsDesc');
    const impactDesc = document.getElementById('employeeImpactDesc');
    
    if (totalBudgetEl) kpis.totalBudget = totalBudgetEl.textContent.trim();
    if (maxHoursEl) kpis.maxHours = maxHoursEl.textContent.trim();
    if (removeProjectEl) kpis.removeProject = removeProjectEl.textContent.trim();
    if (missionBudgetEl) kpis.missionBudget = missionBudgetEl.textContent.trim();
    if (savingsEl) kpis.savings = savingsEl.textContent.trim();
    if (impactEl) kpis.impact = impactEl.textContent.trim();
    
    // Get descriptions for context
    if (totalBudgetDesc) kpis.totalBudgetDesc = totalBudgetDesc.textContent.trim();
    if (maxHoursDesc) kpis.maxHoursDesc = maxHoursDesc.textContent.trim();
    if (removeProjectDesc) kpis.removeProjectDesc = removeProjectDesc.textContent.trim();
    if (missionBudgetDesc) kpis.missionBudgetDesc = missionBudgetDesc.textContent.trim();
    if (savingsDesc) kpis.savingsDesc = savingsDesc.textContent.trim();
    if (impactDesc) kpis.impactDesc = impactDesc.textContent.trim();
    
    return kpis;
}

// Add explanations specifically for the resources dashboard
function addResourcesDashboardExplanation() {
    const helpMessages = document.getElementById('helpMessages');
    const explanationDiv = document.createElement('div');
    explanationDiv.className = 'help-message bot-message';
    
    // Extract current KPI values
    const kpis = extractResourcesKPIs();
    
    // Get selected employee name
    const selectedEmployee = document.querySelector('.project-item.active .project-name');
    const employeeName = selectedEmployee ? selectedEmployee.textContent.trim() : 'Tous les employés';
    
    // Parse values for analysis
    const budgetValue = parseFloat(kpis.totalBudget?.replace(/[^\d]/g, '') || '0');
    const savingsValue = parseFloat(kpis.savings?.replace(/[^\d]/g, '') || '0');
    const hoursValue = parseFloat(kpis.maxHours?.replace(/[^\d]/g, '') || '0');
    
    // Generate contextual analysis
    let analysisText = '';
    let statusIcon = '';
    let recommendations = '';
    
    if (savingsValue > 10000) {
        analysisText = `<strong>🚨 Attention Importante :</strong> Des économies de ${kpis.savings} sont possibles. Cela indique des dépassements budgétaires significatifs.`;
        statusIcon = '🚨';
        recommendations = `
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin-top: 10px;">
                <strong>📝 Recommandations urgentes :</strong><br>
                • Analyser le projet "${kpis.removeProject}" en priorité<br>
                • Réduire ${kpis.maxHours} pour équilibrer le budget<br>
                • Revoir l'allocation des ressources
            </div>
        `;
    } else if (savingsValue > 1000) {
        analysisText = `<strong>⚠️ Optimisation Possible :</strong> Des économies de ${kpis.savings} sont identifiées. Une attention modérée est nécessaire.`;
        statusIcon = '⚠️';
        recommendations = `
            <div style="background: #e2e3e5; border: 1px solid #d6d8db; border-radius: 8px; padding: 12px; margin-top: 10px;">
                <strong>💡 Suggestions d'amélioration :</strong><br>
                • Surveiller le projet "${kpis.removeProject}"<br>
                • Optimiser l'utilisation des ${kpis.maxHours}
            </div>
        `;
    } else {
        analysisText = `<strong>✅ Situation Maîtrisée :</strong> Les coûts sont bien contrôlés avec des économies limitées (${kpis.savings}).`;
        statusIcon = '✅';
        recommendations = `
            <div style="background: #d4edda; border: 1px solid #a3cfbb; border-radius: 8px; padding: 12px; margin-top: 10px;">
                <strong>🎯 Excellente gestion !</strong><br>
                • Budget bien maîtrisé<br>
                • Continuer le suivi actuel
            </div>
        `;
    }

    explanationDiv.innerHTML = `
        <div class="help-message-avatar bot-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="help-message-content bot-content">
            <p><strong>${statusIcon} Analyse Ressources - ${employeeName}</strong></p>
            <p>Voici l'analyse des indicateurs de performance :</p>
            <ul>
                <li><strong>💼 Budget Total :</strong> ${kpis.totalBudget} (${kpis.totalBudgetDesc})</li>
                <li><strong>⚡ Heures à Retirer :</strong> ${kpis.maxHours} (${kpis.maxHoursDesc})</li>
                <li><strong>📉 Projet Prioritaire :</strong> ${kpis.removeProject} (${kpis.removeProjectDesc})</li>
                <li><strong>💰 Budget Mission :</strong> ${kpis.missionBudget} (${kpis.missionBudgetDesc})</li>
                <li><strong>💰 Économies Possibles :</strong> ${kpis.savings} (${kpis.savingsDesc})</li>
                <li><strong>👤 Impact :</strong> ${kpis.impact} (${kpis.impactDesc})</li>
            </ul>
            <p>${analysisText}</p>
            ${recommendations}
            <small style="color: #666; font-style: italic;">🔄 Analyse à ${new Date().toLocaleTimeString()}</small>
        </div>
    `;

    helpMessages.appendChild(explanationDiv);
    helpMessages.scrollTop = helpMessages.scrollHeight;
    saveHelpHistory();
}

// Set up employee selection change listeners for resources dashboard
function setupResourcesChangeListeners() {
    if (window.location.pathname === '/dashboard/resources/') {
        // Monitor for clicks on employee items
        const employeeItems = document.querySelectorAll('.project-item');
        
        employeeItems.forEach(item => {
            item.addEventListener('click', function() {
                // Wait a bit for the UI to update, then add a new analysis message
                setTimeout(() => {
                    addNewResourcesAnalysis();
                }, 800); // Slightly longer delay for resources dashboard
            });
        });
        
        // Also monitor for any dynamic changes to KPI values using MutationObserver
        const kpiContainer = document.querySelector('.kpi-cards-grid');
        if (kpiContainer) {
            const observer = new MutationObserver(function(mutations) {
                let shouldUpdate = false;
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' || 
                        (mutation.type === 'attributes' && mutation.attributeName === 'class') ||
                        (mutation.target.tagName === 'H3')) {
                        shouldUpdate = true;
                    }
                });
                
                if (shouldUpdate) {
                    setTimeout(() => {
                        updateResourcesAnalysis();
                    }, 500);
                }
            });
            
            observer.observe(kpiContainer, {
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            });
        }
    }
}

// Add a new resources analysis message when employee selection changes
function addNewResourcesAnalysis() {
    if (window.location.pathname === '/dashboard/resources/') {
        const helpMessages = document.getElementById('helpMessages');
        const explanationDiv = document.createElement('div');
        explanationDiv.className = 'help-message bot-message';
        
        // Extract current KPI values
        const kpis = extractResourcesKPIs();
        
        // Get selected employee name
        const selectedEmployee = document.querySelector('.project-item.active .project-name');
        const employeeName = selectedEmployee ? selectedEmployee.textContent.trim() : 'Tous les employés';
        
        // Parse values for analysis
        const budgetValue = parseFloat(kpis.totalBudget?.replace(/[^\d]/g, '') || '0');
        const savingsValue = parseFloat(kpis.savings?.replace(/[^\d]/g, '') || '0');
        const hoursValue = parseFloat(kpis.maxHours?.replace(/[^\d]/g, '') || '0');
        
        // Generate contextual analysis
        let analysisText = '';
        let statusIcon = '';
        let recommendations = '';
        
        if (savingsValue > 10000) {
            analysisText = `<strong>🚨 Attention Critique :</strong> ${employeeName} présente des économies potentielles de ${kpis.savings}. Action urgente requise.`;
            statusIcon = '🚨';
            recommendations = `
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin-top: 10px;">
                    <strong>🚨 Actions immédiates :</strong><br>
                    • Réviser l'affectation de ${employeeName}<br>
                    • Réduire ${kpis.maxHours} sur "${kpis.removeProject}"<br>
                    • Réaffecter vers d'autres projets si possible
                </div>
            `;
        } else if (savingsValue > 1000) {
            analysisText = `<strong>⚠️ Optimisation Recommandée :</strong> ${employeeName} offre ${kpis.savings} d'économies potentielles.`;
            statusIcon = '⚠️';
            recommendations = `
                <div style="background: #e2e3e5; border: 1px solid #d6d8db; border-radius: 8px; padding: 12px; margin-top: 10px;">
                    <strong>💡 Suggestions :</strong><br>
                    • Ajuster la charge de travail de ${employeeName}<br>
                    • Surveiller "${kpis.removeProject}"<br>
                    • Optimiser ${kpis.maxHours}
                </div>
            `;
        } else {
            analysisText = `<strong>✅ Performance Optimale :</strong> ${employeeName} présente une utilisation efficace des ressources (${kpis.savings} d'écart).`;
            statusIcon = '✅';
            recommendations = `
                <div style="background: #d4edda; border: 1px solid #a3cfbb; border-radius: 8px; padding: 12px; margin-top: 10px;">
                    <strong>🎯 Excellent travail !</strong><br>
                    • ${employeeName} : gestion efficace<br>
                    • Maintenir le niveau actuel<br>
                    • Modèle à suivre pour d'autres employés
                </div>
            `;
        }
        
        explanationDiv.innerHTML = `
            <div class="help-message-avatar bot-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="help-message-content bot-content">
                <p><strong>${statusIcon} ${employeeName}</strong></p>
                <p><strong>💼 Budget:</strong> ${kpis.totalBudget} | <strong>⚡ Heures:</strong> ${kpis.maxHours} | <strong>💰 Économies:</strong> ${kpis.savings} | <strong>👤 Impact:</strong> ${kpis.impact}</p>
                <p>${analysisText}</p>
                ${recommendations}
                <small style="color: #666; font-style: italic;">🕒 ${new Date().toLocaleTimeString()}</small>
            </div>
        `;
        
        helpMessages.appendChild(explanationDiv);
        helpMessages.scrollTop = helpMessages.scrollHeight;
        saveHelpHistory();
    }
}

// Update resources analysis when values change
function updateResourcesAnalysis() {
    if (window.location.pathname === '/dashboard/resources/') {
        // Find the last bot message and update it
        const helpMessages = document.getElementById('helpMessages');
        const botMessages = helpMessages.querySelectorAll('.help-message.bot-message');
        
        // Find the last resources analysis message
        let lastResourcesMessage = null;
        for (let i = botMessages.length - 1; i >= 0; i--) {
            const messageContent = botMessages[i].querySelector('.help-message-content');
            if (messageContent && (messageContent.innerHTML.includes('Analyse Ressources') || messageContent.innerHTML.includes('💼 Budget:'))) {
                lastResourcesMessage = botMessages[i];
                break;
            }
        }
        
        if (lastResourcesMessage) {
            // Extract current KPI values
            const kpis = extractResourcesKPIs();
            
            // Get selected employee name
            const selectedEmployee = document.querySelector('.project-item.active .project-name');
            const employeeName = selectedEmployee ? selectedEmployee.textContent.trim() : 'Tous les employés';
            
            // Update the message content
            const messageContent = lastResourcesMessage.querySelector('.help-message-content');
            const savingsValue = parseFloat(kpis.savings?.replace(/[^\d]/g, '') || '0');
            
            let statusIcon = '✅';
            let analysisText = `<strong>✅ Situation Maîtrisée :</strong> Les coûts sont bien contrôlés.`;
            
            if (savingsValue > 10000) {
                statusIcon = '🚨';
                analysisText = `<strong>🚨 Attention Importante :</strong> Des économies de ${kpis.savings} sont possibles.`;
            } else if (savingsValue > 1000) {
                statusIcon = '⚠️';
                analysisText = `<strong>⚠️ Optimisation Possible :</strong> Des économies de ${kpis.savings} sont identifiées.`;
            }
            
            messageContent.innerHTML = `
                <p><strong>${statusIcon} Analyse Ressources - ${employeeName}</strong></p>
                <p><strong>💼 Budget:</strong> ${kpis.totalBudget} | <strong>⚡ Heures:</strong> ${kpis.maxHours} | <strong>💰 Économies:</strong> ${kpis.savings} | <strong>👤 Impact:</strong> ${kpis.impact}</p>
                <p>${analysisText}</p>
                <small style="color: #666; font-style: italic;">🔄 Mis à jour à ${new Date().toLocaleTimeString()}</small>
            `;
            
            // Save updated history
            saveHelpHistory();
        }
    }
}

// Initialize HelpBot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set initial state - window closed
    const helpWindow = document.getElementById('helpWindow');
    if (helpWindow) {
        helpWindow.classList.remove('open');
    }
    
    // Initialize with welcome message if needed
    initializeHelpBot();
    
    // Check current page and add explanations if needed
    checkPageAndAddExplanation();
});
