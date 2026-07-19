from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
import pandas as pd
from django.db import transaction
from .models import User, Department, Instructor, Lesson
from .serializers import (
    UserSerializer, DepartmentSerializer, InstructorSerializer, LessonSerializer,
    ExcelUploadSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
)
from .utils import parse_instructors, parse_schedule_and_exam, normalize_fa_text
from django.core.exceptions import ValidationError
from .tokens import account_activation_token, password_reset_token

# ایمپورت‌های جدید برای ساخت توکن امن و ارسال ایمیل
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

class UserViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            try:
                # ۱. ساخت UID و توکن فعال‌سازی
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                
                # ۲. ساخت لینک فعال‌سازی برای فرانت‌اَند (مثلاً ری‌اکت روی پورت 3000)
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                activation_link = f"{frontend_url}/verify-email/{uid}/{token}/"
                
                # ۳. ارسال ایمیل به کاربر
                subject = 'تایید حساب کاربری - سامانه دانشگاه'
                message = f"با سلام،\nلطفاً برای فعال‌سازی حساب کاربری خود روی لینک زیر کلیک کنید:\n\n{activation_link}"
                
                send_mail(
                    subject,
                    message,
                    'noreply@university.com',
                    [user.email],
                    fail_silently=False,
                )
                
                return Response(
                    {"message": ".ثبت‌نام با موفقیت انجام شد. لینک فعال‌سازی به ایمیل شما ارسال گردید"},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                # در صورت خطا در ارسال ایمیل، کاربر غیرفعال حذف می‌شود تا بتواند مجدد تلاش کند
                user.delete()
                return Response({"error": f"خطا در ارسال ایمیل فعال‌سازی: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    # اکشن جدید برای دریافت توکن از فرانت و فعال‌سازی کاربر
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='verify-email/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def verify_email(self, request, uidb64=None, token=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            if user.is_active:
                return Response({'message': '.این حساب کاربری قبلاً فعال شده است'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_active = True
            user.save()
            return Response({'message': '.حساب کاربری شما با موفقیت فعال شد. اکنون می‌توانید لاگین کنید'}, status=status.HTTP_200_OK)
        
        return Response({'error': '.لینک تایید نامعتبر یا منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='request-password-reset')
    def request_password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_no = serializer.validated_data['student_no']

        # پیام موفقیت همیشه یکسان است تا نشود فهمید یک شماره‌دانشجویی
        # در سیستم ثبت‌نام شده یا نه (جلوگیری از user enumeration)
        generic_response = Response(
            {"message": "در صورتی که این شماره دانشجویی در سامانه ثبت شده باشد، لینک بازنشانی رمز عبور به ایمیل مرتبط با آن ارسال خواهد شد"},
            status=status.HTTP_200_OK
        )

        user = User.objects.filter(student_no=student_no).first()
        if user is None or not user.is_active:
            return generic_response

        try:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)

            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"

            subject = 'بازنشانی رمز عبور - سامانه دانشگاه'
            message = f"با سلام،\nبرای بازنشانی رمز عبور حساب کاربری خود روی لینک زیر کلیک کنید:\n\n{reset_link}\n\nاگر این درخواست را شما نداده‌اید، این پیام را نادیده بگیرید."

            send_mail(
                subject,
                message,
                'noreply@university.com',
                [user.email],
                fail_silently=False,
            )
        except Exception:
            pass

        return generic_response

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='reset-password/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def reset_password(self, request, uidb64=None, token=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not password_reset_token.check_token(user, token):
            return Response({'error': '.لینک بازنشانی رمز عبور نامعتبر یا منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['new_password1'])
        user.save()

        return Response({'message': '.رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید با رمز جدید وارد شوید'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def all_users(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
class UploadLessonsExcelView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ExcelUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        department_id = serializer.validated_data['department_id']
        excel_file = serializer.validated_data['excel_file']

        try:
            department = Department.objects.filter(dept_id=department_id).first()
            if not department:
                return Response({'error': 'Department not found'}, status=404)
            
            df = pd.read_excel(excel_file)
            
            created_lessons = []
            changed_lessons = []
            notchanged_lessons = []
            errors = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        lesson_id_raw = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                        lesson_id = lesson_id_raw.replace('_', '')
                        
                        if not lesson_id:
                            continue

                        lesson_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
                        credit = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0
                        active_credit = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0.0
                        capacity = int(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
                        
                        gender_text = str(row.iloc[7]).strip() if pd.notna(row.iloc[6]) else "مختلط"
                        gender_map = {'مختلط': 0, 'مرد': 1, 'زن': 2}
                        gender = gender_map.get(gender_text, 0)
                        
                        instructor_resp_column = row.iloc[10] if len(row) > 8 else ""
                        instructor_resp_column = normalize_fa_text(instructor_resp_column)
                        instructors_list = parse_instructors(instructor_resp_column)
                        
                        if not instructors_list and pd.notna(row.iloc[6]):
                            instructors_list = [str(row.iloc[6]).strip()]

                        schedule_column_text = row.iloc[11] if len(row) > 5 else ""
                        schedule_column_text = normalize_fa_text(schedule_column_text)
                        times, exam_time = parse_schedule_and_exam(schedule_column_text)
                        
                        description = normalize_fa_text(row.iloc[12]) if len(row) > 5 and pd.notna(row.iloc[12]) else ""

                        if (int(int(lesson_id)) // 10000000 != department_id):
                            continue

                        lesson = Lesson.objects.filter(lesson_id=lesson_id, department_id=department).first()

                        haschange = False
                        
                        if lesson:
                            if lesson.lesson_name != lesson_name:
                                lesson.lesson_name = lesson_name
                                haschange = True
                            if lesson.credit != credit:
                                lesson.credit = credit
                                haschange = True
                            if lesson.active_credit != active_credit:
                                lesson.active_credit = active_credit
                                haschange = True
                            if lesson.capacity != capacity:
                                lesson.capacity = capacity
                                haschange = True
                            if lesson.gender != gender:
                                lesson.gender = gender
                                haschange = True
                            if lesson.instructors_list != instructors_list:
                                lesson.instructors_list = instructors_list
                                haschange = True
                            if lesson.times != times:
                                lesson.times = times
                                haschange = True
                            if lesson.exam_time != exam_time:
                                lesson.exam_time = exam_time
                                haschange = True
                            if lesson.description != description:
                                lesson.description = description
                                haschange = True
                            lesson.full_clean()
                            lesson.save()
                            if haschange == True:
                                changed_lessons.append(lesson.lesson_id)
                            if haschange == False:
                                notchanged_lessons.append(lesson.lesson_id)
                        else:
                            lesson = Lesson(
                                lesson_id=lesson_id,
                                lesson_name=lesson_name,
                                department_id=department,
                                credit=credit,
                                active_credit=active_credit,
                                capacity=capacity,
                                gender=gender,
                                instructors_list=instructors_list,
                                times=times,
                                exam_time=exam_time,
                                description=description
                            )
                            lesson.full_clean()
                            lesson.save()
                            created_lessons.append(lesson.lesson_id)

                    except ValidationError as ve:
                        errors.append(f"ردیف {index+1} (کد درس {lesson_id}): خطای اعتبارسنجی - {ve.message_dict}")
                    except Exception as row_error:
                        errors.append(f"ردیف {index+1}: خطای پردازش داده - {str(row_error)}")

            return Response({
                'success': len(errors) == 0,
                'message': f'{len(created_lessons)} درس با موفقیت پردازش شد',
                'created_lessons': created_lessons,
                'changed_lessons': changed_lessons,
                'notchanged_lessons': notchanged_lessons,
                'errors': errors
            }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'error': f"خطای سیستمی: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)