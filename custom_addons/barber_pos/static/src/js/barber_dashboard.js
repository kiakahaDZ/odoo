(function() {
    "use strict";
    console.log("[BarberPOS] Script chargé et exécution immédiate...");

    // État de l'application
    var state = {
        services: [],
        cart: [],
        total: 0.0,
        sessionId: typeof odoo_info !== 'undefined' ? odoo_info.session_id : 1,
        barberId: typeof odoo_info !== 'undefined' ? odoo_info.barber_id : 1
    };

    function init() {
        console.log("[BarberPOS] Initialisation du DOM...");
        loadServices();
        
        const payBtn = document.getElementById('btn_pay_order');
        if (payBtn) {
            payBtn.onclick = function() {
                handlePayment();
            };
        }
    }

    // fallback si DOM déjà prêt
    if (document.readyState === "complete" || document.readyState === "interactive") {
        setTimeout(init, 1);
    } else {
        document.addEventListener("DOMContentLoaded", init);
    }

    function loadServices() {
        console.log("[BarberPOS] Appel RPC pour charger les services...");
        
        // Utilisation de fetch pour être sûr de passer partout si l'asset RPC d'Odoo n'est pas dispo
        fetch("/web/dataset/call_kw/barber.service/search_read", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: "barber.service",
                    method: "search_read",
                    args: [[['active', '=', true]]],
                    kwargs: {
                        fields: ['name', 'price'],
                        limit: 80
                    }
                },
                id: Math.floor(Math.random() * 1000)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                console.log("[BarberPOS] Services reçus :", data.result.length);
                state.services = data.result;
                renderServices();
            } else if (data.error) {
                console.error("[BarberPOS] Erreur Odoo :", data.error);
            }
        })
        .catch(err => {
            console.error("[BarberPOS] Erreur réseau :", err);
        });
    }

    function renderServices() {
        const container = document.getElementById('services_list');
        if (!container) return;
        
        container.innerHTML = '';
        if (state.services.length === 0) {
            container.innerHTML = '<p class="text-warning">Aucune prestation active trouvée en base de données.</p>';
            return;
        }

        state.services.forEach(service => {
            const div = document.createElement('div');
            div.className = 'col-md-4 col-sm-6 mb-3';
            div.innerHTML = `
                <div class="card h-100 shadow-sm service-card border-0" style="cursor: pointer; background: white; border-radius: 15px;">
                    <div class="card-body text-center p-4">
                        <div style="font-size: 2.5rem; margin-bottom: 10px;">✂️</div>
                        <h5 class="fw-bold">${service.name}</h5>
                        <div class="text-primary fw-bold" style="font-size: 1.2rem;">${service.price} DZD</div>
                    </div>
                </div>
            `;
            div.onclick = function() { addToCart(service); };
            container.appendChild(div);
        });
    }

    function addToCart(service) {
        state.cart.push({
            id: service.id,
            name: service.name,
            price: service.price
        });
        updateCart();
    }

    function updateCart() {
        const container = document.getElementById('current_order_lines');
        const totalEl = document.getElementById('order_total');
        
        container.innerHTML = '';
        state.total = 0;

        state.cart.forEach((item, index) => {
            state.total += item.price;
            const line = document.createElement('div');
            line.className = 'd-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded shadow-sm';
            line.innerHTML = `
                <span class="small">${item.name}</span>
                <span class="fw-bold mx-2">${item.price}</span>
                <button class="btn btn-sm btn-link text-danger p-0" style="text-decoration:none;">✕</button>
            `;
            line.querySelector('button').onclick = function(e) {
                e.stopPropagation();
                state.cart.splice(index, 1);
                updateCart();
            };
            container.appendChild(line);
        });

        totalEl.innerText = state.total.toFixed(2) + " DZD";
    }

    function handlePayment() {
        if (state.cart.length === 0) return alert("Panier vide");
        
        if (!confirm("Confirmer le paiement ?")) return;

        fetch("/web/dataset/call_kw/barber.order/create_from_pos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: "barber.order",
                    method: "create_from_pos",
                    args: [{
                        session_id: state.sessionId,
                        barber_id: state.barberId,
                        lines: state.cart.map(i => ({service_id: i.id, qty: 1, unit_price: i.price}))
                    }],
                    kwargs: {}
                },
                id: Math.floor(Math.random() * 1000)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                alert("✅ Payé ! Commande : " + data.result);
                state.cart = [];
                updateCart();
            } else {
                alert("❌ Erreur : " + (data.error ? data.error.message : "Inconnue"));
            }
        });
    }

})();
