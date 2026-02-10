import requests
from datetime import datetime, timedelta

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

from decouple import config

from pinterest.models import PinterestToken, PinterestAccessToken
from pinterest.serializers import PinterestTokenSerializer
from utilities import constants, messages


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# ==========================
# TOKEN HELPERS
# ==========================

def gen_new_access_token(refresh_token):
    raw_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "pins:read,boards:read,user_accounts:read",
    }

    response = requests.post(
        "https://api.pinterest.com/v5/oauth/token",
        data=raw_data,
        headers={
            "Authorization": f"Basic {config('BASIC_TOKEN')}"
        },
    )

    return response.json().get("access_token")


def get_access_token(refresh_token):
    access_token_obj = PinterestAccessToken.objects.first()
    today = datetime.now().date()

    if access_token_obj and today <= access_token_obj.expiry_date:
        return access_token_obj.access_token

    access_token = gen_new_access_token(refresh_token)

    if access_token_obj:
        access_token_obj.access_token = access_token
        access_token_obj.expiry_date = today + timedelta(days=20)
        access_token_obj.save()
    else:
        PinterestAccessToken.objects.create(
            access_token=access_token,
            expiry_date=today + timedelta(days=20),
        )

    return access_token


# ==========================
# APIs
# ==========================

class GetBoardListAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = PinterestTokenSerializer

    def post(self, request):
        refresh_token_object = PinterestToken.objects.first()
        access_token = get_access_token(refresh_token_object.refresh_token)

        response = requests.get(
            "https://api.pinterest.com/v5/boards",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        data = response.json()

        return Response(
            {
                "status": True,
                "data": data.get("items", []),
                "message": messages.SUCCESS,
            },
            status=status.HTTP_200_OK,
        )


class GetBoardPinListAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = PinterestTokenSerializer

    def post(self, request):
        pin_title = request.query_params.get("pin_title")
        ordering = request.query_params.get("ordering")

        refresh_token_object = PinterestToken.objects.first()
        access_token = get_access_token(refresh_token_object.refresh_token)

        board_id = request.data.get("board_id")

        response = requests.get(
            f"https://api.pinterest.com/v5/boards/{board_id}/pins",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        data = response.json()
        items = data.get("items", [])

        if pin_title:
            items = [
                i for i in items
                if pin_title.lower() in (i.get("title") or "").lower()
            ]

        if ordering == "oldest":
            items = items[::-1]

        paginator = StandardResultsSetPagination()
        result = paginator.paginate_queryset(items, request)
        return paginator.get_paginated_response(result)


class GetPinDetailAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = PinterestTokenSerializer

    def post(self, request):
        refresh_token_object = PinterestToken.objects.first()
        access_token = get_access_token(refresh_token_object.refresh_token)

        pin_id = request.data.get("pin_id")

        response = requests.get(
            f"https://api.pinterest.com/v5/pins/{pin_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        return Response(
            {
                "status": True,
                "data": response.json(),
                "message": messages.SUCCESS,
            },
            status=status.HTTP_200_OK,
        )


class GetAllPinsAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = PinterestTokenSerializer

    def post(self, request):
        pin_title = request.query_params.get("pin_title")
        ordering = request.query_params.get("ordering")
        page_size = request.query_params.get("page_size", 250)
        bookmark = request.data.get("bookmark")

        refresh_token_object = PinterestToken.objects.first()
        access_token = get_access_token(refresh_token_object.refresh_token)

        response = requests.get(
            constants.PINTEREST_API_URL,
            params={"page_size": page_size, "bookmark": bookmark},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        data = response.json()
        items = data.get("items", [])

        if pin_title:
            items = [
                i for i in items
                if pin_title.lower() in (i.get("title") or "").lower()
            ]

        if ordering == "oldest":
            items = items[::-1]

        paginator = PageNumberPagination()
        paginator.page_size = 20

        result = paginator.paginate_queryset(items, request)
        response = paginator.get_paginated_response(result)
        response.data["bookmark"] = data.get("bookmark")

        return response
