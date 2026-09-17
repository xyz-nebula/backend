import json
import logging
import uuid

import bcrypt
import coloredlogs
import jwt

from fastapi import APIRouter, HTTPException, Request

from app.api.v1.routers.models import UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["Authentication"])