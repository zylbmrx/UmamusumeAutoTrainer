import time
from enum import Enum


class ScenarioType(Enum):
    SCENARIO_TYPE_UNKNOWN = 0
    SCENARIO_TYPE_URA = 1


class SupportCardType(Enum):
    SUPPORT_CARD_TYPE_UNKNOWN = 0
    SUPPORT_CARD_TYPE_SPEED = 1
    SUPPORT_CARD_TYPE_STAMINA = 2
    SUPPORT_CARD_TYPE_POWER = 3
    SUPPORT_CARD_TYPE_WILL = 4
    SUPPORT_CARD_TYPE_INTELLIGENCE = 5
    SUPPORT_CARD_TYPE_FRIEND = 6
    SUPPORT_CARD_TYPE_GROUP = 7
    SUPPORT_CARD_TYPE_NPC = 10


class SupportCardFavorLevel(Enum):
    SUPPORT_CARD_FAVOR_LEVEL_UNKNOWN = 0
    SUPPORT_CARD_FAVOR_LEVEL_1 = 1
    SUPPORT_CARD_FAVOR_LEVEL_2 = 2
    SUPPORT_CARD_FAVOR_LEVEL_3 = 3
    SUPPORT_CARD_FAVOR_LEVEL_4 = 4


class TrainingType(Enum):
    TRAINING_TYPE_UNKNOWN = 0
    TRAINING_TYPE_SPEED = 1
    TRAINING_TYPE_STAMINA = 2
    TRAINING_TYPE_POWER = 3
    TRAINING_TYPE_WILL = 4
    TRAINING_TYPE_INTELLIGENCE = 5


class TrainingTry:
    training_type_dict = {
    }

    training_try_count_dict = {
    }

    max_try_time = 5
    try_sleep_time = 0.5

    def __init__(self, training_type: TrainingType):
        self.training_type_dict = {TrainingType.TRAINING_TYPE_SPEED: False, TrainingType.TRAINING_TYPE_STAMINA: False,
                                   TrainingType.TRAINING_TYPE_POWER: False, TrainingType.TRAINING_TYPE_WILL: False,
                                   TrainingType.TRAINING_TYPE_INTELLIGENCE: False, training_type: True}

        self.training_try_count_dict = {
            TrainingType.TRAINING_TYPE_SPEED: 0,
            TrainingType.TRAINING_TYPE_STAMINA: 0,
            TrainingType.TRAINING_TYPE_POWER: 0,
            TrainingType.TRAINING_TYPE_WILL: 0,
            TrainingType.TRAINING_TYPE_INTELLIGENCE: 0,
        }

    def needBreak(self):
        return self.isAllSuccess() or sum(self.training_try_count_dict.values()) >= (
                self.max_try_time * (len(self.training_try_count_dict) - 1))

    def success(self, training_type: TrainingType):
        self.training_type_dict[training_type] = True

    def isAllSuccess(self):
        for k, v in self.training_type_dict.items():
            if v is False:
                return False
        return True




class MotivationLevel(Enum):
    MOTIVATION_LEVEL_UNKNOWN = 0
    MOTIVATION_LEVEL_1 = 1
    MOTIVATION_LEVEL_2 = 2
    MOTIVATION_LEVEL_3 = 3
    MOTIVATION_LEVEL_4 = 4
    MOTIVATION_LEVEL_5 = 5


class TurnOperationType(Enum):
    TURN_OPERATION_TYPE_UNKNOWN = 0
    TURN_OPERATION_TYPE_TRAINING = 1
    TURN_OPERATION_TYPE_REST = 2
    TURN_OPERATION_TYPE_MEDIC = 3
    TURN_OPERATION_TYPE_TRIP = 4
    TURN_OPERATION_TYPE_RACE = 5


class SupportCardUma(Enum):
    SUPPORT_CARD_UMA_UNKNOWN = 0
    SUPPORT_CARD_UMA_AKIKAWA = 1
    SUPPORT_CARD_UMA_REPORTER = 2


class RaceTacticType(Enum):
    RACE_TACTIC_TYPE_UNKNOWN = 0
    RACE_TACTIC_TYPE_BACK = 1
    RACE_TACTIC_TYPE_MIDDLE = 2
    RACE_TACTIC_TYPE_FRONT = 3
    RACE_TACTIC_TYPE_ESCAPE = 4
