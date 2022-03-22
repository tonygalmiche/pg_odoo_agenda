# -*- coding: utf-8 -*-
from uuid import uuid4
from odoo import api, fields, models, _
from odoo.addons.google_calendar.models.google_sync import google_calendar_token
from odoo.addons.google_calendar.utils.google_calendar import GoogleCalendarService
import logging
_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'


    def synchroniser_google_user(self,event,user):
        with google_calendar_token(user.sudo()) as token:
            if token:
                _logger.warning("## token = %s" % (token))
                headers = {'Content-type': 'application/json', 'Authorization': 'Bearer %s' % token}
                params = {'access_token': token}
                values = event._google_values()
                _logger.warning("## values = %s" % (values))
                google_service = GoogleCalendarService(self.with_user(user).env['google.service'])
                event_id = values.get('id')
                _logger.warning("## synchroniser_google_action event_id = %s" % (event_id))
                try:
                    _logger.warning("## _google_patch event = %s" % (event))
                    event.with_user(user)._google_patch(google_service, event_id, values, timeout=3)
                except:
                    _logger.exception("## _google_patch  ERROR event = %s" % (event))


    def synchroniser_google_action(self):
        for obj in self.browse(self.env.context['active_ids']):
            for line in obj.attendee_ids:
                user=line.is_user_id
                _logger.warning("## synchroniser_google_action user = %s" % (user.login))
                if user:
                    self.synchroniser_google_user(obj,user)


    @api.onchange('partner_ids','start','duration')
    def _compute_is_alerte(self):

        for obj in self:
            alertes=[]
            for partner in obj.partner_ids:
                SQL="""
                    SELECT rp.name, e.name event_name, e.privacy
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
                    if e[2] == 'private':
                        event_name = 'Occupé(e)'
                    else:
                        event_name = e[1]
                    msg=e[0]+" : "+event_name
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


    # def agenda_journee_action(self):
    #     for obj in self:
    #         res= {
    #             'name': 'Agenda',
    #             'view_mode': 'calendar',
    #             'res_model': 'calendar.event',
    #             'res_id': obj.id,
    #             'type': 'ir.actions.act_window',
    #             'view_id': self.env.ref('pg_odoo_agenda.view_calendar_event_calendar_journee').id,
    #             'domain': [["start","<=","2021-07-04 21:59:59"],["stop",">=","2021-06-27 22:00:00"],["partner_ids","in",[3,7]]],
    #         }
    #         return res


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



    def _accepter_invitation_actions(self):
        for obj in self.browse(self.env.context['active_ids']):
            obj.state="accepted"


    def _refuser_invitation_actions(self):
        for obj in self.browse(self.env.context['active_ids']):
            obj.state="declined"


    def write(self, vals):
        res = super(CalendarAttendee, self).write(vals)
        self.env['calendar.event'].synchroniser_google_user(self.event_id,self.is_user_id)
        return res

