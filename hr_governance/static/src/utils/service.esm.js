import {registry} from "@web/core/registry";

export const governanceNotificationService = {
    dependencies: ["bus_service", "notification"],

    start(env, {bus_service, notification}) {
        bus_service.subscribe("circle_member_changed", (payload) => {
            notification.add(payload.message, {
                sticky: false,
                title: payload.title,
                type: payload.type,
            });
        });
    },
};

registry
    .category("services")
    .add("governance_notification", governanceNotificationService);
