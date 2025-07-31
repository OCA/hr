import {SearchBar} from "@web/search/search_bar/search_bar";

export class Many2ManySearchBar extends SearchBar {
    getFieldType(searchItem) {
        const type = super.getFieldType(searchItem);
        const fieldType = type === "many2many" ? "many2one" : type;
        return fieldType;
    }
}
