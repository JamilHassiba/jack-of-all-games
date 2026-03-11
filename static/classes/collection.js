export class Collection {
    constructor() {
        this.collection = {}
    }

    Add(id, object) {
        this.collection[id] = object
    }

    Remove(id) {
        this.collection[id] = null
    }
}