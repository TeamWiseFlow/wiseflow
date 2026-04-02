/**
 * Koa应用配置
 */

import Koa from 'koa';
import bodyParser from 'koa-bodyparser';
import webhookRouter from './routes/webhook';
import webhookWorkToolRouter from './routes/webhook-worktool';
// import apiRouter from './routes/api';

const app = new Koa();

// 错误处理中间件
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err: any) {
    console.error('[App] 错误:', err);
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
  console.log(`[App] ${ctx.method} ${ctx.url} - ${ms}ms`);
});

// 解析请求体
app.use(
  bodyParser({
    enableTypes: ['json', 'form', 'text'],
    jsonLimit: '10mb'
  })
);

// 注册路由
app.use(webhookRouter.routes());
app.use(webhookRouter.allowedMethods());
// 注册 WorkTool Webhook 路由
app.use(webhookWorkToolRouter.routes());
app.use(webhookWorkToolRouter.allowedMethods());
// app.use(apiRouter.routes());
// app.use(apiRouter.allowedMethods());

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
