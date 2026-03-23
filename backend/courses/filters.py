import django_filters
from .models import Course


class CourseFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte')
    level = django_filters.MultipleChoiceFilter(choices=Course.LEVEL_CHOICES)
    category = django_filters.CharFilter(field_name='category__slug')
    is_free = django_filters.BooleanFilter()
    language = django_filters.CharFilter(lookup_expr='icontains')
    min_rating = django_filters.NumberFilter(
        field_name='average_rating', lookup_expr='gte')

    class Meta:
        model = Course
        fields = ['level', 'category', 'is_free', 'language',
                  'min_price', 'max_price', 'min_rating']
