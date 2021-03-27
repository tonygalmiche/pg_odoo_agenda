# -*- coding: utf-8 -*-
from odoo import api, fields, models, _



class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _ajouter_invitation_responsable_action(self):
        for obj in self.browse(self.env.context['active_ids']):
            for partner in obj.partner_ids:
                if partner not in obj.attendee_ids.partner_id:
                    print("Ajouter", partner.name,obj.id)
                    vals={
                        "event_id"  : obj.id,
                        "partner_id": partner.id,
                        "state"     : "accepted",
                    }
                    self.env['calendar.attendee'].create(vals)


#   id   | event_id | partner_id |    state    |         common_name          | availability |           access_token           | create_uid |        create_date         | write_uid |         write_date         | is_user_id 
# -------+----------+------------+-------------+------------------------------+--------------+----------------------------------+------------+----------------------------+-----------+----------------------------+------------
#  10670 |     5015 |         65 | accepted    | Laetitia LEBRUN              |              | eab118c4b99344aa965bfc5d46ed7487 |         81 | 2021-03-22 10:14:20.049383 |        64 | 2021-03-22 10:17:38.760978 |         64
#  10673 |     5016 |         65 | accepted    | Laetitia LEBRUN              |              | 2eca7e6a1ab44d368f81c7847c5eb016 |         81 | 2021-03-22 10:14:20.049383 |        64 | 2021-03-22 10:17:38.760978 |         64





class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    @api.depends('partner_id')
    def _compute_is_user_id(self):
        for obj in self:
            user_id=False
            if obj.partner_id:
                users = self.env['res.users'].search([
                    ('partner_id', '=', obj.partner_id.id),
                ])
                if users:
                    user_id=users[0].id
            obj.is_user_id=user_id


    is_user_id = fields.Many2one('res.users', 'Utilisateur', compute='_compute_is_user_id', store=True, readonly=True, index=True)




# class Meeting(models.Model):
#     _inherit = 'calendar.event'


#     def _compute_is_je_participe(self):
#         for obj in self:
#             test=False
#             if self.env.user.partner_id in obj.partner_ids:
#                 test=True
#             obj.is_je_participe=test
#     is_je_participe = fields.Boolean('Je participe', compute='_compute_is_je_participe')


# class Meeting(models.Model):
#     _inherit = 'calendar.event'
 
#     @api.model_create_multi
#     def create(self, vals_list):
#         ## Bug création en double des repetitions sur la premiere journée ******
#         if vals_list:
#             v=vals_list[0]
#             user_id=v.get("user_id")
#             if user_id:
#                 print('user_id=',user_id,vals_list)
#                 start=v.get("start")
#                 events = self.env['calendar.event'].search([('user_id', '=', user_id),('start', '=', start)], limit=1)
#                 if events:
#                     return events
#         #***********************************************************************

#         res=super().create(vals_list)
#         return res
