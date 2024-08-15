from rest_framework import serializers
from user.models import User, Contact, SpamReport
class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField( required=False, allow_blank=True)
    name = serializers.CharField(max_length=255, read_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value
    
    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name') if data.get('last_name') else ''
        name = f'{first_name} {last_name}'.strip()
        data['name'] = name
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ContactSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=15)
    spam_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Contact
        fields = ['id', 'phone_number', 'name', 'spam_count']

class SpamReportSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    reporter = serializers.PrimaryKeyRelatedField(read_only=True)
    phone_number = serializers.CharField(max_length=15)

    class Meta:
        model = SpamReport
        fields = ['id', 'reporter', 'phone_number', 'reported_at']

    def validate(self, data):
        """Custom validation to ensure the same user doesn't report the same number twice."""
        reporter = self.context['request'].user
        phone_number = data.get('phone_number')

        if SpamReport.objects.filter(reporter=reporter, phone_number=phone_number).exists():
            raise serializers.ValidationError("You have already reported this contact as spam.")

        return data

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        reporter = self.context['request'].user

        # Retrieve or create the contact
        contact, created = Contact.objects.get_or_create(phone_number=phone_number)
        
        # Increment the spam count
        contact.spam_count += 1
        contact.save()

        # Create the spam report
        spam_report = SpamReport.objects.create(reporter=reporter, phone_number=phone_number)
        
        return spam_report
