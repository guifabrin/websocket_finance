export default {
    getParam(key) {
        return window.location.search.substring(window.location.search.indexOf(key) + key.length + 1);
    }
}