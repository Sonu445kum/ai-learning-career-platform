from django.urls import path
from .views import (
    CategoryListView,
    CourseListView, CourseDetailView, CourseCreateView, CourseUpdateView, InstructorCoursesView,
    SectionListCreateView, LessonListCreateView, LessonDetailView,
    EnrollFreeView, MyCoursesView, CourseProgressView, MarkLessonCompleteView,
    ReviewListCreateView,
    InitiatePaymentView, VerifyPaymentView, PaymentHistoryView,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # Courses
    path('', CourseListView.as_view(), name='course-list'),
    path('create/', CourseCreateView.as_view(), name='course-create'),
    path('my-courses/', MyCoursesView.as_view(), name='my-courses'),
    path('instructor/courses/', InstructorCoursesView.as_view(),
         name='instructor-courses'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),

    # Sections & Lessons
    path('<int:course_pk>/sections/',
         SectionListCreateView.as_view(), name='section-list'),
    path('sections/<int:section_pk>/lessons/',
         LessonListCreateView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),

    # Enrollment
    path('<int:course_id>/enroll/', EnrollFreeView.as_view(), name='enroll-free'),
    path('<int:course_id>/progress/',
         CourseProgressView.as_view(), name='course-progress'),
    path('lessons/<int:lesson_id>/complete/',
         MarkLessonCompleteView.as_view(), name='lesson-complete'),

    # Reviews
    path('<int:course_pk>/reviews/',
         ReviewListCreateView.as_view(), name='review-list'),

    # Payments
    path('payment/initiate/', InitiatePaymentView.as_view(),
         name='payment-initiate'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='payment-verify'),
    path('payment/history/', PaymentHistoryView.as_view(), name='payment-history'),
]
