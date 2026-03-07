path = "/app/.venv/lib/python3.12/site-packages/mcp/server/auth/handlers/register.py"
with open(path) as f:
    src = f.read()

# Patch 1: grant_types — auto-add refresh_token if missing
old1 = '        if not {"authorization_code", "refresh_token"}.issubset(set(client_metadata.grant_types)):'
new1 = (
    '        if "authorization_code" in client_metadata.grant_types'
    ' and "refresh_token" not in client_metadata.grant_types:\n'
    '            client_metadata.grant_types = list(client_metadata.grant_types) + ["refresh_token"]\n'
    '        if not {"authorization_code", "refresh_token"}.issubset(set(client_metadata.grant_types)):'
)
patched = src.replace(old1, new1, 1)
assert patched != src, "Patch 1 (grant_types) not found — patch failed"

# Patch 2: scope — ignore unknown scopes instead of rejecting
old2 = (
    '        elif client_metadata.scope is not None and self.options.valid_scopes is not None:\n'
    '            requested_scopes = set(client_metadata.scope.split())\n'
    '            valid_scopes = set(self.options.valid_scopes)\n'
    '            if not requested_scopes.issubset(valid_scopes):  # pragma: no branch\n'
    '                return PydanticJSONResponse(\n'
    '                    content=RegistrationErrorResponse(\n'
    '                        error="invalid_client_metadata",\n'
    '                        error_description="Requested scopes are not valid: "\n'
    '                        f"{\', \'.join(requested_scopes - valid_scopes)}",\n'
    '                    ),\n'
    '                    status_code=400,\n'
    '                )'
)
new2 = (
    '        elif client_metadata.scope is not None and self.options.valid_scopes is not None:\n'
    '            requested_scopes = set(client_metadata.scope.split())\n'
    '            valid_scopes = set(self.options.valid_scopes)\n'
    '            # Allow unknown scopes: filter to only known scopes\n'
    '            client_metadata.scope = " ".join(requested_scopes & valid_scopes) or " ".join(valid_scopes)'
)
patched2 = patched.replace(old2, new2, 1)
assert patched2 != patched, "Patch 2 (scope) not found — patch failed"

with open(path, "w") as f:
    f.write(patched2)
print("Patched OK (grant_types + scope)")

# Patch 3: consent.py — filter upstream scopes to only GitHub-known scopes
# Prevents Claude.ai's "claudeai" scope from being forwarded to GitHub
consent_path = "/app/.venv/lib/python3.12/site-packages/fastmcp/server/auth/oauth_proxy/consent.py"
with open(consent_path) as f:
    consent_src = f.read()

old3 = "        scopes_to_use = transaction.get(\"scopes\") or self.required_scopes or []"
new3 = (
    "        _all_scopes = transaction.get(\"scopes\") or self.required_scopes or []\n"
    "        _known_scopes = set(self.required_scopes or [])\n"
    "        scopes_to_use = [s for s in _all_scopes if s in _known_scopes] or list(_known_scopes) or _all_scopes"
)
patched3 = consent_src.replace(old3, new3, 1)
assert patched3 != consent_src, "Patch 3 (upstream scope filter) not found — patch failed"
with open(consent_path, "w") as f:
    f.write(patched3)
print("Patched OK (upstream scope filter in consent.py)")

# Patch 4: mcp/shared/auth.py — validate_scope: unknown scopes filtered instead of rejected
# Claude.ai sends scope=user+claudeai in /authorize, but CIMD client is registered with scope=user only.
# The default strict check raises InvalidScopeError, aborting the flow before GitHub is reached.
auth_path = "/app/.venv/lib/python3.12/site-packages/mcp/shared/auth.py"
with open(auth_path) as f:
    auth_src = f.read()

old4 = (
    '        requested_scopes = requested_scope.split(" ")\n'
    '        allowed_scopes = [] if self.scope is None else self.scope.split(" ")\n'
    '        for scope in requested_scopes:\n'
    '            if scope not in allowed_scopes:  # pragma: no branch\n'
    '                raise InvalidScopeError(f"Client was not registered with scope {scope}")\n'
    '        return requested_scopes  # pragma: no cover'
)
new4 = (
    '        requested_scopes = requested_scope.split(" ")\n'
    '        allowed_scopes = [] if self.scope is None else self.scope.split(" ")\n'
    '        # Filter unknown scopes instead of rejecting (Claude.ai sends extra scopes like "claudeai")\n'
    '        filtered = [s for s in requested_scopes if s in allowed_scopes]\n'
    '        return filtered if filtered else None'
)
patched4 = auth_src.replace(old4, new4, 1)
assert patched4 != auth_src, "Patch 4 (validate_scope filter) not found — patch failed"
with open(auth_path, "w") as f:
    f.write(patched4)
print("Patched OK (validate_scope filter in mcp/shared/auth.py)")
