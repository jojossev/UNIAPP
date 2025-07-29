// Fonction pour mettre à jour le compteur d'articles du panier
function updateCartCount() {
    // Vérifier si l'utilisateur est connecté
    if (document.body.querySelector('.cart-badge')) {
        fetch('/panier/api/nombre-articles/')
            .then(response => response.json())
            .then(data => {
                const badge = document.querySelector('.cart-badge');
                if (badge) {
                    badge.textContent = data.nombre_articles;
                    badge.style.display = data.nombre_articles > 0 ? 'inline-block' : 'none';
                }
            })
            .catch(error => console.error('Erreur lors de la mise à jour du panier:', error));
    }
}

// Gestionnaire d'événements pour le chargement du document
document.addEventListener('DOMContentLoaded', function() {
    // Mettre à jour le compteur du panier au chargement de la page
    updateCartCount();
    // Gestion des messages flash (fermeture automatique après 5 secondes)
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            setTimeout(() => {
                const fadeEffect = setInterval(() => {
                    if (!alert.style.opacity) {
                        alert.style.opacity = 1;
                    }
                    if (alert.style.opacity > 0) {
                        alert.style.opacity -= 0.1;
                    } else {
                        clearInterval(fadeEffect);
                        alert.remove();
                    }
                }, 50);
            }, 5000);
        });
    }

    // Gestion de l'affichage/masquage du mot de passe
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            // Basculer le type d'entrée
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // Changer l'icône
            icon.classList.toggle('bi-eye');
            icon.classList.toggle('bi-eye-slash');
        });
    });

    // Validation des formulaires côté client
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // Désactiver la soumission du formulaire si des champs invalides
    (function() {
        'use strict';
        window.addEventListener('load', function() {
            const forms = document.getElementsByClassName('needs-validation');
            const validation = Array.prototype.filter.call(forms, function(form) {
                form.addEventListener('submit', function(event) {
                    if (form.checkValidity() === false) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                }, false);
            });
        }, false);
    })();

    // Animation pour les boutons de chargement
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Traitement...';
                this.disabled = true;
                this.form.submit();
            }
        });
    });
});

// Fonction pour afficher une alerte
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container:first-of-type');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Fermer automatiquement après 5 secondes
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
    
    return alertDiv;
}

// Fonction pour afficher un modal
function showModal(title, content, buttons = []) {
    const modalId = 'customModal' + Date.now();
    const modalHtml = `
    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    ${buttons.map(btn => 
                        `<button type="button" class="btn ${btn.class || 'btn-secondary'}" ${btn.id ? `id="${btn.id}"` : ''} data-bs-dismiss="${btn.dismiss !== false ? 'modal' : ''}">
                            ${btn.text}
                        </button>`
                    ).join('')}
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Ajouter le modal au DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Afficher le modal
    const modalElement = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Nettoyer après la fermeture
    modalElement.addEventListener('hidden.bs.modal', function () {
        modalElement.remove();
    });
    
    return modal;
}
