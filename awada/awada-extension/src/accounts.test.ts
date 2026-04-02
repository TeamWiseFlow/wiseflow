import { describe, expect, it } from "vitest";
import {
  listAwadaAccountIds,
  resolveAwadaAccount,
  resolveDefaultAwadaAccountId,
} from "./accounts.js";
import type { ClawdbotConfig } from "openclaw/plugin-sdk/feishu";

function makeConfig(awada?: Record<string, unknown>): ClawdbotConfig {
  return { channels: awada !== undefined ? { awada } : undefined } as ClawdbotConfig;
}

describe("resolveAwadaAccount", () => {
  it("returns default values when no awada config is present", () => {
    const account = resolveAwadaAccount({ cfg: makeConfig() });
    expect(account.accountId).toBe("default");
    expect(account.enabled).toBe(true);
    expect(account.configured).toBe(false);
    expect(account.redisUrl).toBeUndefined();
    expect(account.lane).toBe("user");
    expect(account.consumerGroup).toBe("openclaw");
    expect(account.consumerName).toBe("openclaw_bot");
  });

  it("resolves redisUrl and marks configured=true", () => {
    const account = resolveAwadaAccount({
      cfg: makeConfig({ redisUrl: "redis://localhost:6379" }),
    });
    expect(account.configured).toBe(true);
    expect(account.redisUrl).toBe("redis://localhost:6379");
  });

  it("trims whitespace from redisUrl", () => {
    const account = resolveAwadaAccount({
      cfg: makeConfig({ redisUrl: "  redis://localhost:6379  " }),
    });
    expect(account.redisUrl).toBe("redis://localhost:6379");
  });

  it("marks configured=false for empty redisUrl string", () => {
    const account = resolveAwadaAccount({ cfg: makeConfig({ redisUrl: "  " }) });
    expect(account.configured).toBe(false);
    expect(account.redisUrl).toBeUndefined();
  });

  it("respects enabled=false", () => {
    const account = resolveAwadaAccount({
      cfg: makeConfig({ enabled: false, redisUrl: "redis://localhost" }),
    });
    expect(account.enabled).toBe(false);
  });

  it("defaults enabled to true when not set", () => {
    const account = resolveAwadaAccount({
      cfg: makeConfig({ redisUrl: "redis://localhost" }),
    });
    expect(account.enabled).toBe(true);
  });

  it("uses custom lane when provided", () => {
    const account = resolveAwadaAccount({
      cfg: makeConfig({ lane: "cs" }),
    });
    expect(account.lane).toBe("cs");
  });

  it("uses custom consumerGroup and consumerName", () => {
    const account = resolveAwadaAccount({
      cfg: makeConfig({ consumerGroup: "my-group", consumerName: "worker-1" }),
    });
    expect(account.consumerGroup).toBe("my-group");
    expect(account.consumerName).toBe("worker-1");
  });

  it("uses provided accountId", () => {
    const account = resolveAwadaAccount({ cfg: makeConfig(), accountId: "custom-id" });
    expect(account.accountId).toBe("custom-id");
  });

  it("trims and falls back to default when accountId is blank", () => {
    const account = resolveAwadaAccount({ cfg: makeConfig(), accountId: "  " });
    expect(account.accountId).toBe("default");
  });
});

describe("listAwadaAccountIds", () => {
  it("always returns [default]", () => {
    expect(listAwadaAccountIds({} as ClawdbotConfig)).toEqual(["default"]);
  });
});

describe("resolveDefaultAwadaAccountId", () => {
  it("always returns default", () => {
    expect(resolveDefaultAwadaAccountId({} as ClawdbotConfig)).toBe("default");
  });
});
