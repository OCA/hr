// @odoo-module
import {registry} from "@web/core/registry";
import {user} from "@web/core/user";

/**
 * Ask the server once per web client load whether the current user should see
 * today's horoscope. The server answers at most once a day, and only when the
 * user enabled the option and their birth data is complete.
 */
export const dailyHoroscopeService = {
    dependencies: ["notification", "orm"],
    start(env, {notification, orm}) {
        if (!user.isInternalUser) {
            return;
        }
        env.bus.addEventListener(
            "WEB_CLIENT_READY",
            async () => {
                const horoscope = await orm.silent.call(
                    "res.users",
                    "get_daily_horoscope",
                    []
                );
                if (horoscope) {
                    notification.add(horoscope.message, {
                        title: horoscope.title,
                        type: "info",
                    });
                }
            },
            {once: true}
        );
    },
};

registry
    .category("services")
    .add("hr_birth_astral_chart.daily_horoscope", dailyHoroscopeService);
