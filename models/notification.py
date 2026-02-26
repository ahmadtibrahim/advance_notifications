import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AdvanceNotification(models.Model):
    _name = "advance.notification"
    _description = "Advanced User Notifications"
    _order = "create_date desc"

    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    message_id = fields.Many2one("mail.message", required=True, ondelete="cascade", index=True)
    model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    ai_summary = fields.Text()
    is_done = fields.Boolean(default=False, index=True)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        for message in messages:
            if not (
                message.message_type == "email"
                and message.model
                and message.res_id
                and message.body
            ):
                continue

            record = self.env[message.model].browse(message.res_id).exists()
            if not record or "user_id" not in record._fields:
                continue

            target_user = record.user_id
            if not target_user:
                continue

            notification = self.env["advance.notification"].create(
                {
                    "user_id": target_user.id,
                    "message_id": message.id,
                    "model": message.model,
                    "res_id": message.res_id,
                }
            )

            self.env["bus.bus"]._sendone(
                target_user.partner_id,
                "advance_notifications_channel",
                {
                    "id": notification.id,
                    "model": notification.model,
                    "res_id": notification.res_id,
                },
            )

            summary = self.env["openai.service"].summarize_message(message.body)
            if summary:
                notification.write({"ai_summary": summary})
            else:
                _logger.debug("OpenAI summary not available for notification %s", notification.id)

        return messages
