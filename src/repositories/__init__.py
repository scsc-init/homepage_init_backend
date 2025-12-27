from .article import ArticleRepositoryDep
from .attachment import AttachmentRepositoryDep
from .board import BoardRepositoryDep
from .check_user_status_rule import CheckUserStatusRuleRepositoryDep
from .comment import CommentRepositoryDep
from .file_metadata import FileMetadataRepositoryDep
from .key_value import KeyValueRepositoryDep
from .major import MajorRepositoryDep
from .pig import PigMemberRepositoryDep, PigRepositoryDep
from .scsc import SCSCGlobalStatusRepositoryDep
from .sig import SigMemberRepositoryDep, SigRepositoryDep
from .user import (
    OldboyApplicantRepositoryDep,
    StandbyReqTblRepositoryDep,
    UserRepositoryDep,
    UserRoleRepositoryDep,
    get_user_role_level,
)
from .w import WRepositoryDep
