{
    "name": "Advance Notifications",
    "version": "18.0.1.0.0",
    "depends": ["mail", "web", "bus"],
    "author": "PremaFirm",
    "category": "Tools",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "advance_notifications/static/src/js/systray_notifications.js",
            "advance_notifications/static/src/xml/systray_template.xml",
            "advance_notifications/static/src/scss/style.scss",
        ],
    },
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
