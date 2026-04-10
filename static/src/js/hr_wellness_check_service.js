/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, xml, onWillStart } from "@odoo/owl";

/**
 * Invisible component added to the web client to trigger the Wellness Check logic.
 * This is the most stable way to run global logic in Odoo 17/18.
 */
class WellnessPulseTrigger extends Component {
    static template = xml`<div class="o_wellness_pulse_trigger" style="display:none;"></div>`;

    setup() {
        onWillStart(async () => {
            try {
                // We access the actions and RPC via the env services
                const { rpc, action } = this.env.services;

                // Call the backend to see if we should show the prompt today
                const shouldPrompt = await rpc("/web/dataset/call_kw/res.users/check_wellness_prompt", {
                    model: "res.users",
                    method: "check_wellness_prompt",
                    args: [],
                    kwargs: {},
                });

                if (shouldPrompt) {
                    // Trigger the wizard after a tiny delay to allow the dashboard to render first
                    setTimeout(() => {
                        action.doAction("hr_wellness_check.action_hr_wellness_check_wizard");
                    }, 500);
                }
            } catch (err) {
                // Silently catch errors so the main Odoo UI never breaks
                console.warn("Wellness Check automated trigger suppressed an error:", err);
            }
        });
    }
}

// Register as a Main Component so it loads with the web client but doesn't block boot
registry.category("main_components").add("WellnessPulseTrigger", { Component: WellnessPulseTrigger });
