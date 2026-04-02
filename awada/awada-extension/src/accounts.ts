import { DEFAULT_ACCOUNT_ID } from "openclaw/plugin-sdk/feishu";
import type { ClawdbotConfig } from "openclaw/plugin-sdk/feishu";
import type { AwadaConfig, ResolvedAwadaAccount } from "./types.js";

const DEFAULT_LANE = "user";
const DEFAULT_CONSUMER_GROUP = "openclaw";
const DEFAULT_CONSUMER_NAME = "openclaw_bot";

function getAwadaCfg(cfg: ClawdbotConfig): AwadaConfig | undefined {
  return cfg.channels?.awada as AwadaConfig | undefined;
}

export function resolveAwadaAccount(params: {
  cfg: ClawdbotConfig;
  accountId?: string | null;
}): ResolvedAwadaAccount {
  const awadaCfg = getAwadaCfg(params.cfg);
  const accountId = params.accountId?.trim() || DEFAULT_ACCOUNT_ID;
  const enabled = awadaCfg?.enabled !== false;
  const redisUrl = awadaCfg?.redisUrl?.trim() || undefined;
  const configured = Boolean(redisUrl);

  return {
    accountId,
    enabled,
    configured,
    redisUrl,
    lane: awadaCfg?.lane?.trim() || DEFAULT_LANE,
    platform: awadaCfg?.platform?.trim() || undefined,
    consumerGroup: awadaCfg?.consumerGroup ?? DEFAULT_CONSUMER_GROUP,
    consumerName: awadaCfg?.consumerName ?? DEFAULT_CONSUMER_NAME,
    config: awadaCfg ?? {},
  };
}

export function listAwadaAccountIds(_cfg: ClawdbotConfig): string[] {
  return [DEFAULT_ACCOUNT_ID];
}

export function resolveDefaultAwadaAccountId(_cfg: ClawdbotConfig): string {
  return DEFAULT_ACCOUNT_ID;
}
