from django.conf.urls import url

from . import views


# This should be under the namespace 'spectator:reading'.

urlpatterns = [
    url(
        regex=r"^$",
        view=views.ReadingHomeView.as_view(),
        name='home'
    ),
    url(
        regex=r"^series/$",
        view=views.PublicationSeriesListView.as_view(),
        name='publicationseries_list'
    ),
    url(
        regex=r"^series/(?P<pk>\d+)/$",
        view=views.PublicationSeriesDetailView.as_view(),
        name='publicationseries_detail'
    ),
    url(
        regex=r"^publications/$",
        view=views.PublicationListView.as_view(),
        name='publication_list'
    ),
    url(
        regex=r"^publications/periodicals/$",
        view=views.PublicationListView.as_view(),
        name='publication_list_periodical',
        kwargs={'kind': 'periodical',}
    ),
    url(
        regex=r"^publications/(?P<pk>\d+)/$",
        view=views.PublicationDetailView.as_view(),
        name='publication_detail'
    ),
    url(
        regex=r"^(?P<year>[0-9]{4})/$",
        view=views.ReadingYearArchiveView.as_view(),
        name='reading_year_archive'
    ),
]

