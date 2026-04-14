# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BarberPOSController(http.Controller):

    @http.route(['/barber/pos/<int:session_id>'], type='http', auth='user', website=True)
    def barber_pos_interface(self, session_id, **kwargs):
        """Affiche l'interface du Point de Vente pour une session donnée."""
        session = request.env['barber.session'].browse(session_id)
        if not session.exists() or session.state != 'open':
            return request.render('website.404')

        # Pour l'instant on affiche une page HTML simple en attendant le template QWeb complet
        # On passe les données nécessaires à l'interface
        values = {
            'session': session,
            'barber': session.barber_id,
            'company': request.env.company,
        }
        
        # En Odoo, on préfère utiliser request.render('addon.template_id', values)
        # Je vais créer le template QWeb minimaliste juste après.
        return request.render('barber_pos.barber_pos_index', values)
