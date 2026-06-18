(function() {
    "use strict";
    console.log("[BarberPOS] Script chargé et exécution immédiate...");

    // État de l'application
    var state = {
        services: [],
        customers: [],
        config: {},
        cart: [],
        total: 0.0,
        selectedCustomerId: null,
        pointsUsed: 0.0,
        sessionId: typeof odoo_info !== 'undefined' ? odoo_info.session_id : 1,
        barberId: typeof odoo_info !== 'undefined' ? odoo_info.barber_id : 1
    };

    function init() {
        console.log("[BarberPOS] Initialisation du DOM...");
        loadConfig();
        loadServices();
        loadCustomers();
        
        const payBtn = document.getElementById('btn_pay_order');
        if (payBtn) {
            payBtn.onclick = function() {
                handlePayment();
            };
        }

        const customerSelect = document.getElementById('customer_select');
        if (customerSelect) {
            customerSelect.onchange = function() {
                state.selectedCustomerId = this.value ? parseInt(this.value) : null;
                state.pointsUsed = 0.0;
                updateCustomerInfo();
                updateCart();
            };
        }
    }

    // fallback si DOM déjà prêt
    if (document.readyState === "complete" || document.readyState === "interactive") {
        setTimeout(init, 1);
    } else {
        document.addEventListener("DOMContentLoaded", init);
    }

    function loadConfig() {
        fetch("/web/dataset/call_kw/barber.config/search_read", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: "barber.config",
                    method: "search_read",
                    args: [[]],
                    kwargs: { fields: ['enable_vip', 'vip_point_ratio', 'vip_point_value'], limit: 1 }
                },
                id: Math.floor(Math.random() * 1000)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result && data.result.length > 0) {
                state.config = data.result[0];
            }
        });
    }

    function loadCustomers() {
        fetch("/web/dataset/call_kw/res.partner/search_read", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: "res.partner",
                    method: "search_read",
                    args: [[]],
                    kwargs: {
                        fields: ['name', 'vip_points', 'is_vip'],
                        limit: 100
                    }
                },
                id: Math.floor(Math.random() * 1000)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                state.customers = data.result;
                renderCustomers();
            }
        });
    }

    function renderCustomers() {
        const select = document.getElementById('customer_select');
        if (!select) return;
        
        state.customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer.id;
            option.text = customer.name + (customer.is_vip ? " ⭐" : "");
            select.appendChild(option);
        });
    }

    function updateCustomerInfo() {
        const infoDiv = document.getElementById('customer_vip_info');
        if (!infoDiv) return;

        if (state.selectedCustomerId) {
            const customer = state.customers.find(c => c.id === state.selectedCustomerId);
            if (customer && state.config.enable_vip) {
                document.getElementById('customer_points').innerText = customer.vip_points.toFixed(1);
                document.getElementById('customer_points_val').innerText = (customer.vip_points * state.config.vip_point_value).toFixed(2);
                infoDiv.style.display = 'block';
                return;
            }
        }
        infoDiv.style.display = 'none';
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
                        fields: ['name', 'price', 'allow_price_override'],
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
            price: service.price,
            allow_price_override: service.allow_price_override
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
            
            let priceHtml = `<span class="fw-bold mx-2">${item.price}</span>`;
            if (item.allow_price_override) {
                priceHtml = `<input type="number" class="form-control form-control-sm mx-2 item-price-input" 
                             style="width: 80px;" value="${item.price}" step="0.01">`;
            }

            line.innerHTML = `
                <span class="small">${item.name}</span>
                ${priceHtml}
                <button class="btn btn-sm btn-link text-danger p-0" style="text-decoration:none;">✕</button>
            `;

            const priceInput = line.querySelector('.item-price-input');
            if (priceInput) {
                priceInput.onchange = function() {
                    const newPrice = parseFloat(this.value);
                    if (!isNaN(newPrice) && newPrice >= 0) {
                        state.cart[index].price = newPrice;
                        updateCart();
                    } else {
                        this.value = item.price;
                    }
                };
            }

            line.querySelector('button').onclick = function(e) {
                e.stopPropagation();
                state.cart.splice(index, 1);
                updateCart();
            };
            container.appendChild(line);
        });

        totalEl.innerText = state.total.toFixed(2) + " DZD";

        // Affichage points VIP si possible
        if (state.selectedCustomerId && state.config.enable_vip) {
            const customer = state.customers.find(c => c.id === state.selectedCustomerId);
            const maxPoints = Math.min(customer.vip_points, state.total / state.config.vip_point_value);
            
            const pointsDiv = document.createElement('div');
            pointsDiv.className = 'mt-3 pt-3 border-top';
            pointsDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span class="small">Utiliser points (Max: ${maxPoints.toFixed(1)})</span>
                    <input type="number" class="form-control form-control-sm w-25" id="points_to_use" 
                           value="${state.pointsUsed}" max="${maxPoints}" step="0.1">
                </div>
                <div class="d-flex justify-content-between mt-1 text-success small">
                    <span>Remise points</span>
                    <span>-${(state.pointsUsed * state.config.vip_point_value).toFixed(2)} DZD</span>
                </div>
            `;
            container.appendChild(pointsDiv);

            const pointsInput = pointsDiv.querySelector('#points_to_use');
            pointsInput.onchange = function() {
                let val = parseFloat(this.value) || 0;
                if (val < 0) val = 0;
                if (val > maxPoints) val = maxPoints;
                state.pointsUsed = val;
                updateCart();
            };
        }
    }

    function handlePayment() {
        if (state.cart.length === 0) return alert("Panier vide");
        
        if (!confirm("Confirmer le paiement ?")) return;

        const finalAmount = state.total - (state.pointsUsed * state.config.vip_point_value);

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
                        partner_id: state.selectedCustomerId,
                        points_used: state.pointsUsed,
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
