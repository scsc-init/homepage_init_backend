from typing import Final

from .helper import (
    DepositDTO,
    generate_user_hash,
    get_next_year_semester,
    map_semester_name,
    process_standby_user,
    split_filename,
    utcnow,
)
from .logger_config import LOGGING_CONFIG, request_id_var
from .singleton import SingletonMeta
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
