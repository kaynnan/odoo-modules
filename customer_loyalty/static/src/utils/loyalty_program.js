/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { useState, onWillStart } from "@odoo/owl";

export function useLoyaltyProgram() {
    const orm = useService("orm");
    const state = useState({
        levels: [],
        loading: true,
    });

    onWillStart(async () => {
        state.levels = await orm.searchRead(
            "loyalty.level",
            [],
            ["name", "min_points"],
            { order: "min_points asc" }
        );
        state.loading = false;
    });

    return state;
}