from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    LEVEL_CHOICES = [(BEGINNER, 'Beginner'), (INTERMEDIATE,
                                              'Intermediate'), (ADVANCED, 'Advanced')]

    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    STATUS_CHOICES = [(DRAFT, 'Draft'), (PUBLISHED,
                                         'Published'), (ARCHIVED, 'Archived')]

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_created'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='courses')

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/', null=True, blank=True)
    preview_video = models.URLField(blank=True)

    level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, default=BEGINNER)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    language = models.CharField(max_length=50, default='English')

    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    is_free = models.BooleanField(default=False)

    requirements = models.JSONField(default=list)
    what_you_learn = models.JSONField(default=list)
    tags = models.JSONField(default=list)

    duration_hours = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sections'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    VIDEO = 'video'
    ARTICLE = 'article'
    QUIZ = 'quiz'
    TYPE_CHOICES = [(VIDEO, 'Video'), (ARTICLE, 'Article'), (QUIZ, 'Quiz')]

    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    lesson_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=VIDEO)
    video_url = models.URLField(blank=True)
    content = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    resources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lessons'
        ordering = ['order']

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    progress_percent = models.FloatField(default=0.0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.email} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    watch_time_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.lesson.title}"


class Review(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ['student', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.email} rated {self.course.title} - {self.rating}/5"


class Payment(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'), (COMPLETED, 'Completed'),
        (FAILED, 'Failed'), (REFUNDED, 'Refunded')
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=300, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.email} - {self.course.title} - {self.status}"
