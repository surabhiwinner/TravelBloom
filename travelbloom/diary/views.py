from django.shortcuts import render,redirect,get_object_or_404

from .forms import DiaryMediaForm ,DiaryEntryForm

from .models import DiaryEntry, DiaryMedia

from authentication.models import Profile

from django.conf import settings

from django.views import View

import mimetypes

from django.http import JsonResponse

from diary.models import DiaryMedia

from blog.models import BlogPost

# Create your views here.

from authentication.models import Traveller

from authentication.models import Traveller

class HomeView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'page': 'home-page',
        }

        if request.user.is_authenticated:
            try:
                traveller = Traveller.objects.get(profile=request.user)
                context['traveller'] = traveller

                print(traveller.uuid,'exist')
            except Traveller.DoesNotExist:
                context['traveller'] = None

                print(traveller.uuid,'not')
        else:
            context['traveller'] = None

            # print(traveller.uuid,'none')


        

        return render(request, 'diary/home.html', context)


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

    def post(self, request, *args, **kwargs):
        entry_form = DiaryEntryForm(request.POST)
        media_form = DiaryMediaForm(request.POST, request.FILES)

        if entry_form.is_valid() and media_form.is_valid():
            # Get the profile (your Profile is the User model)
            profile = request.user

            # Create diary entry
            diary_entry = entry_form.save(commit=False)

            diary_entry.profile = profile

            diary_entry.latitude = request.POST.get('latitude') or None

            diary_entry.longitude = request.POST.get('longitude') or None

            diary_entry.place_name = request.POST.get('place_name') or None

            diary_entry.save()

            # Handle multiple media files
            files = request.FILES.getlist('file')

            for f in files:

                media_type = detect_media_type(f)

                DiaryMedia.objects.create(
                    diary=diary_entry,
                    file=f,
                    media_type=media_type
                )

            return redirect('diary-list')

        # If invalid, show form again
        data = {
            'entry_form': entry_form,

            'media_form': media_form,

            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'diary/create_entry.html', context=data)


class DiaryListView(View):
    def get(self, request, *args, **kwargs):
        diary_entries = DiaryEntry.objects.none()  # default empty queryset

        if request.user.is_authenticated:
            profile = request.user
            if profile.role == 'User':
                diary_entries = DiaryEntry.objects.filter(profile=profile)
            elif profile.role =='Admin':
                diary_entries = DiaryEntry.objects.all()

        data = {
            'diary_entries': diary_entries,
            'page': 'diary-page'
        }
        return render(request, 'diary/entry_list_page.html', context=data)
 
class DiaryEntryDetailView(View):
    def get(self, request, uuid):
        diary_entry = get_object_or_404(DiaryEntry, uuid=uuid)
        diary_media  = diary_entry.media_files.all()  # related_name='media_files'
        context = {
            "diary_entry": diary_entry,
            "diary_media": diary_media,
            "page": "diary-page"
        }
        return render(request, "diary/entry_details.html", context)

# class HomeView(View):


#     def get(self, request, *args, **kwargs):

#         data = {
#             'page' : 'home-page'
#         }

#         return render(request,'diary/home.html',context=data)


class DiaryentryDeleteView(View):

    def get(self, request, *args , **kwargs) :

        uuid = kwargs.get('uuid')

        diary_entry = DiaryEntry.objects.get(uuid=uuid)

        diary_entry.delete()

        return redirect('diary-list')
    
def detect_media_type(file):

    mime_type, _ = mimetypes.guess_type(file.name)
    if mime_type :
        if mime_type.startswith('image'):

            return 'Image'
        elif mime_type.startswith('video'):

            return 'Video'
        
    return 'Unknown'
    

class ChatView(View):
    def get(self, request):

        return render(request,'diary/chatbot.html')
    
class ChatMessageView(View):

    def post(self, request):

        user_msg = request.POST.get('message','')

        # basic rule-based bot

        if 'hello' in user_msg.lower():

            bot_response = "Hi there! How can I help with your trip?"

        elif 'trip' in user_msg.lower():

            bot_response = "Are you planning a new trip or checking past ones?"
        else:
            bot_response = "I'm not sure how to respond to that yet 😅"

        
        return JsonResponse({'response' : bot_response})
    

class ContactView(View):

    def get(self, request, *args, **kwargs):


        return render(request, 'diary/contact.html',context={'page' : 'contact-page'})

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Optional: Store/save/send email/etc.
        print(f"Contact form submitted by {name} ({email}): {message}")

        messages.success(request, "Thank you for contacting us. We'll get back to you soon.")
        return redirect('contact')


class GalleryView(View):
    def get(self, request):
        if request.user.is_authenticated:
            diary_photos = DiaryMedia.objects.filter(diary__profile=request.user).order_by('-created_at')
        else:
            diary_photos = []

        blog_photos = BlogPost.objects.exclude(image='').order_by('-created_at')

        context = {
            'diary_photos': diary_photos,
            'blog_photos': blog_photos,
        }

        return render(request, 'diary/gallery.html', context)


class AboutPageView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "page": "about-page",  # optional for navbar highlighting
        }
        return render(request, 'diary/about.html', context)