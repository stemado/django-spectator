from django.db.models import Min
from django.http import Http404
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.generic import DetailView, ListView, YearArchiveView
from django.views.generic.detail import SingleObjectMixin
try:
    # Django >= 1.10
    from django.urls import reverse
except ImportError:
    # Django < 1.10
    from django.core.urlresolvers import reverse

from spectator.core.views import PaginatedListView
from .models import ClassicalWork, DancePiece, Event, Movie, Play, Venue


class EventListView(PaginatedListView):
    """
    Includes context of counts of all different Event types,
    plus the kind of event this page is for,
    plus adding `event_list` (synonym for `object_list`).
    """
    model = Event
    ordering = ['-date',]

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('kind_slug', None)
        if slug is not None and slug not in Event.get_valid_kind_slugs():
            raise Http404("Invalid kind_slug: '%s'" % slug)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update( self.get_event_counts() )

        context['event_kind'] = self.get_event_kind()
        context['event_list'] = context['object_list']
        return context

    def get_event_counts(self):
        """
        Returns a dict like:
            {'counts': {
                'all': 30,
                'movie': 12,
                'gig': 10,
            }}
        """
        counts = {'all': Event.objects.count(),}

        for k,v in Event.KIND_CHOICES:
            # e.g. 'movie_count':
            counts[k] = Event.objects.filter(kind=k).count()

        return {'counts': counts,}

    def get_event_kind(self):
        """
        Unless we're on the front page we'll have a kind_slug like 'movies'.
        We need to translate that into an event `kind` like 'movie'.
        """
        slug = self.kwargs.get('kind_slug', None)
        if slug is None:
            return None  # Front page; showing all Event kinds.
        else:
            slugs_to_kinds = {v:k for k,v in Event.KIND_SLUGS.items()}
            return slugs_to_kinds.get(slug, None)

    def get_queryset(self):
        "Restrict to a single kind of event, if any, and include Venue data."
        qs = super().get_queryset()

        kind = self.get_event_kind()
        if kind is not None:
            qs = qs.filter(kind=kind)

        qs = qs.select_related('venue')

        return qs


class EventDetailView(DetailView):
    """
    For simple events, like Gigs and Misc, it's a standard EventDetail view.

    For Movies and Plays it's actually a MovieDetail or PlayDetail view, as
    determined by the value of `kind_slug`.
    """
    model = Event
    slug_url_kwarg = 'kind_slug'
    slug_field = 'kind_slug'
    query_pk_and_slug = True

    def get_queryset(self):
        """
        Determine if we need to change the model and template_name due to the
        `kind_slug`.
        """
        kind = self.get_event_kind()
        if kind == 'movie':
            self.model = Movie
            self.template_name = 'spectator_events/movie_detail.html'
            self.query_pk_and_slug = False
        elif kind == 'play':
            self.model = Play
            self.template_name = 'spectator_events/play_detail.html'
            self.query_pk_and_slug = False
        return super().get_queryset()

    def get_event_kind(self):
        "Translate the `kind_slug` into an event `kind` like 'movie'."
        slug = self.kwargs.get('kind_slug')
        slugs_to_kinds = {v:k for k,v in Event.KIND_SLUGS.items()}
        return slugs_to_kinds.get(slug, None)


class EventYearArchiveView(YearArchiveView):
    allow_empty = True
    date_field = 'date'
    make_object_list = True
    model = Event
    ordering = 'date'

    def get_queryset(self):
        "Reduce the number of queries and speed things up."
        qs = super().get_queryset()
        qs = qs.select_related('venue')
        return qs

    def get_dated_items(self):
        items, qs, info = super().get_dated_items()

        if 'year' in info and info['year']:
            # Get the earliest date we have an Event for:
            date_min = Event.objects.aggregate(Min('date'))['date__min']
            # Make it a 'yyyy-01-01' date:
            min_year_date = date_min.replace(month=1, day=1)
            if info['year'] < min_year_date:
                # The year we're viewing is before our minimum date, so 404.
                raise Http404(_("No %(verbose_name_plural)s available") % {
                    'verbose_name_plural': force_text(qs.model._meta.verbose_name_plural)
                })
            elif info['year'] == min_year_date:
                # This is the earliest year we have events for, so
                # there is no previous year.
                info['previous_year'] = None

        return items, qs, info


# CLASSICAL WORK, DANCE PIECE, MOVIE AND PLAY LISTS/DETAILS.

class WorkListView(PaginatedListView):
    """
    Parent class for all the "work" list views.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('roles__creator')
        return qs

class MovieListView(WorkListView):
    model = Movie

class MovieDetailView(DetailView):
    model = Movie

class PlayListView(WorkListView):
    model = Play

class PlayDetailView(DetailView):
    model = Play

class ClassicalWorkListView(WorkListView):
    model = ClassicalWork
    template_name = 'spectator_events/m2m_work_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Classical works'
        return context

class ClassicalWorkDetailView(DetailView):
    model = ClassicalWork
    template_name = 'spectator_events/m2m_work_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_list_title'] = 'Classical works'
        context['breadcrumb_list_url'] = reverse(
                'spectator:events:classicalwork_list')
        return context

class DancePieceListView(WorkListView):
    model = DancePiece
    template_name = 'spectator_events/m2m_work_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Dance pieces'
        return context

class DancePieceDetailView(DetailView):
    model = DancePiece
    template_name = 'spectator_events/m2m_work_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_list_title'] = 'Dance pieces'
        context['breadcrumb_list_url'] = reverse(
                'spectator:events:dancepiece_list')
        return context


# VENUES

class VenueListView(PaginatedListView):
    model = Venue
    ordering = ['name_sort']


class VenueDetailView(SingleObjectMixin, PaginatedListView):
    template_name = 'spectator_events/venue_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Venue.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venue'] = self.object
        context['event_list'] = context['object_list']
        if hasattr(settings, 'SPECTATOR_GOOGLE_MAPS_API_KEY') and settings.SPECTATOR_GOOGLE_MAPS_API_KEY:
            if self.object.latitude is not None and self.object.longitude is not None:
                context['SPECTATOR_GOOGLE_MAPS_API_KEY'] = settings.SPECTATOR_GOOGLE_MAPS_API_KEY
        return context

    def get_queryset(self):
        return self.object.event_set.order_by('-date')


