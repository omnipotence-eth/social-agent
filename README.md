# Social Agent

A powerful social media automation tool built with Python, leveraging AI for content generation and engagement.

## Features

- 🤖 AI-powered content generation using Grok
- 🖼️ Image generation with Stable Diffusion
- 📊 Analytics and performance tracking
- 🔄 Automated interactions and engagement
- 📈 Trend monitoring and analysis
- 🔒 Secure credential management
- 📝 Comprehensive logging and monitoring

## Prerequisites

- Docker and Docker Compose
- API keys for:
  - X (Twitter)
  - Grok
  - Modal
  - SerpAPI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/social-agent.git
cd social-agent
```

2. Create a `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` with your credentials:
```env
# Add your API keys and credentials
X_API_KEY=your_key
X_API_SECRET=your_secret
X_ACCESS_TOKEN=your_token
X_ACCESS_TOKEN_SECRET=your_token_secret
GROK_API_KEY=your_grok_key
MODAL_API_KEY=your_modal_key
SERPAPI_API_KEY=your_serpapi_key
```

4. Start the services:
```bash
docker-compose up -d --build
```

## Accessing the Dashboard

The monitoring dashboard is available at:
```
http://localhost:3000
```

Default credentials:
- Username: admin
- Password: admin

## Project Structure

```
social-agent/
├── main.py              # Main application entry point
├── content_generator.py # AI content generation
├── image_generator.py   # Image generation
├── x_api_client.py     # Twitter API client
├── database.py         # MongoDB operations
├── analytics.py        # Analytics tracking
├── monitoring.py       # System monitoring
├── utils.py           # Utility functions
├── config.py          # Configuration management
├── docker-compose.yml # Docker configuration
└── Dockerfile         # Application container setup
```

## Security

- API keys are stored securely using environment variables
- Sensitive files are excluded from version control
- MongoDB runs in a secure container
- All API calls are rate-limited
- Input sanitization for all user data

## Monitoring

- System metrics collection
- API call tracking
- Performance monitoring
- Error tracking and alerting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Grok AI for content generation
- Stable Diffusion for image generation
- MongoDB for data storage
- Twitter (X) for platform access 