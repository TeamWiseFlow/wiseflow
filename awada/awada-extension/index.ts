import type { OpenClawPluginApi } from "openclaw/plugin-sdk/feishu";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk/feishu";
import { awadaPlugin } from "./src/channel.js";
import { setAwadaRuntime } from "./src/runtime.js";
import { registerCustomerDb, type CustomerDbConfig } from "./src/customerdb.js";

export { monitorAwadaProvider } from "./src/monitor.js";
export { probeAwada } from "./src/probe.js";
export { sendTextToAwada, encodeAwadaTo, decodeAwadaTo } from "./src/send.js";
export { publishTextToAwada } from "./src/publisher.js";
export { awadaPlugin } from "./src/channel.js";

type AwadaPluginConfig = {
  /**
   * When set, activates the built-in CustomerDB feature:
   * injects customer context into LLM prompts and registers silent sales
   * commands (payment_success, club_join).
   *
   * Example openclaw.json:
   *   "plugins": [{
   *     "path": "awada/awada-extension",
   *     "config": {
   *       "customerdb": {
   *         "agentId": "sales-cs",
   *         "workspaceDir": "/home/user/.openclaw/workspace-sales-cs"
   *       }
   *     }
   *   }]
   */
  customerdb?: CustomerDbConfig & { enabled?: boolean };
};

const plugin = {
  id: "awada",
  name: "Awada",
  description: "Awada channel plugin — WeChat via Redis bridge",
  configSchema: emptyPluginConfigSchema(),
  register(api: OpenClawPluginApi) {
    setAwadaRuntime(api.runtime);
    api.registerChannel({ plugin: awadaPlugin });

    const pluginCfg = (api.pluginConfig ?? {}) as AwadaPluginConfig;
    const cdbCfg = pluginCfg.customerdb;
    if (cdbCfg && cdbCfg.enabled !== false && cdbCfg.agentId) {
      registerCustomerDb(api, cdbCfg);
    }
  },
};

export default plugin;
