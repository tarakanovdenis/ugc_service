import enum

from django.contrib.postgres.aggregates import ArrayAgg
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.db.models import Q
from movies.models import FilmWork


class Role(enum.Enum):
    actor = 'actor'
    director = 'director'
    writer = 'writer'


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        return FilmWork.objects.values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type').annotate(
                genres=ArrayAgg(
                    'genres__name',
                    distinct=True,
                    default=[]
                ),
                actors=ArrayAgg(
                    'persons__full_name',
                    distinct=True,
                    filter=Q(personfilmwork__role=Role.actor.value),
                    default=[]
                ),
                directors=ArrayAgg(
                    'persons__full_name',
                    distinct=True,
                    filter=Q(personfilmwork__role=Role.director.value),
                    default=[]
                ),
                writers=ArrayAgg(
                    'persons__full_name',
                    distinct=True,
                    filter=Q(personfilmwork__role=Role.actor.value),
                    default=[]
                )
            )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )

        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset)
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context['movie']
