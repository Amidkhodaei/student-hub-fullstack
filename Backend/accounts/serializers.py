from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Department, Instructor, Lesson, SavedSchedule, ScheduleItem

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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_staff'] = user.is_staff
        token['fullname'] = f"{user.first_name} {user.last_name}"
        return token


class ScheduleItemSerializer(serializers.ModelSerializer):
    lesson_detail = LessonSerializer(source='lesson', read_only=True)

    class Meta:
        model = ScheduleItem
        fields = ['id', 'lesson', 'lesson_detail', 'color']
        extra_kwargs = {
            'lesson': {'write_only': True},
        }


class SavedScheduleSerializer(serializers.ModelSerializer):
    items = ScheduleItemSerializer(many=True)

    class Meta:
        model = SavedSchedule
        fields = ['id', 'title', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        schedule = SavedSchedule.objects.create(user=user, **validated_data)
        for item_data in items_data:
            ScheduleItem.objects.create(schedule=schedule, **item_data)
        return schedule

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                ScheduleItem.objects.create(schedule=instance, **item_data)

        return instance


class ExcelUploadSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()
    excel_file = serializers.FileField()

    def validate_excel_file(self, value):
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("فرمت فایل باید اکسل باشد")
        return value