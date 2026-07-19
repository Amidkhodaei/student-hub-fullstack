from rest_framework import serializers
from .models import User, Department, Instructor, Lesson

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = User
        fields = [
            'id', 
            'student_no', 
            'fullname',
            'first_name',
            'last_name', 
            'email', 
            'phone', 
            'password', 
            'fullname'
        ]

        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'first_name': {'write_only': True,'required': True},
            'last_name': {'write_only': True,'required': True},
            'email': {'required': True}
        }

    def get_fullname(self, user):
        return f"{user.first_name} {user.last_name}"
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department

        fields = [
            'dept_id',
            'dept_name'
        ]

        extra_kwargs = {
            'dept_id' : {'required': True},
            'dept_name': {'required': True}
        }

class  InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'

class  LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

        extra_kwargs = {
            'lesson_id' : {'required': True},
            'lesson_name': {'required': True},
            'credit' : {'required': True},
            'active_credit': {'required': True},
            'capacity' : {'required': True},
            'gender': {'required': True},
            'times': {'required': True},
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    student_no = serializers.CharField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': 'رمز عبور و تکرار آن یکسان نیستند'})
        if len(attrs['new_password1']) < 6:
            raise serializers.ValidationError({'new_password1': 'رمز عبور باید حداقل ۶ کاراکتر باشد'})
        return attrs


class ExcelUploadSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()
    excel_file = serializers.FileField()

    def validate_excel_file(self, value):
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("فرمت فایل باید اکسل باشد")
        return value