"""Auth service for authentication business logic."""
from datetime import datetime, timedelta, timezone
from typing import Optional
import pyotp

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.repositories import (
    UserRepository,
    RoleRepository,
    UserRoleRepository,
    SessionRepository,
    TotpRepository,
    PasswordResetRepository,
)
from app.modules.auth.models import User, UserStatus, Role, Session, TotpSecret, PasswordReset
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.user_role_repo = UserRoleRepository(session)
        self.session_repo = SessionRepository(session)
        self.totp_repo = TotpRepository(session)
        self.password_reset_repo = PasswordResetRepository(session)

    async def register(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
    ) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        default_role = await self.role_repo.get_by_name("producer")
        if not default_role:
            default_role = await self.role_repo.get_by_name("user")
        
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            phone=phone,
            city=city,
            status=UserStatus.ACTIVE,
        )
        user = await self.user_repo.create(user)

        if default_role:
            await self.user_role_repo.assign_role(user.id, default_role.id)

        await self.session.commit()
        return user

    async def authenticate(
        self,
        email: str,
        password: str,
        totp_code: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> tuple[User, str, str]:
        user = await self.user_repo.get_by_email_with_password(email)
        if not user:
            raise ValueError("Invalid credentials")

        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account is not active")

        if user.locked_until and user.locked_until > datetime.utcnow():
            raise ValueError("Account temporarily locked")

        if not verify_password(password, user.hashed_password):
            await self.user_repo.increment_failed_attempts(user)
            
            if user.failed_login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOGIN_BLOCK_MINUTES)
                await self.session.flush()
            
            await self.session.commit()
            raise ValueError("Invalid credentials")

        if user.totp_enabled:
            if not totp_code:
                raise ValueError("TOTP code required")
            
            totp_secret = await self.totp_repo.get_by_user_id(user.id)
            if not totp_secret or not pyotp.TOTP(totp_secret.secret).verify(totp_code):
                raise ValueError("Invalid TOTP code")

        await self.user_repo.reset_failed_attempts(user)

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        session_obj = Session(
            user_id=user.id,
            refresh_token_hash=hash_password(refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        await self.session_repo.create(session_obj)

        await self.session.commit()
        return user, access_token, refresh_token

    async def refresh_tokens(
        self,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> tuple[str, str]:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            user_id = int(payload["sub"])
        except Exception:
            raise ValueError("Invalid refresh token")

        session_obj = await self.session_repo.get_by_refresh_token_hash(
            hash_password(refresh_token)
        )
        if not session_obj or session_obj.revoked or session_obj.expires_at < datetime.utcnow():
            raise ValueError("Invalid or expired refresh token")

        user = await self.user_repo.get_by_id(user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise ValueError("User not found or inactive")

        await self.session_repo.revoke(session_obj)

        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        new_session = Session(
            user_id=user.id,
            refresh_token_hash=hash_password(new_refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        await self.session_repo.create(new_session)

        await self.session.commit()
        return new_access_token, new_refresh_token

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                return
        except Exception:
            return

        session_obj = await self.session_repo.get_by_refresh_token_hash(
            hash_password(refresh_token)
        )
        if session_obj:
            await self.session_repo.revoke(session_obj)
            await self.session.commit()

    async def logout_all(self, user_id: int) -> None:
        await self.session_repo.revoke_all_user_sessions(user_id)
        await self.session.commit()

    async def request_password_reset(self, email: str) -> Optional[str]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None

        import secrets
        token = secrets.token_urlsafe(32)
        token_hash = hash_password(token)

        reset = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        await self.password_reset_repo.create(reset)
        await self.session.commit()
        return token

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        token_hash = hash_password(token)
        reset = await self.password_reset_repo.get_valid_by_token_hash(token_hash)
        if not reset:
            return False

        user = await self.user_repo.get_by_id(reset.user_id)
        if not user:
            return False

        user.hashed_password = hash_password(new_password)
        await self.password_reset_repo.mark_used(reset)
        await self.session_repo.revoke_all_user_sessions(user.id)
        await self.session.commit()
        return True

    async def enable_totp(self, user_id: int) -> tuple[str, list[str]]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        existing = await self.totp_repo.get_by_user_id(user_id)
        if existing:
            raise ValueError("TOTP already enabled")

        secret = pyotp.random_base32()
        totp = TotpSecret(
            user_id=user_id,
            secret=secret,
        )
        await self.totp_repo.create(totp)

        backup_codes = [secrets.token_urlsafe(8) for _ in range(10)]
        totp.backup_codes = ",".join(backup_codes)
        await self.totp_repo.update(totp)

        user.totp_enabled = True
        await self.user_repo.update(user)
        await self.session.commit()

        return secret, backup_codes

    async def disable_totp(self, user_id: int, totp_code: str) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.totp_enabled:
            return False

        totp_secret = await self.totp_repo.get_by_user_id(user_id)
        if not totp_secret or not pyotp.TOTP(totp_secret.secret).verify(totp_code):
            return False

        await self.totp_repo.delete(user_id)
        user.totp_enabled = False
        await self.user_repo.update(user)
        await self.session.commit()
        return True

    async def verify_totp(self, user_id: int, code: str) -> bool:
        totp_secret = await self.totp_repo.get_by_user_id(user_id)
        if not totp_secret:
            return False
        return pyotp.TOTP(totp_secret.secret).verify(code)

    async def get_totp_uri(self, user_id: int) -> Optional[str]:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.totp_enabled:
            return None
        totp_secret = await self.totp_repo.get_by_user_id(user_id)
        if not totp_secret:
            return None
        return pyotp.TOTP(totp_secret.secret).provisioning_uri(
            user.email, issuer_name=settings.TOTP_ISSUER
        )