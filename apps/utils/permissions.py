from functools import wraps

from rest_framework import status
from rest_framework.response import Response
from apps.utils.enums import UserTypeEnum


def company_access_only():
    """
    Grant permission to company alone
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user_type = request.user.user_type
            if user_type is not None:
                if user_type.strip() not in [UserTypeEnum.COMPANY_OWNER]:
                    return Response(
                        {
                            "status": status.HTTP_403_FORBIDDEN,
                            "message": "You currently do not have access to this resource",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                response = func(request, *args, **kwargs)
                return response
            else:
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        return wrapper

    return decorator
