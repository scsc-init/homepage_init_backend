from typing import Final

from .validator import sha256_hash, create_uuid, is_valid_phone, is_valid_student_id, is_valid_year, is_valid_semester, is_valid_img_url
from .helper import get_file_extension, get_user, process_standby_user, DepositDTO
from .get_from_db import get_user_role_level, SCSCGlobalStatusDep
from .rabbitmq import send_discord_bot_request, send_discord_bot_request_no_reply, change_discord_role
from .logger_config import LOGGING_CONFIG, request_id_var
from .config_keys import FOOTER_MESSAGE_KEY

DELETED: Final[str] = "(삭제됨)"  # used as placeholder for deleted article/comment content
