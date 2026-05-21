from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
import pandas as pd
from django.db import transaction
from .models import User, Department, Instructor, Lesson
from .serializers import UserSerializer, DepartmentSerializer, InstructorSerializer, LessonSerializer, ExcelUploadSerializer
from .utils import parse_instructors, parse_schedule_and_exam, normalize_fa_text
from django.core.exceptions import ValidationError

# Create your views here.
class UserViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "ثبت نام با موفقیت ثبت شد."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'],  permission_classes=[IsAuthenticated])
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
            #cnt = 1

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # ۱. تبدیل شماره و گروه درس (مثلاً تبدیل 1710105_01 به 171010501)
                        lesson_id_raw = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                        lesson_id = lesson_id_raw.replace('_', '') # حذف خط تیره
                        
                        if not lesson_id:
                            continue

                        # ۲. نام درس
                        lesson_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
                        
                        # ۳. تعداد واحد (کل)
                        credit = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0

                        # ۴. تعداد واحد عملی
                        active_credit = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0.0
                        
                        # ۵. ظرفیت
                        capacity = int(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
                        
                        # ۶. جنسیت
                        gender_text = str(row.iloc[7]).strip() if pd.notna(row.iloc[6]) else "مختلط"
                        gender_map = {'مختلط': 0, 'مرد': 1, 'زن': 2}
                        gender = gender_map.get(gender_text, 0)
                        
                        # ۷. اساتید (ایندکس ۸ - ستون نوع مسئولیت استاد)
                        instructor_resp_column = row.iloc[10] if len(row) > 8 else ""
                        instructor_resp_column = normalize_fa_text(instructor_resp_column)
                        instructors_list = parse_instructors(instructor_resp_column)
                        
                        if not instructors_list and pd.notna(row.iloc[6]):
                            instructors_list = [str(row.iloc[6]).strip()]

                        # ۸. زمان کلاس، مکان و اطلاعات امتحان (ایندکس ۱۰ - ستون زمان و مکان)
                        schedule_column_text = row.iloc[11] if len(row) > 5 else ""
                        schedule_column_text = normalize_fa_text(schedule_column_text)
                        times, exam_time = parse_schedule_and_exam(schedule_column_text)
                        
                        # ۹. توضیحات (ایندکس ۱۱ - ستون توضیحات)
                        description = normalize_fa_text(row.iloc[12]) if len(row) > 5 and pd.notna(row.iloc[12]) else ""

                        if (int(int(lesson_id)) // 10000000 != department_id):
                            continue

                        # بررسی وجود یا آپدیت درس
                        lesson = Lesson.objects.filter(lesson_id=lesson_id, department_id=department).first()

                        #print(cnt)
                        #cnt += 1
                        print(lesson_id)
                        print(lesson_name)
                        print(department)
                        print(credit)
                        print(active_credit)
                        print(capacity)
                        print(gender)
                        print(instructors_list)
                        print(times)
                        print(exam_time)
                        print(description)

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