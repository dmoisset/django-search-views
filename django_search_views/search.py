import functools
import operator

from django.template.response import TemplateResponse

from django.db.models import Q
from django.db.models.options import get_verbose_name

from django_search_views.forms import SearchForm


class InvalidConfiguration(Exception):
    pass

class SearchCategory(object):

    form = SearchForm

    @classmethod
    def search_view(cls):
        """Returns a view that can do search in this category"""
        def view(request):
            name = get_verbose_name(cls.__name__).replace(' ','_')
            context = {
                'form': cls.form,
            }
            return TemplateResponse(request, 'search/search_%s.html' % name, context)
        return view

    @classmethod
    def results_view(cls):
        """Returns a view with search results for this category"""
        self = cls()
        def view(request):
            results = None
            query = None
            form = cls.form(request.GET)
            name = get_verbose_name(cls.__name__).replace(' ','_')
            if form.is_valid():
                results = self.get_results(form.cleaned_data, request)
                query = form.cleaned_data
            context = {
                'form': form,
                'results': results,
                'query_data': query
            }
            return TemplateResponse(request, 'search/results_%s.html' % name, context)
        return view

    def get_results(self, cleaned_data, request=None):
        """
        Return the search results for this category, according to the
        query specified in `cleaned_data`, for the given `request`.
        Override this to customize search behavior.
        
        The default implementation covers a few usual cases of DB lookups,
        assuming you set the following class attributes:
            - model: a django.db.Model (a class, not just a name) where the
                     lookup should be done.
                     Example: model = auth.User
            - queryset: instead of model, you can define a queryset. Searches
                        will be restricted to objects in the given queryset.
                        If you specify a queryset, model attribute is ignored.
                        Example: queryset = User.objects.filter(is_staff=False)
            - lookups: a list of field lookups to be done on the model with the
                       query used. 
                       Example: lookups = ['username', 'email__icontains']
        """
        # Check that configuration is correct
        try:
            if hasattr(self, 'queryset'):
                queryset = self.queryset
            else:
                queryset = self.model._default_manager.all()
            lookups = self.lookups
        except AttributeError:
            raise InvalidConfiguration("%s: You need to define model/queryset and lookups, "
                                       "or override get_results()" % 
                                       type(self).__name__)
        # Check that lookups has items
        if not lookups:
            raise InvalidConfiguration("%s: lookups is empty" % 
                                       type(self).__name__)
            
        query_string = cleaned_data['q']
        q_lookups = (Q(**{lookup: query_string}) for lookup in lookups)
        q = functools.reduce(operator.or_, q_lookups)
        return queryset.filter(q)
        
class Search(object):

    @classmethod
    def search_form(cls):
        """Returns a Form class usable for generic queries"""
        raise NotImplementedError
        
    @classmethod
    def category_search_form(cls):
        """Returns a Form class usable for querying a user-selected category"""
        raise NotImplementedError

    @classmethod
    def search_view(cls):
        """Returns a view that can do a generic search"""
        raise NotImplementedError

    @classmethod
    def category_search_view(cls):
        """Returns a view that can do a generic search"""
        raise NotImplementedError

    @classmethod
    def results_view(cls):
        """Returns a view with search results grouped by category"""
        raise NotImplementedError

    @classmethod
    def category_search_view(cls):
        """Returns a view that can do a generic search"""
        raise NotImplementedError

    @classmethod
    def urls(cls, namespace='search'):
        """
        Returns a set of namespaced urls for global+category search and result
        views; This can be used in an include() on a URLConf
        """
        raise NotImplementedError
        

