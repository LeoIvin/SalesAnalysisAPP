# AnalysisAPP - Deployment Guide

This guide explains how to deploy the AnalysisAPP Django backend to Render.com using the existing Supabase PostgreSQL database.

## Prerequisites

- A Render.com account
- Your existing Supabase PostgreSQL database
- Git repository with your code

## Deployment Steps

### 1. Push Your Code to a Git Repository

Make sure your code is in a Git repository (GitHub, GitLab, etc.) as Render deploys directly from Git.

### 2. Create a New Web Service on Render

1. Log in to your Render dashboard
2. Click on "New" and select "Web Service"
3. Connect your Git repository
4. Configure the service with the following settings:
   - **Name**: Choose a name for your service (e.g., datusanalysis)
   - **Environment**: Python
   - **Region**: Choose a region close to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn AnalysisAPP.wsgi:application`

### 3. Configure Environment Variables

Add the following environment variables in the Render dashboard:

- `SECRET_KEY`: Your Django secret key
- `DEBUG`: Set to 'False' for production
- `ALLOWED_HOSTS`: Add your Render domain (e.g., datusanalysis.onrender.com)
- `DATABASE_URL`: Your Supabase PostgreSQL connection string
- `RENDER_EXTERNAL_HOSTNAME`: Your Render domain (e.g., datusanalysis.onrender.com)

Alternatively, you can set individual database variables:
- `DB_NAME`: Your database name (postgres)
- `DB_USER`: Your database user
- `DB_PASSWORD`: Your database password
- `DB_HOST`: Your Supabase host
- `DB_PORT`: Your Supabase port

### 4. Deploy

Click "Create Web Service" and Render will start the deployment process. This may take a few minutes.

## Checking Your Deployment

Once deployed, you can access your API at the URL provided by Render (e.g., https://datusanalysis.onrender.com/).

## Troubleshooting

- Check the Render logs for any deployment errors
- Ensure your database credentials are correct
- Verify that all required environment variables are set

## Additional Information

- The `build.sh` script handles installing dependencies, collecting static files, and running migrations
- The `Procfile` tells Render how to run your application
- WhiteNoise is configured to serve static files efficiently in production