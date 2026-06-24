INSERT INTO key_value (key, value, writing_permission_level)
VALUES
  ('TEXT_DEPOSIT_ACC', '국민은행 942902-02-054136 (강명석)', 500),
  ('TEXT_DISCORD_INVITE_LINK', 'https://discord.gg/SmXFDxA7XE', 500),
  ('TEXT_KAKAO_INVITE_LINK', 'https://invite.kakao.com/tc/II2yiLsQhY', 500)
ON CONFLICT (key) DO NOTHING;
