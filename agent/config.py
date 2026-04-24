"""Agent configuration — AWS profiles, regions, endpoints."""

import os

from dotenv import load_dotenv

load_dotenv()

# AWS
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
AWS_PROFILE_CODECOMMIT = os.getenv("AWS_PROFILE_CODECOMMIT", "saml")
AWS_PROFILE_SSM = os.getenv("AWS_PROFILE_SSM", "sia-nonprod-auto2")

# Demo target
DEMO_EC2_INSTANCE_ID = os.getenv("DEMO_EC2_INSTANCE_ID", "")
DEMO_EC2_ENDPOINT = os.getenv("DEMO_EC2_ENDPOINT", "")
DEMO_CODECOMMIT_REPO = os.getenv("DEMO_CODECOMMIT_REPO", "demo-app")
DEMO_CODECOMMIT_BRANCH = os.getenv("DEMO_CODECOMMIT_BRANCH", "eugene")

# API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GENSPARK_API_KEY = os.getenv("GENSPARK_API_KEY", "")

# Paths
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
