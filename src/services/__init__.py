from .article import (
    ArticleServiceDep,
    BodyCreateArticle,
    BodyUpdateArticle,
)
from .board import BoardServiceDep, BodyCreateBoard, BodyUpdateBoard
from .bot import BodySendMessageToID, BotServiceDep
from .comment import BodyCreateComment, BodyUpdateComment, CommentServiceDep
from .file import FileServiceDep
from .key_value import KvServiceDep, KvUpdateBody
from .major import BodyCreateMajor, MajorServiceDep
from .scsc import (
    BodyUpdateSCSCGlobalStatus,
    SCSCServiceDep,
    ctrl_status_available,
    map_semester_name,
)
from .sig import (
    BodyCreateSIG,
    BodyExecutiveJoinSIG,
    BodyExecutiveLeaveSIG,
    BodyHandoverSIG,
    BodyUpdateSIG,
    SigServiceDep,
)
from .test_utils import BodyCreateTestUser, TestUserServiceDep
from .user import (
    BodyCreateExternalMemberApplication,
    BodyCreateUser,
    BodyLogin,
    BodyUpdateMyProfile,
    BodyUpdateUser,
    ExternalMemberServiceDep,
    OldboyServiceDep,
    ProcessDepositResponse,
    ProcessDepositResult,
    ProcessStandbyListManuallyBody,
    ProcessStandbyListResponse,
    ResponseLogin,
    StandbyServiceDep,
    UserActivityLogResponse,
    UserService,
    UserServiceDep,
)
from .w import WServiceDep
