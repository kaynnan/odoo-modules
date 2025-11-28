/** @odoo-module **/

import { Component } from "@odoo/owl";

export class LoyaltyCard extends Component {
    static template = "customer_loyalty.LoyaltyCard";
    static props = {
        points: { type: Number },
        levels: { type: Array },
        loading: { type: Boolean, optional: true },
    };

    get currentLevelInfo() {
        let matchedLevel = this.props.levels[0];
        let colorIndex = 0;

        if (!this.props.levels.length) {
            return { name: "No Level", color: "#6c757d" };
        }

        for (let i = 0; i < this.props.levels.length; i++) {
            const level = this.props.levels[i];
            if (this.props.points >= level.min_points) {
                matchedLevel = level;
                colorIndex = i;
            } else {
                break;
            }
        }

        return {
            name: matchedLevel.name,
            color: this._getColorByIndex(colorIndex),
        };
    }

    _getColorByIndex(index) {
        const colors = ['#CD7F32', '#C0C0C0', '#FFD700', '#00d2d3', '#5f27cd'];
        return colors[index] || '#2e86de';
    }
}