"""Persistence-backed karma management."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, List

from ..config_models import KarmaConfig


@dataclass
class KarmaProfile:
    """Represents accumulated karma and current role for a user."""

    username: str
    karma: int = 0
    role: str = ""

    def to_dict(self) -> Dict[str, int | str]:
        payload = asdict(self)
        payload["karma"] = int(self.karma)
        payload["role"] = str(self.role)
        return payload


class KarmaManager:
    """Manage karma balances and promotions based on configurable thresholds."""

    def __init__(self, config: KarmaConfig) -> None:
        self.config = config
        self._profiles: Dict[str, KarmaProfile] = self._load_profiles()

    def award(self, username: str, points: int) -> KarmaProfile:
        """Award (or deduct) karma and persist the updated profile."""

        if points == 0:
            return self.get_profile(username)

        if username not in self._profiles:
            self._profiles[username] = KarmaProfile(
                username=username,
                karma=0,
                role=self.config.default_role,
            )

        profile = self._profiles[username]
        profile.karma = max(0, profile.karma + points)
        profile.role = self._resolve_role(profile.karma)
        self._profiles[username] = profile
        self._write_profiles()
        return profile

    def get_profile(self, username: str) -> KarmaProfile:
        """Return the current profile, resolving the role for the existing karma."""

        profile = self._profiles.get(username)
        if profile is None:
            return KarmaProfile(
                username=username,
                karma=0,
                role=self.config.default_role,
            )

        profile.role = self._resolve_role(profile.karma)
        return profile

    def list_profiles(self) -> List[KarmaProfile]:
        """Return all known profiles sorted by karma descending."""

        profiles = list(self._profiles.values())
        for profile in profiles:
            profile.role = self._resolve_role(profile.karma)
        return sorted(profiles, key=lambda profile: profile.karma, reverse=True)

    def _load_profiles(self) -> Dict[str, KarmaProfile]:
        path = self.config.storage_path
        if not path.exists():
            return {}

        raw = json.loads(path.read_text(encoding="utf-8"))
        profiles: Dict[str, KarmaProfile] = {}
        for username, payload in raw.items():
            karma_value = int(payload.get("karma", 0))
            profile = KarmaProfile(
                username=username,
                karma=max(0, karma_value),
                role=self._resolve_role(karma_value),
            )
            profiles[username] = profile
        return profiles

    def _write_profiles(self) -> None:
        path = self.config.storage_path
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {username: profile.to_dict() for username, profile in self._profiles.items()}
        tmp_path = path.parent / f".{path.name}.tmp"
        tmp_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _resolve_role(self, karma: int) -> str:
        thresholds = sorted(self.config.thresholds.items(), key=lambda item: item[1])
        eligible_roles: List[str] = [
            role for role, threshold in thresholds if karma >= threshold
        ]
        if not eligible_roles:
            return self.config.default_role
        return eligible_roles[-1]

