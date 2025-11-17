from typing import Final

from .get_from_db import SCSCGlobalStatusDep, get_user_role_level
from .helper import (
    DepositDTO,
    UserDep,
    generate_user_hash,
    get_new_year_semester,
    get_user,
    map_semester_name,
    process_standby_user,
    split_filename,
)
from .logger_config import LOGGING_CONFIG, request_id_var
from .rabbitmq import (
    change_discord_role,
    send_discord_bot_request,
    send_discord_bot_request_no_reply,
)
from .validator import (
    create_uuid,
    is_valid_img_url,
    is_valid_phone,
    is_valid_student_id,
    sha256_hash,
    validate_and_read_file,
)

DELETED: Final[str] = (
    "(삭제됨)"  # used as placeholder for deleted article/comment content
)
