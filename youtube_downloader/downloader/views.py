import yt_dlp
from django.http import HttpResponse, FileResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
import os
from django.utils.encoding import iri_to_uri
from django.conf import settings
from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
import json
import random
import string

client_secret = {
    "web": {
        "client_id": "510825766562-2vpu5l9t9dlnu45bso5f32ohvellkm23.apps.googleusercontent.com",
        "project_id": "download-youtube-439301",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost:8000", "https://youtube-downloader-ym2g.onrender.com"],
        "javascript_origins": ["http://localhost:8000"]
    }
}

def home(request):
    # Verifica si el usuario ya tiene credenciales guardadas en la sesión
    if 'credentials' not in request.session:
        return redirect('oauth2callback')  # Redirige a la página de login si no está autenticado

    credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])
    
    # Aquí puedes usar las credenciales para hacer algo con la API de YouTube, si es necesario.

    return render(request, 'home.html')  # Renderiza tu plantilla principal

def oauth2_login_or_callback(request):
    # Verifica si el usuario ya tiene credenciales guardadas en la sesión
    if 'credentials' in request.session:
        return redirect('home')  # Redirige a la página de inicio si ya está autenticado

    client_secrets_file = os.path.join(os.path.dirname(__file__), './client_secret.json')
    
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=['https://www.googleapis.com/auth/youtube.readonly'],
        redirect_uri=settings.REDIRECT_URI  # Asegúrate de que esto sea HTTPS
    )

    if 'code' in request.GET:
        state = request.session.get('state')
        if state is None:
            return HttpResponseBadRequest("No se pudo encontrar el estado en la sesión.")

        flow.fetch_token(authorization_response=request.build_absolute_uri())

        credentials = flow.credentials
        request.session['credentials'] = credentials_to_dict(credentials)

        return redirect('home')

    state = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    request.session['state'] = state

    authorization_url, _ = flow.authorization_url(state=state)
    
    return redirect(authorization_url)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# Aquí puedes agregar tus otras funciones como download_mp3, etc.




TEMP_FOLDER = "./descargas"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

def download_mp3(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')
        nombre = request.POST.get('nombre')
        
        titulo = ''
        if nombre  == '':
            titulo = f'{TEMP_FOLDER}/%(title)s.%(ext)s'
        else:
            titulo = f'{TEMP_FOLDER}/{nombre}.%(ext)s'

        ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{titulo}',  # especifica la ubicación y nombre del archivo
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            safe_filename = iri_to_uri(os.path.basename(filename))
            # Asegurarnos de que el archivo existe y puede abrirse
            if os.path.exists(filename):
                response = FileResponse(open(filename, 'rb'), content_type='audio/mpeg')
                response['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}"
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'

                print(response.items())

                return response
            else:
                return HttpResponse("El archivo no se pudo encontrar.", status=404)

        except Exception as e:
            # Si algo sale mal, capturar el error y devolverlo como respuesta
            return HttpResponse(f"Error al procesar la descarga: {str(e)}", status=500)

    return render(request, template_name='download.html')
