from django.db import models
try:
    # Django >= 1.10
    from django.urls import reverse
except ImportError:
    # Django < 1.10
    from django.core.urlresolvers import reverse

from .fields import NaturalSortField


class TimeStampedModelMixin(models.Model):
    "Should be mixed in to all models."
    time_created = models.DateTimeField(auto_now_add=True,
                help_text="The time this item was created in the database.")
    time_modified = models.DateTimeField(auto_now=True,
                help_text="The time this item was last saved to the database.")

    class Meta:
        abstract = True


class BaseRole(TimeStampedModelMixin, models.Model):
    """
    Base class for linking a Creator to a Book, Event, Movie, etc.

    Child classes should add fields like:

        creator = models.ForeignKey('spectator_core.Creator', blank=False,
                    on_delete=models.CASCADE, related_name='publication_roles')

        publication = models.ForeignKey('spectator_reading.Publication',
                    on_delete=models.CASCADE, related_name='roles')
    """
    role_name = models.CharField(null=False, blank=True, max_length=50,
            help_text="e.g. 'Headliner', 'Support', 'Editor', 'Illustrator', 'Director', etc. Optional.")

    role_order = models.PositiveSmallIntegerField(null=False, blank=False,
            default=1,
            help_text="The order in which the Creators will be listed.")

    class Meta:
        abstract = True
        ordering = ('role_order', 'role_name',)

    def __str__(self):
        if self.role_name:
            return '{} ({})'.format(self.creator, self.role_name)
        else:
            return str(self.creator)


class Creator(TimeStampedModelMixin, models.Model):
    """
    A person or a group/company/organisation that is responsible for making all
    or part of a book, play, movie, gig, etc.

    Get the things they've worked on:

        creator = Creator.objects.get(pk=1)

        # Just Publication titles:
        for publication in creator.publications.distinct():
            print(publication.title)

        # You can do similar to that to get lists of `events`, `movies` and,
        # `plays` the Creator was involved with.


        # Or Publications including the Creator and their role:
        for role in creator.publication_roles.all():
            print(role.publication, role.creator, role.role_name)

        # Similarly for Event roles:
        for role in creator.event_roles.all():
            print(role.event, role.creator, role.role_name)

        # And for Movie roles:
        for role in creator.movie_roles.all():
            print(role.movie, role.creator, role.role_name)

        # And for Play roles:
        for role in creator.play_roles.all():
            print(role.play, role.creator, role.role_name)
    """

    KIND_CHOICES = (
        ('individual', 'Individual'),
        ('group', 'Group'),
    )

    name = models.CharField(max_length=255,
            help_text="e.g. 'Douglas Adams' or 'The Long Blondes'.")

    name_sort = NaturalSortField(
        'name', max_length=255, default='',
        help_text="Best for sorting groups. e.g. 'long blondes, the' or 'adams, douglas'.")

    kind = models.CharField(max_length=20, choices=KIND_CHOICES,
                                                        default='individual')

    class Meta:
        ordering = ('name_sort',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('spectator:creators:creator_detail', kwargs={'pk':self.pk})

    @property
    def sort_as(self):
        "Used by the NaturalSortField."
        if self.kind == 'individual':
            return 'person'
        else:
            return 'thing'

    def get_movies(self):
        """
        A list of all the Movies the Creator worked on.
        Each one also has these properties:
        * `creator_roles` - QuerySet of MovieRole objects for this Creator.
        * `creator_role_names` - List of the role_names (if any this Creator
            had. Note, this could be empty if none of the roles have names.
        """
        movies = []
        for movie in self.movies.distinct():
            movie.creator_roles = movie.roles.filter(creator=self)
            movie.creator_role_names = []
            for role in movie.creator_roles:
                if role.role_name:
                    movie.creator_role_names.append(role.role_name)
            movies.append(movie)
        return movies

    def get_plays(self):
        """
        A list of all the Plays the Creator worked on.
        Each one also has these properties:
        * `creator_roles` - QuerySet of PlayRole objects for this Creator.
        * `creator_role_names` - List of the role_names (if any this Creator
            had. Note, this could be empty if none of the roles have names.
        """
        plays = []
        for play in self.plays.distinct():
            play.creator_roles = play.roles.filter(creator=self)
            play.creator_role_names = []
            for role in play.creator_roles:
                if role.role_name:
                    play.creator_role_names.append(role.role_name)
            plays.append(play)
        return plays

