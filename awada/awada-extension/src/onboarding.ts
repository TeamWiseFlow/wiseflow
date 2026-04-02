import type { ChannelSetupWizard, DmPolicy, OpenClawConfig } from "openclaw/plugin-sdk/setup";
import { createTopLevelChannelDmPolicy, DEFAULT_ACCOUNT_ID } from "openclaw/plugin-sdk/setup";
import { probeAwada } from "./probe.js";
import type { AwadaConfig } from "./types.js";

const channel = "awada" as const;

function getAwadaCfg(cfg: OpenClawConfig): AwadaConfig | undefined {
  return cfg.channels?.awada as AwadaConfig | undefined;
}

function isAwadaConfigured(cfg: OpenClawConfig): boolean {
  return Boolean(getAwadaCfg(cfg)?.redisUrl?.trim());
}

function setAwadaAllowFrom(cfg: OpenClawConfig, allowFrom: string[]): OpenClawConfig {
  return {
    ...cfg,
    channels: {
      ...cfg.channels,
      awada: {
        ...getAwadaCfg(cfg),
        allowFrom,
      },
    },
  };
}

const awadaDmPolicy = createTopLevelChannelDmPolicy({
  label: "Awada",
  channel,
  policyKey: "channels.awada.dmPolicy",
  allowFromKey: "channels.awada.allowFrom",
  getCurrent: (cfg) => (getAwadaCfg(cfg)?.dmPolicy ?? "open") as DmPolicy,
  getAllowFrom: (cfg) => getAwadaCfg(cfg)?.allowFrom,
  promptAllowFrom: async ({ cfg, prompter }) => {
    const existing = getAwadaCfg(cfg)?.allowFrom ?? [];
    const entry = await prompter.text({
      message: "Awada allowFrom (user_id_external values, comma-separated)",
      placeholder: "user_123, user_456",
      initialValue: existing.join(", "),
      validate: (value) => (String(value ?? "").trim() ? undefined : "Required"),
    });
    const parts = String(entry)
      .split(/[\n,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    const unique = [...new Set([...existing, ...parts])];
    return setAwadaAllowFrom(cfg, unique);
  },
});

export const awadaSetupWizard: ChannelSetupWizard = {
  channel,
  resolveAccountIdForConfigure: () => DEFAULT_ACCOUNT_ID,
  resolveShouldPromptAccountIds: () => false,
  status: {
    configuredLabel: "configured",
    unconfiguredLabel: "needs Redis URL",
    configuredHint: "configured",
    unconfiguredHint: "needs Redis URL",
    configuredScore: 2,
    unconfiguredScore: 0,
    resolveConfigured: ({ cfg }) => isAwadaConfigured(cfg),
    resolveStatusLines: async ({ cfg, configured }) => {
      const awadaCfg = getAwadaCfg(cfg);
      const redisUrl = awadaCfg?.redisUrl?.trim();
      let probeResult = null;
      if (configured && redisUrl) {
        try {
          probeResult = await probeAwada({ redisUrl });
        } catch {
          // ignore probe errors
        }
      }
      if (!configured) {
        return ["Awada: needs Redis URL"];
      }
      if (probeResult?.ok) {
        return ["Awada: connected to Redis"];
      }
      return ["Awada: configured (connection not verified)"];
    },
    resolveSelectionHint: ({ cfg }) =>
      isAwadaConfigured(cfg) ? "configured" : "needs Redis URL",
    resolveQuickstartScore: ({ cfg }) => (isAwadaConfigured(cfg) ? 2 : 0),
  },
  credentials: [],
  finalize: async ({ cfg, prompter }) => {
    const awadaCfg = getAwadaCfg(cfg);
    const currentUrl = awadaCfg?.redisUrl?.trim() ?? "";

    await prompter.note(
      [
        "Configure awada channel to receive WeChat messages via awada-server Redis bridge.",
        "You need:",
        "  1. A running awada-server that publishes events to Redis Streams",
        "  2. Redis URL (e.g. redis://localhost:6379 or redis://:pass@host:6379)",
        "  3. Lane to subscribe to (default: user)",
        "  4. Platform identifier for proactive sends (e.g. worktool:mybot)",
      ].join("\n"),
      "Awada setup",
    );

    const redisUrl = String(
      await prompter.text({
        message: "Redis URL",
        placeholder: "redis://localhost:6379",
        initialValue: currentUrl,
        validate: (value) => (String(value ?? "").trim() ? undefined : "Required"),
      }),
    ).trim();

    let next: OpenClawConfig = {
      ...cfg,
      channels: {
        ...cfg.channels,
        awada: {
          ...awadaCfg,
          enabled: true,
          redisUrl,
        },
      },
    };

    // Test connection
    try {
      const probe = await probeAwada({ redisUrl });
      if (probe.ok) {
        await prompter.note("Redis connection successful!", "Awada connection test");
      } else {
        await prompter.note(
          `Connection failed: ${probe.error ?? "unknown error"}`,
          "Awada connection test",
        );
      }
    } catch (err) {
      await prompter.note(`Connection test failed: ${String(err)}`, "Awada connection test");
    }

    // Lane configuration
    const currentLane = awadaCfg?.lane?.trim() ?? "user";
    const laneInput = String(
      await prompter.text({
        message: "Lane to subscribe to",
        placeholder: "user",
        initialValue: currentLane,
      }),
    ).trim();
    const resolvedLane = laneInput || "user";
    next = {
      ...next,
      channels: {
        ...next.channels,
        awada: {
          ...(next.channels?.awada as AwadaConfig),
          lane: resolvedLane,
        },
      },
    };

    // Platform configuration (used for proactive sends)
    const currentPlatform = awadaCfg?.platform?.trim() ?? "";
    const platformInput = String(
      await prompter.text({
        message: "Platform identifier for proactive sends (e.g. worktool:mybot)",
        placeholder: "worktool:mybot",
        initialValue: currentPlatform,
      }),
    ).trim();
    if (platformInput) {
      next = {
        ...next,
        channels: {
          ...next.channels,
          awada: {
            ...(next.channels?.awada as AwadaConfig),
            platform: platformInput,
          },
        },
      };
    }

    return { cfg: next };
  },
  dmPolicy: awadaDmPolicy,
  disable: (cfg) => ({
    ...cfg,
    channels: {
      ...cfg.channels,
      awada: { ...getAwadaCfg(cfg), enabled: false },
    },
  }),
};
