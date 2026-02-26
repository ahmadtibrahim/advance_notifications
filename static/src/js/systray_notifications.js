/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class AdvanceNotifications extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.bus = useService("bus_service");

        this.state = useState({
            notifications: [],
            open: false,
        });

        this.bus.addChannel("advance_notifications_channel");
        this.bus.addEventListener("notification", ({ detail }) => {
            for (const notif of detail) {
                if (notif.type === "advance_notifications_channel") {
                    this.loadNotifications();
                    this.playSound();
                }
            }
        });

        onWillStart(async () => {
            await this.loadNotifications();
        });
    }

    async loadNotifications() {
        this.state.notifications = await this.orm.searchRead(
            "advance.notification",
            [["is_done", "=", false]],
            ["ai_summary", "model", "res_id"],
            { limit: 10 }
        );
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    async markDone(id) {
        await this.orm.write("advance.notification", [id], { is_done: true });
        await this.loadNotifications();
    }

    openRecord(model, res_id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            res_id,
            views: [[false, "form"]],
        });
    }

    playSound() {
        const audio = new Audio("/advance_notifications/static/src/sound/notify.mp3");
        audio.volume = 0.2;
        audio.play().catch(() => {});
    }
}

AdvanceNotifications.template = "advance_notifications.Template";

registry.category("systray").add("advance_notifications", {
    Component: AdvanceNotifications,
});
