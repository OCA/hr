// NOTE: add mechanism to handle circular references when traversing
export function isEquals(o1, o2, o1Refs, o2Refs) {
    const _o1Refs = o1Refs || [];
    const _o2Refs = o2Refs || [];

    if (o1 === o2) return true;
    if ((o1 && !o2) || (o2 && !o1)) return false;
    if (typeof o1 !== typeof o2) return false;
    if (typeof o1 !== "object") return false;

    // Keep track of the references
    // make sure both circular references point to the same part of the history
    const o1RefIndex = _o1Refs.indexOf(o1);
    const o2RefIndex = _o2Refs.indexOf(o2);

    if (o1RefIndex === o2RefIndex && o1RefIndex >= 0) return true;
    _o1Refs.push(o1);
    _o2Refs.push(o2);

    // Objects can have different keys if the values are undefined
    for (const key in o2) {
        if (!(key in o1) && o2[key] !== undefined) {
            return false;
        }
    }
    for (const key in o1) {
        if (typeof o1[key] !== typeof o2[key]) return false;
        if (typeof o1[key] === "object") {
            if (!isEquals(o1[key], o2[key], _o1Refs.slice(), _o2Refs.slice()))
                return false;
        } else if (o1[key] !== o2[key]) return false;
    }
    return true;
}

// From @spreadsheet/helpers/helpers
export function isEmpty(item) {
    if (!item) {
        return true;
    }
    if (typeof item === "object") {
        if (
            Object.values(item).length === 0 ||
            Object.values(item).every((val) => val === undefined)
        ) {
            return true;
        }
    }
    return false;
}
