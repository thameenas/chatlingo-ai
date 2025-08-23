# ChatLingo AI - Application Overview

This is a **WhatsApp-based language learning bot** that helps Malayalam speakers learn **spoken Kannada** through interactive, scenario-based conversations.

## Core Functionality

**30-Day Learning Journey:**
- Each day focuses on a specific real-life scenario (from `scenarios.json`)
- Scenarios include: "Self Introduction", "Grocery Shopping", "At a Restaurant", etc.
- Progressive difficulty building from simple phrases to full conversations


## Deployment Ready

The app is configured for deployment on Render with:
- **`Procfile`**: Gunicorn WSGI server configuration
- **`render.yaml`**: Render deployment configuration
- **`runtime.txt`**: Python version specification
- **`requirements.txt`**: All dependencies listed 