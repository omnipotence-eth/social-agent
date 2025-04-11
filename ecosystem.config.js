module.exports = {
  apps: [{
    name: 'social-agent',
    script: 'main.py',
    interpreter: 'python3',
    watch: false,
    autorestart: true,
    max_restarts: 10,
    restart_delay: 4000,
    env: {
      PYTHONPATH: '/path/to/social_agent'
    }
  }]
} 