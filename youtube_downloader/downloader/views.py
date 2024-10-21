import yt_dlp
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
import os
from django.utils.encoding import iri_to_uri



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
