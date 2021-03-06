import re

from django.db import models


class NaturalSortField(models.CharField):
    """
    Using the value of another field on the model, make a version that is
    more suitable for sorting.

    If the object has a `sort_as` property and that is set to `person` then
    the string will be treated as if it's a name, i.e. surname put first.

    Either way, this will be done:

    * Stripped of leading/trailing spaces.
    * All lowercase.
    * Integers heavily padded with zeros.

    And, if it's a person:

    * Surnames moved to the start.
        e.g. "David Foster Wallace" becomes "wallace, david foster".
             "John Le Carre" becomes "le carre, john".
             "Daphne du Maurier" becomes "maurier, daphne du".
             "Sir Fred Bloggs Jr" becomes "bloggs, sir fred jr".
             "Prince" is "prince".

    Or, if it's not a person:

    * Articles ("the", "a", etc) moved to the end of the string.
        e.g. "The Long Blondes" becomes "long blondes, the".
             "An Actor Prepares" becomes "actor prepares, an".
             "Le Tigre" becomes "tigre, le".
             "Vol. 2 No. 11, November 2004" becomes
                 "vol. 00000002 no. 00000011, november 00002004".

    So, use like:

        class Author(mdoels.Model):
            name = models.CharField(max_length=255)
            name_sort = NaturalSortField('name',  max_length=255)
            sort_as = 'person'

            class Meta:
                ordering = ('name_sort',)
    """

    description = "A string to allow more human-friendly sorting"

    def __init__(self, for_field, *args, **kwargs):
        """
        for_field - The name of the field to base this field's string on.
                    e.g. 'title' or 'name'.
        """
        self.for_field = for_field
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('max_length', 255)
        super(NaturalSortField, self).__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        args.append(self.for_field)
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        string = getattr(model_instance, self.for_field)

        string = string.strip()

        if hasattr(model_instance, 'sort_as') and model_instance.sort_as == 'person':
            string = self.naturalize_person(string)
            # The case of the name is important, so we lowercase afterwards:
            string = string.lower()
        else:
            string = string.lower()
            string = self.naturalize_thing(string)

        return string

    def naturalize_thing(self, string):
        """
        Make a naturalized version of a general string, not a person's name.
        e.g., title of a book, a band's name, etc.

        string -- a lowercase string.
        """

        # Things we want to move to the back of the string:
        articles = [
                        'a', 'an', 'the',
                        'un', 'une', 'le', 'la', 'les', "l'", "l’",
                        'ein', 'eine', 'der', 'die', 'das',
                        'una', 'el', 'los', 'las',
                    ]

        sort_string = string
        parts = string.split(' ')

        if len(parts) > 1 and parts[0] in articles:
            if parts[0] != parts[1]:
                # Don't do this if the name is 'The The' or 'La La Land'.
                # Makes 'long blondes, the':
                sort_string = '{}, {}'.format(' '.join(parts[1:]), parts[0])

        sort_string = self._naturalize_numbers(sort_string)

        return sort_string

    def naturalize_person(self, string):
        """
        Attempt to make a version of the string that has the surname, if any,
        at the start.

        'John, Brown' to 'Brown, John'
        'Sir John Brown Jr' to 'Brown, Sir John Jr'
        'Prince' to 'Prince'

        string -- The string to change.
        """
        suffixes = [
                    'Jr', 'Jr.', 'Sr', 'Sr.',
                    'I', 'II', 'III', 'IV', 'V',
                    ]
        # Add lowercase versions:
        suffixes = suffixes + [s.lower() for s in suffixes]

        # If a name has a capitalised particle in we use that to sort.
        # So 'Le Carre, John' but 'Carre, John le'.
        particles = [
                    'Le', 'La',
                    'Von', 'Van',
                    'Du', 'De',
                    ]

        surname = '' # Smith
        names = ''   # Fred James
        suffix = ''  # Jr

        sort_string = string
        parts = string.split(' ')

        if parts[-1] in suffixes:
            # Remove suffixes entirely, as we'll add them back on the end.
            suffix = parts[-1]
            parts = parts[0:-1] # Remove suffix from parts
            sort_string = ' '.join(parts)

        if len(parts) > 1:

            if parts[-2] in particles:
                # From ['Alan', 'Barry', 'Le', 'Carré']
                # to   ['Alan', 'Barry', 'Le Carré']:
                parts = parts[0:-2] + [ ' '.join(parts[-2:]) ]

            # From 'David Foster Wallace' to 'Wallace, David Foster':
            sort_string = '{}, {}'.format(parts[-1], ' '.join(parts[:-1]))

        if suffix:
            # Add it back on.
            sort_string = '{} {}'.format(sort_string, suffix)

        # In case this name has any numbers in it.
        sort_string = self._naturalize_numbers(sort_string)

        return sort_string

    def _naturalize_numbers(self, string):
        """
        Makes any integers into very zero-padded numbers.
        e.g. '1' becomes '00000001'.
        """

        def naturalize_int_match(match):
            return '%08d' % (int(match.group(0)),)

        string = re.sub(r'\d+', naturalize_int_match, string)

        return string


class PersonNaturalSortField(NaturalSortField):
    pass

class PersonDisplayNaturalSortField(NaturalSortField):
    pass
