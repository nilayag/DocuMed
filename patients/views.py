from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Medication, Documents,PatientUser
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import PatientRegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from doctors.models import DoctorUser, SharedDocument
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def home(request):
     user = request.user
     if PatientUser.objects.filter(user=user).exists():
      return render(request, 'patients/pathome.html')
     else:
         return redirect('home')


def RegisterPatient(request):
    if request.method=="POST":
         form = PatientRegisterForm(request.POST)
         if form.is_valid():
             user_instance = form.save()
             patient_user = PatientUser.objects.create(user=user_instance,phone_number = form.cleaned_data['phone_number'],age = form.cleaned_data['age'],name = form.cleaned_data['name'],gender = form.cleaned_data['gender'],blood_group = form.cleaned_data['blood_group'])
             #messages.success(request,f'Account created for {username}')
             return redirect('home')
    else:
         form = PatientRegisterForm()
    return render(request,'patients/patientreg.html',{'form':form})

"""
@login_required
def redirect_user(request):
    user = request.user

    # Check if the user is a doctor
    if PatientUser.objects.filter(user=user).exists():
        return render(request,'patients/pathome.html')

    # If user is not a doctor or patient, redirect to a generic dashboard or homepage
    else:
        return redirect('home')
"""


class UploadMedication(LoginRequiredMixin, CreateView):
    model = Medication
    fields = ['medical_condition', 'medicines', 'file']
    success_url = reverse_lazy('medupload')
    login_url = '/patient/login/' 

    def form_valid(self, form):
        form.instance.author = self.request.user.patientuser
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medications'] = Medication.objects.all()
        return context
    
class UploadDocuments(LoginRequiredMixin, CreateView):
    model = Documents
    fields = ['file']
    success_url = reverse_lazy('patient:docupload')
    login_url = '/patient/login/'
    
    def form_valid(self, form):
        form.instance.author = self.request.user.patientuser
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = Documents.objects.all()
        return context
    
    
@login_required
def share_documents(request):
    patient = request.user.patientuser
    documents = Documents.objects.filter(author=patient)
    doctors = DoctorUser.objects.all()

    if request.method == 'POST':
        selected_doctors = request.POST.getlist('doctors')
        selected_documents = request.POST.getlist('documents')

        for doctor_id in selected_doctors:
            doctor = DoctorUser.objects.get(id=doctor_id)
            for document_id in selected_documents:
                document = Documents.objects.get(id=document_id, author=patient)
                SharedDocument.objects.create(document=document, doctor=doctor, patient=patient)

        return redirect('patient:patient-home')

    return render(request, 'patients/share_documents.html', {'documents': documents, 'doctors': doctors})
