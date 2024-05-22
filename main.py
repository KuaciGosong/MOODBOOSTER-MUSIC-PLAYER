import PySimpleGUI as sg
import os
import pygame
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
import json

# Inisialisasi Pygame mixer
pygame.mixer.init()

# Fungsi untuk memutar musik
def play_music(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Fungsi untuk menghentikan musik
def stop_music():
    pygame.mixer.music.pause()

# Fungsi untuk melanjutkan musik
def resume_music():
    pygame.mixer.music.unpause()

# Fungsi untuk memeriksa apakah musik sedang diputar
def is_music_playing():
    return pygame.mixer.music.get_busy()

# Warna tema
background_color = '#191414'
text_color = '#1DB954'
input_background_color = '#191414'
input_text_color = '#FFFFFF'
button_color = ('#FFFFFF', '#1DB954')

# Layout PySimpleGUI
layout = [
    [sg.Image(filename='logo.png', pad=((0, 0), (10, 0))), sg.Push(background_color=background_color), sg.Text('Tidak ada lagu yang diputar', key='-SONG_STATUS-', background_color=background_color, text_color=text_color)],
    [sg.Column([
        [sg.Text('', size=(30, 1), key='-PLAYLIST_NAME-', background_color=background_color, text_color=text_color)],
        [sg.Listbox(values=[], size=(36, 15), key='-PLAYLIST-', enable_events=True, background_color=input_background_color, text_color=input_text_color)],
        [sg.Button('+', key='-ADD-', size=(3, 1), button_color=button_color),
         sg.Button('-', key='-REMOVE-', size=(3, 1), button_color=button_color),
         sg.Button('↑', key='-MOVE_UP-', size=(3, 1), button_color=button_color),
         sg.Button('↓', key='-MOVE_DOWN-', size=(3, 1), button_color=button_color)],
        [sg.Button('Simpan Playlist', key='-SAVE_PLAYLIST-', size=(15, 1), button_color=button_color),
         sg.Button('Buka Playlist', key='-LOAD_PLAYLIST-', size=(15, 1), button_color=button_color)]
    ], background_color=background_color),
    sg.Column([
        [sg.Image(filename='album.png', key='-ALBUM_ART-', size=(146, 135), pad=((75, 0), (0, 10)))],
        [sg.Button(image_filename='previous.png', key='-PREVIOUS-', pad=(20, 10), button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0),
         sg.Button(image_filename='play.png', key='-PLAY-', pad=(20, 10), button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0),
         sg.Button(image_filename='next.png', key='-NEXT-', pad=(20, 10), button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
        [sg.Text('Informasi Lagu', background_color=background_color, text_color=text_color)],
        [sg.Text('Judul Lagu', size=(10, 1), background_color=background_color, text_color=text_color), sg.InputText(key='-TITLE-', size=(25, 1), background_color=input_background_color, text_color=input_text_color)],
        [sg.Text('Artis', size=(10, 1), background_color=background_color, text_color=text_color), sg.InputText(key='-ARTIST-', size=(25, 1), background_color=input_background_color, text_color=input_text_color)],
        [sg.Text('Album', size=(10, 1), background_color=background_color, text_color=text_color), sg.InputText(key='-ALBUM-', size=(25, 1), background_color=input_background_color, text_color=input_text_color)],
    ], background_color=background_color),]
]

# Inisialisasi window
window = sg.Window('MoodBooster Music Player', layout, finalize=True, background_color=background_color)

# Daftar playlist dan informasi lagu
playlist = []
song_infos = {}
current_playlist = ""  # Variabel untuk menyimpan nama playlist yang sedang terbuka

# Indeks lagu saat ini yang sedang diputar
current_index = 0

# Fungsi untuk menyimpan playlist
def save_playlist(playlist, file_path):
    playlist_data = {
        "playlist": playlist
    }
    with open(file_path, 'w') as file:
        json.dump(playlist_data, file)

# Fungsi untuk memuat playlist
def load_playlist(file_path):
    with open(file_path, 'r') as file:
        playlist_data = json.load(file)
        return playlist_data["playlist"]
    
# Fungsi untuk memuat dan memutar musik
def load_and_play_music(file_path):
    global current_index
    current_index = playlist.index(file_path)
    audio = mutagen.File(file_path)
    title = audio.get('TIT2', 'Unknown Title')
    artist = audio.get('TPE1', 'Unknown Artist')
    album = audio.get('TALB', 'Unknown Album')
    window['-TITLE-'].update(title)
    window['-ARTIST-'].update(artist)
    window['-ALBUM-'].update(album)
    window['-SONG_STATUS-'].update(f"Sedang memutar: {title} - {artist}")
    play_music(file_path)

# Fungsi untuk menyimpan metadata
def save_metadata(file_path):
    audio = ID3(file_path)
    audio['TIT2'] = TIT2(encoding=3, text=window['-TITLE-'].get())
    audio['TPE1'] = TPE1(encoding=3, text=window['-ARTIST-'].get())
    audio['TALB'] = TALB(encoding=3, text=window['-ALBUM-'].get())
    
    if window['-ALBUM_ART-'].get():
        window['-ALBUM_ART-'].get().save("temp.jpg")
        with open("temp.jpg", "rb") as img:
            audio['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=img.read())
    audio.save()

    if os.path.exists("temp.jpg"):
        os.remove("temp.jpg")

# Event loop PySimpleGUI
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == '-ADD-':
        file_path = sg.popup_get_file('Pilih File Musik', file_types=(("Audio Files", "*.mp3;*.wav"),))
        if file_path:
            playlist.append(file_path)
            window['-PLAYLIST-'].update(playlist)
    elif event == '-REMOVE-':
        selected = values['-PLAYLIST-']
        if selected:
            for item in selected:
                playlist.remove(item)
            window['-PLAYLIST-'].update(playlist)
    elif event == '-MOVE_UP-':
        selected = values['-PLAYLIST-']
        if selected:
            for item in selected:
                index = playlist.index(item)
                if index > 0:
                    playlist[index], playlist[index - 1] = playlist[index - 1], playlist[index]
            window['-PLAYLIST-'].update(playlist)
    elif event == '-MOVE_DOWN-':
        selected = values['-PLAYLIST-']
        if selected:
            for item in selected:
                index = playlist.index(item)
                if index < len(playlist) - 1:
                    playlist[index], playlist[index + 1] = playlist[index + 1], playlist[index]
            window['-PLAYLIST-'].update(playlist)
    elif event == '-PLAYLIST-':
        if values['-PLAYLIST-']:
            if not is_music_playing():
                load_and_play_music(values['-PLAYLIST-'][0])
    elif event == '-PLAY-':
        if is_music_playing():
            stop_music()
        else:
            if values['-PLAYLIST-']:
                if current_index < len(playlist):
                    resume_music()
                else:
                    load_and_play_music(playlist[0])
    elif event == '-PREVIOUS-':
        if playlist:
            if current_index > 0:
                stop_music()
                current_index -= 1
                load_and_play_music(playlist[current_index])
            else:
                stop_music()
                current_index = len(playlist) - 1
                load_and_play_music(playlist[current_index])
    elif event == '-NEXT-':
        if playlist:
            if current_index < len(playlist) - 1:
                stop_music()
                current_index += 1
                load_and_play_music(playlist[current_index])
            else:
                stop_music()
                current_index = 0
                load_and_play_music(playlist[current_index])
    elif event == '-LOAD_PLAYLIST-':
        file_path = sg.popup_get_file('Pilih Playlist', file_types=(("Playlist Files", "*.json"),))
        if file_path:
            playlist = load_playlist(file_path)
            window['-PLAYLIST-'].update(playlist)
            window['-PLAYLIST_NAME-'].update(f"Playlist Terbuka: {os.path.basename(file_path)}")
            current_playlist = file_path
    elif event == '-SAVE_PLAYLIST-':
        file_path = sg.popup_get_file('Simpan Playlist', save_as=True, file_types=(("Playlist Files", "*.json"),))
        if file_path:
            save_playlist(playlist, file_path)
            window['-PLAYLIST_NAME-'].update(f"Playlist Terbuka: {os.path.basename(file_path)}")

    elif event == '-SAVE_CHANGES-':
        selected = values['-PLAYLIST-']
        if selected:
            file_path = selected[0]
            song_infos[file_path] = {
                "title": window['-TITLE-'].get(),
                "artist": window['-ARTIST-'].get(),
                "album": window['-ALBUM-'].get(),
                "album_art": window['-ALBUM_ART-'].get()
            }
            save_metadata(file_path)

window.close()
       
