// Pass the Permissions Test.
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === "notifications"
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);
Object.defineProperty(navigator, "webdriver", {
    get: () => undefined,
});
window.navigator.chrome = {
    runtime: {},
    // Add other properties if necessary
};
Object.defineProperty(document, "hidden", {
    get: () => false,
});
Object.defineProperty(document, "visibilityState", {
    get: () => "visible",
});
