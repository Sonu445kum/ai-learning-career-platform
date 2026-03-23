from rest_framework import serializers
from .models import Course, Category, Section, Lesson, Enrollment, LessonProgress, Review, Payment
from accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'course_count']

    def get_course_count(self, obj):
        return obj.courses.filter(status='published').count()


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'lesson_type', 'video_url',
                  'content', 'duration_minutes', 'is_preview', 'resources']
        extra_kwargs = {
            'video_url': {'required': False},
            'content': {'required': False},
        }


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'title', 'order', 'lessons',
                  'total_lessons', 'total_duration']

    def get_total_lessons(self, obj):
        return obj.lessons.count()

    def get_total_duration(self, obj):
        return sum(l.duration_minutes for l in obj.lessons.all())


class CourseListSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    effective_price = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    thumbnail_url = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'thumbnail_url',
            'instructor', 'category', 'level', 'status', 'language',
            'price', 'discount_price', 'effective_price', 'discount_percent',
            'is_free', 'duration_hours', 'total_lessons', 'total_students',
            'average_rating', 'total_reviews', 'tags', 'created_at', 'is_enrolled',
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(student=request.user, course=obj).exists()
        return False


class CourseDetailSerializer(CourseListSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            'description', 'preview_video', 'requirements',
            'what_you_learn', 'sections', 'reviews', 'published_at',
        ]

    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_approved=True)[:5]
        return ReviewSerializer(reviews, many=True, context=self.context).data


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'category', 'short_description', 'description',
            'thumbnail', 'preview_video', 'level', 'language',
            'price', 'discount_price', 'is_free', 'requirements',
            'what_you_learn', 'tags', 'duration_hours',
        ]

    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    completed_lessons = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'is_completed',
                  'progress_percent', 'completed_lessons', 'total_lessons', 'last_accessed']

    def get_completed_lessons(self, obj):
        return obj.lesson_progress.filter(is_completed=True).count()

    def get_total_lessons(self, obj):
        return obj.course.total_lessons


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'lesson', 'is_completed',
                  'completed_at', 'watch_time_seconds']


class ReviewSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'student', 'rating',
                  'comment', 'created_at', 'updated_at']
        read_only_fields = ['student', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class PaymentInitSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()


class PaymentVerifySerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class PaymentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'course', 'razorpay_order_id', 'razorpay_payment_id',
                  'amount', 'status', 'created_at']
