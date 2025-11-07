from .article import (
    ArticleServiceDep,
    BodyCreateArticle,
    BodyUpdateArticle,
    create_article_ctrl,
)
from .board import BoardServiceDep, BodyCreateBoard, BodyUpdateBoard
from .bot import BodySendMessageToID, BotServiceDep
from .comment import BodyCreateComment, BodyUpdateComment, CommentServiceDep
from .file import FileServiceDep
from .key_value import KvServiceDep, KvUpdateBody
from .pig import (
    BodyCreatePIG,
    BodyUpdatePIG,
    create_pig_ctrl,
    handover_pig_ctrl,
    update_pig_ctrl,
)
from .scsc import (
    ctrl_status_available,
    map_semester_name,
    update_scsc_global_status_ctrl,
)
from .sig import (
    BodyCreateSIG,
    BodyUpdateSIG,
    create_sig_ctrl,
    handover_sig_ctrl,
    update_sig_ctrl,
)
from .user import (
    BodyCreateUser,
    ProcessDepositResult,
    create_user_ctrl,
    enroll_user_ctrl,
    process_deposit_ctrl,
    process_oldboy_applicant_ctrl,
    reactivate_oldboy_ctrl,
    register_oldboy_applicant_ctrl,
    verify_enroll_user_ctrl,
)
