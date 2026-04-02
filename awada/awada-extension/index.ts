import type { OpenClawPluginApi } from "openclaw/plugin-sdk/feishu";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk/feishu";
import { awadaPlugin } from "./src/channel.js";
import { setAwadaRuntime } from "./src/runtime.js";

export { monitorAwadaProvider } from "./src/monitor.js";
export { probeAwada } from "./src/probe.js";
export { sendTextToAwada, encodeAwadaTo, decodeAwadaTo } from "./src/send.js";
export { publishTextToAwada } from "./src/publisher.js";
export { awadaPlugin } from "./src/channel.js";

const plugin = {
  id: "awada",
  name: "Awada",
  description: "Awada channel plugin — WeChat via Redis bridge",
  configSchema: emptyPluginConfigSchema(),
  register(api: OpenClawPluginApi) {
    setAwadaRuntime(api.runtime);
    api.registerChannel({ plugin: awadaPlugin });
  },
};

export default plugin;
