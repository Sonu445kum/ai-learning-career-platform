from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
import razorpay
import hmac
import hashlib

from .models import Course, Category, Section, Lesson, Enrollment, LessonProgress, Review, Payment
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseCreateSerializer,
    CategorySerializer, SectionSerializer, LessonSerializer,
    EnrollmentSerializer, LessonProgressSerializer, ReviewSerializer,
    PaymentInitSerializer, PaymentVerifySerializer, PaymentSerializer,
)
from .filters import CourseFilter
from accounts.permissions import IsInstructor, IsStudent


# ─── Category ────────────────────────────────────────────────────────────────

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ─── Courses ──────────────────────────────────────────────────────────────────

class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'short_description',
                     'tags', 'instructor__first_name']
    ordering_fields = ['created_at', 'price',
                       'average_rating', 'total_students']
    ordering = ['-created_at']

    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('instructor', 'category')


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(status='published')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseCreateSerializer
    permission_classes = [IsInstructor]


class CourseUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseCreateSerializer
    permission_classes = [IsInstructor]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class InstructorCoursesView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [IsInstructor]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


# ─── Sections & Lessons ───────────────────────────────────────────────────────

class SectionListCreateView(generics.ListCreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsInstructor]

    def get_queryset(self):
        course = get_object_or_404(
            Course, pk=self.kwargs['course_pk'], instructor=self.request.user)
        return Section.objects.filter(course=course)

    def perform_create(self, serializer):
        course = get_object_or_404(
            Course, pk=self.kwargs['course_pk'], instructor=self.request.user)
        serializer.save(course=course)


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsInstructor]

    def get_queryset(self):
        return Lesson.objects.filter(section__pk=self.kwargs['section_pk'])

    def perform_create(self, serializer):
        section = get_object_or_404(Section, pk=self.kwargs['section_pk'])
        serializer.save(section=section)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsInstructor]

    def get_queryset(self):
        return Lesson.objects.filter(section__course__instructor=self.request.user)


# ─── Enrollment ───────────────────────────────────────────────────────────────

class EnrollFreeView(APIView):
    """Enroll in a free course."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id, status='published')
        if not course.is_free:
            return Response({'error': 'This course requires payment.'}, status=status.HTTP_400_BAD_REQUEST)
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course)
        if not created:
            return Response({'message': 'Already enrolled.'})
        course.total_students += 1
        course.save(update_fields=['total_students'])
        return Response({'message': 'Enrolled successfully.', 'enrollment_id': enrollment.id},
                        status=status.HTTP_201_CREATED)


class MyCoursesView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course')


class CourseProgressView(generics.ListAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        enrollment = get_object_or_404(
            Enrollment, student=self.request.user, course__pk=self.kwargs['course_id']
        )
        return LessonProgress.objects.filter(enrollment=enrollment)


class MarkLessonCompleteView(APIView):
    """Mark a lesson as complete and update progress."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        enrollment = get_object_or_404(
            Enrollment, student=request.user, course=lesson.section.course
        )
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            # Recalculate enrollment progress
            total = enrollment.course.total_lessons
            completed = LessonProgress.objects.filter(
                enrollment=enrollment, is_completed=True).count()
            enrollment.progress_percent = (
                completed / total * 100) if total else 0
            if enrollment.progress_percent >= 100:
                enrollment.is_completed = True
                enrollment.completed_at = timezone.now()
            enrollment.save()
        return Response({'progress_percent': enrollment.progress_percent})


# ─── Reviews ─────────────────────────────────────────────────────────────────

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Review.objects.filter(course__pk=self.kwargs['course_pk'], is_approved=True)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        review = serializer.save(student=self.request.user, course=course)
        # Update course average rating
        reviews = Review.objects.filter(course=course, is_approved=True)
        course.average_rating = sum(
            r.rating for r in reviews) / reviews.count()
        course.total_reviews = reviews.count()
        course.save(update_fields=['average_rating', 'total_reviews'])


# ─── Payments ─────────────────────────────────────────────────────────────────

class InitiatePaymentView(APIView):
    """Create a Razorpay order."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(
            Course, pk=serializer.validated_data['course_id'], status='published')

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({'error': 'Already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)

        amount = int(course.effective_price * 100)  # paise
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create(
            {'amount': amount, 'currency': 'INR', 'payment_capture': 1})

        payment = Payment.objects.create(
            student=request.user,
            course=course,
            razorpay_order_id=order['id'],
            amount=course.effective_price,
        )
        return Response({
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'course_title': course.title,
        })


class VerifyPaymentView(APIView):
    """Verify Razorpay payment signature and enroll student."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payment = get_object_or_404(
            Payment, razorpay_order_id=data['razorpay_order_id'], student=request.user)

        # Verify signature
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{data['razorpay_order_id']}|{data['razorpay_payment_id']}".encode(),
            hashlib.sha256,
        ).hexdigest()

        if generated_signature != data['razorpay_signature']:
            payment.status = Payment.FAILED
            payment.save()
            return Response({'error': 'Invalid payment signature.'}, status=status.HTTP_400_BAD_REQUEST)

        payment.razorpay_payment_id = data['razorpay_payment_id']
        payment.razorpay_signature = data['razorpay_signature']
        payment.status = Payment.COMPLETED
        payment.save()

        # Create enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=payment.course
        )
        if created:
            payment.course.total_students += 1
            payment.course.save(update_fields=['total_students'])

        return Response({'message': 'Payment verified. Enrolled successfully!', 'enrollment_id': enrollment.id})


class PaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(student=self.request.user)
