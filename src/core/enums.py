from enum import Enum


class RollingAdmission(str, Enum):
    always = "always"
    never = "never"
    during_recruiting_period = "during_recruiting_period"
