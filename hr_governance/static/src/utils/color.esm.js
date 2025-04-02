/** @odoo-module **/

const COLORS = [
    "#FFFFFF",
    "#D0D1D3",
    "#b3ffc5",
    "#b9f0ff",
    "#c9d9cb",
    "#e0f9ff",
    "#e9ccff",
    "#eaecc1",
    "#f5d9d9",
    "#fcffbe",
    "#ffe1a5",
    "#ffccca",
    "#a5d6ff",
];

/**
 * @param {Object} node
 * @returns {String}
 */
export function getColor(node) {
    const color = node.data?.color;
    if (color) {
        return COLORS[color - 1];
    }
    return COLORS[Math.floor(Math.random() * COLORS.length)];
}
