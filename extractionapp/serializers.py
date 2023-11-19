from rest_framework import serializers
from .models import UrlState


class DataContentSerializer(serializers.ModelSerializer):
    extracted_content = serializers.JSONField()

    class Meta:
        model = UrlState
        fields = ['id', 'url', 'time_fetched', 'fetch_status','extracted_content']

    def to_representation(self, instance):
        display_extracted = self.context.get("display_extracted")
        ret = super().to_representation(instance)
        if display_extracted and instance.extracted_content:
            ret['extracted_content'] = instance.extracted_content
        else:
            ret['extracted_content'] = None
        return ret
