import { describe, expect, it } from "vitest";
import { validateAwadaRedisUrl } from "./probe.js";

describe("validateAwadaRedisUrl", () => {
  it("accepts standard redis urls", () => {
    expect(validateAwadaRedisUrl("redis://:pass@127.0.0.1:6379/0")).toBeNull();
    expect(validateAwadaRedisUrl("rediss://:pass@redis.example.com:6380/1")).toBeNull();
  });

  it("rejects urls with unsupported protocol", () => {
    expect(validateAwadaRedisUrl("http://127.0.0.1:6379")).toBe(
      "invalid redisUrl protocol (expected redis:// or rediss://)",
    );
  });

  it("rejects malformed urls", () => {
    expect(validateAwadaRedisUrl("not-a-url")).toBe("invalid redisUrl format");
  });

  it("rejects unescaped hash fragment in password", () => {
    expect(validateAwadaRedisUrl("redis://:Aw4d@R3d1s#2025!Sec@121.4.44.143:7601/0")).toBe(
      "invalid redisUrl: found unescaped # fragment; URL-encode password special characters (for example @, #, !, %)",
    );
  });
});
