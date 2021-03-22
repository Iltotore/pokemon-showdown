import json


class UserInfo:

    def __init__(self,
                 logged_in: bool,
                 nickname: str,
                 avatar: str,
                 blockChallenges: bool,
                 blockPMs: bool,
                 ignoreTickets: bool,
                 hideBattlesFromTrainerCard: bool,
                 blockInvites: bool,
                 doNotDisturb: bool,
                 hiddenNextBattle: bool,
                 inviteOnlyNextBattle: bool,
                 language: str):  # Constructor parameters use the same case than showdown's to easify deserialization
        self.logged_in = logged_in
        self.nickname = nickname
        self.avatar = avatar
        self.block_challenges = blockChallenges
        self.block_pms = blockPMs
        self.ignore_tickets = ignoreTickets
        self.hide_battles_from_trainer_card = hideBattlesFromTrainerCard
        self.block_invites = blockInvites
        self.do_not_disturb = doNotDisturb
        self.hidden_next_battle = hiddenNextBattle
        self.invite_only_next_battle = inviteOnlyNextBattle
        self.language = language


def user_from_json(data: str, **kwargs):
    d = json.loads(data)
    d.update(kwargs)
    return UserInfo(**d)


default_user = UserInfo(False, "Guest", "red", False, False, False, False, False, False, False, False, "english")


class Format:

    def __init__(self, name: str, visibility: str):
        self.name = name
        self.visibility = visibility

    def is_visible(self):
        return self.visibility == "e" or self.visibility == "f"

    def is_random(self):
        return self.visibility == "f"
