from django.contrib import admin
from .models import Category, Course, Section, Lesson, Enrollment, LessonProgress, Review, Payment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [SectionInline]
    list_display = ['title', 'instructor', 'category', 'level', 'status', 'price',
                    'total_students', 'average_rating', 'created_at']
    list_filter = ['status', 'level', 'category', 'is_free']
    search_fields = ['title', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['total_students', 'average_rating',
                       'total_reviews', 'created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'lesson_type',
              'duration_minutes', 'is_preview']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ['title', 'course', 'order']
    list_filter = ['course']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at',
                    'progress_percent', 'is_completed']
    list_filter = ['is_completed']
    search_fields = ['student__email', 'course__title']
    readonly_fields = ['enrolled_at', 'last_accessed']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved']
    list_editable = ['is_approved']
    search_fields = ['student__email', 'course__title']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'amount',
                    'status', 'razorpay_order_id', 'created_at']
    list_filter = ['status']
    search_fields = ['student__email', 'razorpay_order_id']
    readonly_fields = ['razorpay_order_id',
                       'razorpay_payment_id', 'razorpay_signature', 'created_at']
