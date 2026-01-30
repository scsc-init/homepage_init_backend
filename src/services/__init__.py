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
from .pig import (
    BodyCreatePIG,
    BodyExecutiveJoinPIG,
    BodyExecutiveLeavePIG,
    BodyHandoverPIG,
    BodyUpdatePIG,
    PigServiceDep,
)
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
from .test_utils import (
    BodyAssignPresident,
    BodyCreateTestUser,
    TestSemesterServiceDep,
    TestUserServiceDep,
)
from .user import (
    BodyCreateUser,
    BodyLogin,
    BodyUpdateMyProfile,
    BodyUpdateUser,
    OldboyServiceDep,
    ProcessDepositResponse,
    ProcessDepositResult,
    ProcessStandbyListManuallyBody,
    ProcessStandbyListResponse,
    ResponseLogin,
    StandbyServiceDep,
    UserService,
    UserServiceDep,
)
from .w import WServiceDep
