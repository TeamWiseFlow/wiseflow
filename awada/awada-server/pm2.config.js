module.exports = {
  apps: [
    {
      name: 'awada-server',
      script: './src/index.ts',
      interpreter: 'ts-node',
      interpreter_args: '-r tsconfig-paths/register',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 8088,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 8088,
      },
    },
  ],
};

