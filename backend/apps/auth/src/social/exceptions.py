from src.common.exceptions import BaseServiceError


class SocialProviderNotRegisteredError(BaseServiceError):
    pass


class SocialProviderUnknownError(BaseServiceError):
    pass


class SocialServiceError(BaseServiceError):
    pass


class SocialAccountAlreadyExistsError(SocialServiceError):
    pass


class InvalidSocialProviderAccessTokenError(SocialServiceError):
    pass


class UserSocialInfoParseError(SocialServiceError):
    pass
