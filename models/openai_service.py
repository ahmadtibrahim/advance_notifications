import logging

import requests

from odoo import models
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class OpenAIService(models.AbstractModel):
    _name = "openai.service"
    _description = "OpenAI Service"

    def summarize_message(self, body):
        api_key = self.env["ir.config_parameter"].sudo().get_param("openai.api_key")
        if not api_key or not body:
            return False

        clean_text = html2plaintext(body).strip()[:1200]
        if not clean_text:
            return False

        payload = {
            "model": "gpt-4.1-mini",
            "messages": [
                {
                    "role": "user",
                    "content": f"Summarize this business email in ONE short sentence:\n\n{clean_text}",
                }
            ],
            "temperature": 0.2,
        }

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
        except requests.RequestException:
            _logger.exception("OpenAI request failed for advance notifications summary")
            return False

        try:
            return response.json()["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, ValueError):
            _logger.exception("Invalid OpenAI response payload for advance notifications summary")
            return False
