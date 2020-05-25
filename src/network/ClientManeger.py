from src.music_utils.PlayQueue import PlayQueue, State
from src.music_utils.PlaylistHandler import PlaylistHandler
from src.music_utils.Song import Playlist, Song
from src.network.NetworkCommunication import *
from src.network.OperationType import OperationType


from src.utils.Constants import GUIFiles

server_songs = Playlist()
my_songs = PlaylistHandler("Downloads").music
play_queue = PlayQueue()

gui_src = None
socket = None
log = None
is_online = None


def init(sock, logger, online):
    global socket
    socket = sock
    global log
    log = logger
    global gui_src
    gui_src = GUIFiles(log)
    global is_online
    is_online = online


def get_all_server_songs():
    send_req(assemble_req(OperationType.ALL_SONGS.name), socket, log)
    server_msg_raw = recv_req(socket, log)
    server_msg_raw = server_msg_raw[len(OperationType.ALL_SONGS.name) + len(SEPARATOR_CHAR) + 1: len(server_msg_raw) - len(SEPARATOR_CHAR)]
    server_msg_raw = server_msg_raw.replace("'", "")

    global server_songs
    server_songs.conv_to_obj(playlist=server_msg_raw.split(","), name="ServerAllSongs")


def search_song(search):
    search = search.replace(" ", '').casefold()
    send_req(assemble_req(OperationType.SEARCH.name, search), socket, log)
    stream_song(search)


def disconnect():
    send_req(assemble_req(OperationType.DISCONNECT.name), socket, log)
    play_queue.delete_cache()


def stream_song(search):
    if search == play_queue.current.song_name.replace(" ", '').casefold():
        return

    s_bytes = recv_req(socket, log, decode=False)
    file = play_queue.manege_cache()
    file.write(s_bytes)
    path = file.name

    song = None
    for p_song in server_songs.songs:
        if p_song.song_name.replace(' ', '').casefold() in search:
            song = Song(path)
            song.song_name = p_song.song_name
            song.artist = p_song.artist
            break

    play_queue.set_current_song(song)
    play_queue.set_state(State.PLAY)


def req_song(song_index):
    send_req(assemble_req(OperationType.REQ_SONG, song_index))
    s_bytes = recv_req(socket, log, decode=False)

    file = play_queue.manege_cache(unload=False)
    file.write(s_bytes)
    path = file.name

    song = Song(path)
    song.song_name = server_songs[song_index].song_name
    song.artist = server_songs[song_index].artist

    play_queue.set_next(path)

