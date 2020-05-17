from src.music_utils.PlaylistHandler import PlaylistHandler
from src.network.OperationType import OperationType
from src.network.NetworkCommunication import *

_playlist_handler = PlaylistHandler()


def do_req(req, socket, address, log):
    if req[0] == OperationType.ALL_SONGS.name:
        _send_all_song_playlist(socket, log)
        return

    elif req[0] == OperationType.SEARCH.name:
        _search(req[1:], socket, log)
        return

    elif req[0] == OperationType.DISCONNECT.name:
        _disconnect(socket, address, log)
        return

    elif req[0] == OperationType.REQ_SONG.name:
        _send_song(req[1:], socket, log)
        return

    else:
        return


def _search(search, socket, log):
    # len\search\song(str)
    _send_song(search, socket, log)


def _send_song(song_to_play, socket, log):
    # len\send_song\song(str)
    song_to_play = song_to_play[0]
    index = 0
    for song in _playlist_handler.all_music.songs:
        if song.song_name.casefold().replace(' ', '') == song_to_play:
            break

        index += 1

    file = open(_playlist_handler.all_music.songs[index].file_name, "rb")
    print(_playlist_handler.all_music.songs[index].file_name)
    send_req(assemble_req(OperationType.REQ_SONG.name, str(file.read())), socket, log)
    file.close()


def _disconnect(socket, address, log):
    # len\disconnect
    log.write("{} disconnecting".format(address))
    socket.close()


def _send_all_song_playlist(socket, log):
    # len\all_songs
    send_req(assemble_req(OperationType.ALL_SONGS.name, _playlist_handler.all_music.string()), socket, log)
