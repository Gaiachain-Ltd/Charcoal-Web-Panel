from django import forms
from django.core.exceptions import ValidationError

from apps.additional_data.models import Village, Producer, Parcel


class ProducerAdminUploadForm(forms.Form):
    csv_file = forms.FileField()


class ProducersAdminUploadDataForm(forms.Form):
    village = forms.CharField(max_length=100)
    producer_code = forms.CharField(max_length=20)
    producer_name = forms.CharField(max_length=100)
    parcel = forms.CharField(max_length=20)

    def clean(self):
        village, _ = Village.objects.get_or_create(
            name=self.cleaned_data['village']
        )
        producer, _ = Producer.objects.get_or_create(
            name=self.cleaned_data['producer_name'],
            pid=self.cleaned_data['producer_code'],
            village=village
        )
        parcel, _ = Parcel.objects.get_or_create(
            pid=self.cleaned_data['parcel'],
            producer=producer
        )
