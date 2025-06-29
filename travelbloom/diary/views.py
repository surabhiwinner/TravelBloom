from django.shortcuts import render,redirect

from .forms import DiaryMediaForm ,DiaryEntryForm

from .models import DiaryEntry, DiaryMedia

from authentication.models import Profile

from django.conf import settings

from django.views import View

# Create your views here.


class DiaryEntryWriteView(View):

    def get(self, request, *args , **kwargs):

        entry_form = DiaryEntryForm()

        media_form = DiaryMediaForm()

        

        data = {
            'entry_form' : entry_form,
            'media_form' : media_form,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
        }

        return render(request, 'diary/create_entry.html', context=data)

    def post(self, request, *args , **kwargs):

        entry_form = DiaryEntryForm(request.POST)

        media_form = DiaryMediaForm(request.POST , request.FILES)

        if entry_form.is_valid() and media_form.is_valid() :

            #get profile
            profile = Profile.objects.get(user = request.user)

            # create diary entry
            diary_entry = entry_form.save(commit=False)

            diary_entry.profile = profile

            diary_entry.latitude = request.POST.get('latitude') or None

            diary_entry.longitude = request.POST.get('longitude') or None

            diary_entry.save()


            # create media file

            media_file = media_form.save(commit=False)

            media_form.diary = diary_entry

            media_file.save()

            return redirect('entry-list')
        

class DiaryListView(View):

    def get(self , request , *args , **kwargs):

        diary_entries = DiaryEntry.objects.all()

        data = { 'diary_entries' : diary_entries}

        return render(request,'diary/entry_list_page.html',context=data)

