"""RunwayZero Agent — AI-Powered Vulnerability Impact Agent."""

import os

from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
AWS_PROFILE_CODECOMMIT = os.getenv("AWS_PROFILE_CODECOMMIT", "saml")
AWS_PROFILE_SSM = os.getenv("AWS_PROFILE_SSM", "sia-nonprod-auto2")
