# -*- coding: utf-8 -*-
from uuid import uuid4
from odoo import api, fields, models, _
from odoo.addons.google_calendar.models.google_sync import google_calendar_token
from odoo.addons.google_calendar.utils.google_calendar import GoogleCalendarService
import logging
_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'


    def synchroniser_google_action(self):


        _logger.warning("## synchroniser_google_action self = %s" % (self))


        for obj in self.browse(self.env.context['active_ids']):

            #if not obj.google_id:
            #    obj.google_id = uuid4().hex


            _logger.warning("## synchroniser_google_action obj = %s" % (obj))

            #if obj.google_id:
            #event_id = obj.id
            #_logger.warning("## Recherche si évènement existe avant de le créer event_id = %s" % (event_id))
            #url = "/calendar/v3/calendars/primary/events/%s" % event_id
            for line in obj.attendee_ids:
                user=line.is_user_id
                if user:
                    with google_calendar_token(user.sudo()) as token:
                        if token:
                            _logger.warning("## token = %s" % (token))
                            headers = {'Content-type': 'application/json', 'Authorization': 'Bearer %s' % token}
                            params = {'access_token': token}
                            values = obj._google_values()
                            _logger.warning("## values = %s" % (values))
                            google_service = GoogleCalendarService(self.with_user(user).env['google.service'])
                            email  = line.email
                            #values["organizer"]   = {'email': email, 'self': True}
                            #values["attendees"]=[]
                            #values["description"]="GoogleSync write\ntoto et tutu\nsur 2 lignes\n"+"\n"+email

                            #if not values.get('id'):
                            #    values['id'] = uuid4().hex

                            event_id = values.get('id')
                            _logger.warning("## synchroniser_google_action event_id = %s" % (event_id))


                            #_logger.warning("## email,google_service = %s,%s" % (email, google_service))
                            try:
                                _logger.warning("## _google_patch email = %s" % (email))
                                obj.with_user(user)._google_patch(google_service, event_id, values, timeout=3)
                            except:
                                _logger.exception("## _google_patch  ERROR email = %s" % (email))





    @api.onchange('partner_ids','start','duration')
    def _compute_is_alerte(self):

        for obj in self:
            alertes=[]
            for partner in obj.partner_ids:
                SQL="""
                    SELECT rp.name, e.name event_name
                    FROM calendar_event e join calendar_attendee a on e.id=a.event_id
                                          join res_partner      rp on a.partner_id=rp.id 
                    WHERE 
                        e.active='t' and 
                        e.id<>%s and
                        a.state not in ('declined') and
                        a.partner_id=%s and ( 
                            (e.start<%s and e.stop>%s) or
                            (e.start<%s and e.stop>%s) or
                            (e.start<=%s and e.stop>=%s) or
                            (e.start>=%s and e.stop<=%s) or
                            (e.start=%s and e.stop=%s)
                        )
                    ORDER BY rp.name, e.name
                """
                self._cr.execute(SQL, [
                    obj._origin.id, partner._origin.id, 
                    obj.start, obj.start, 
                    obj.stop , obj.stop, 
                    obj.start, obj.stop, 
                    obj.start, obj.stop, 
                    obj.start, obj.stop
                ])
                events=self._cr.fetchall()
                for e in events:
                    msg=e[0]+" : "+e[1]
                    alertes.append(msg)
            if len(alertes):
                alertes="\n".join(alertes)
            else:
                alertes=False
            obj.is_alerte=alertes


    @api.onchange('partner_ids')
    def _compute_is_participants(self):
        for obj in self:
            lines=[]
            for attendee in obj.attendee_ids:
                if attendee.state == "declined":
                    lines.append('-  <del style="color:red">'+attendee.partner_id.name+"</del>")
                if attendee.state == "accepted":
                    lines.append('-  <b style="color:green">'+attendee.partner_id.name+"</b>")
                if attendee.state not in ["declined","accepted"]:
                    lines.append('-  <i style="color:gray">'+attendee.partner_id.name+"</i>")
            obj.is_participants = "<br />".join(lines)







    is_alerte       = fields.Text('Alerte'      , copy=False, compute=_compute_is_alerte)
    is_participants = fields.Text('Participants', copy=False, compute=_compute_is_participants)


    def _ajouter_invitation_responsable_action(self):
        for obj in self.browse(self.env.context['active_ids']):
            for partner in obj.partner_ids:
                if partner not in obj.attendee_ids.partner_id:
                    vals={
                        "event_id"  : obj.id,
                        "partner_id": partner.id,
                        "state"     : "accepted",
                    }
                    self.env['calendar.attendee'].create(vals)


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
