/**
 * WorkTool Koa应用配置
 * 独立的 WorkTool 应用，与 QiweAPI 完全隔离
 */

import Koa from 'koa';
import bodyParser from 'koa-bodyparser';
import webhookRouter from './routes/webhook-worktool';

const app = new Koa();

// 错误处理中间件
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err: any) {
    console.error('[WorkTool-App] 错误:', err);
    ctx.status = err.status || 500;
    ctx.body = {
      code: ctx.status,
      msg: err.message || '服务器内部错误'
    };
  }
});

// 请求日志中间件
app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  console.log(`[WorkTool-App] ${ctx.method} ${ctx.url} - ${ms}ms`);
});

// 解析请求体
app.use(
  bodyParser({
    enableTypes: ['json', 'form', 'text'],
    jsonLimit: '10mb'
  })
);

// 注册 WorkTool Webhook 路由
app.use(webhookRouter.routes());
app.use(webhookRouter.allowedMethods());

// 404处理
app.use(async (ctx) => {
  if (!ctx.body) {
    ctx.status = 404;
    ctx.body = {
      code: 404,
      msg: '接口不存在'
    };
  }
});

export default app;

