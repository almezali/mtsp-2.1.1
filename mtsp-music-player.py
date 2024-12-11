#!/usr/bin/env python3
# MTSP - Multimedia Terminal Soundtrack Player

import os
import sys
import time
import argparse
import sqlite3
import random
import mutagen
from typing import List, Dict
import subprocess
import threading

class ShellMusicPlayer:
    def __init__(self, music_dir=None):
        """Initialize the music player"""
        # Home directory for configuration and database
        self.home_dir = os.path.expanduser("~/.shell_music_player")
        os.makedirs(self.home_dir, exist_ok=True)

        # Database setup
        self.db_path = os.path.join(self.home_dir, "music_library.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_database()

        # Music directory
        self.music_dir = music_dir or os.path.expanduser("~/Music")
        
        # Playback state
        self.current_playlist = []
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False

        # Player process
        self.player_process = None

    def _create_database(self):
        """Create database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                filename TEXT,
                artist TEXT,
                album TEXT,
                duration REAL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                playlist_id INTEGER,
                track_id INTEGER,
                FOREIGN KEY(playlist_id) REFERENCES playlists(id),
                FOREIGN KEY(track_id) REFERENCES tracks(id)
            )
        ''')
        self.conn.commit()

    def scan_music_library(self):
        """Scan music directory and add tracks to database"""
        supported_formats = ('.mp3', '.wav', '.flac', '.ogg', '.m4a')
        tracks_added = 0

        for root, _, files in os.walk(self.music_dir):
            for file in files:
                if file.lower().endswith(supported_formats):
                    full_path = os.path.join(root, file)
                    
                    # Check if track already exists
                    self.cursor.execute("SELECT id FROM tracks WHERE path = ?", (full_path,))
                    if self.cursor.fetchone():
                        continue

                    # Extract metadata
                    try:
                        metadata = mutagen.File(full_path, easy=True)
                        artist = metadata.get('artist', ['Unknown Artist'])[0]
                        album = metadata.get('album', ['Unknown Album'])[0]
                        duration = metadata.get('length', 0)
                    except Exception:
                        artist = 'Unknown Artist'
                        album = 'Unknown Album'
                        duration = 0

                    # Insert track
                    self.cursor.execute('''
                        INSERT INTO tracks (path, filename, artist, album, duration)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (full_path, file, artist, album, duration))
                    tracks_added += 1

        self.conn.commit()
        return tracks_added

    def get_tracks(self, limit=50, offset=0, search=None, order_by='filename', sort='ASC'):
        """Retrieve tracks from database with sorting and searching"""
        query = "SELECT id, path, filename, artist, album, duration FROM tracks"
        params = []

        if search:
            query += " WHERE filename LIKE ? OR artist LIKE ? OR album LIKE ?"
            search_param = f"%{search}%"
            params = [search_param, search_param, search_param]

        # Add ORDER BY clause with user-specified column and sort direction
        valid_columns = ['id', 'filename', 'artist', 'album', 'duration']
        if order_by in valid_columns:
            query += f" ORDER BY {order_by} {sort}"

        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def display_tracks(self, tracks):
        """Display tracks in a formatted table"""
        # Define column widths
        col_widths = {
            'ID': 5,
            'Filename': 30,
            'Artist': 20,
            'Album': 20,
            'Duration': 10
        }

        # Print header
        header_format = "{:<{id_width}} {:<{filename_width}} {:<{artist_width}} {:<{album_width}} {:<{duration_width}}"
        print(header_format.format(
            'ID', 'Filename', 'Artist', 'Album', 'Duration (s)',
            id_width=col_widths['ID'],
            filename_width=col_widths['Filename'],
            artist_width=col_widths['Artist'],
            album_width=col_widths['Album'],
            duration_width=col_widths['Duration']
        ))
        
        # Print separator
        print('-' * (sum(col_widths.values()) + len(col_widths) * 3))

        # Print tracks
        for track in tracks:
            print(header_format.format(
                track[0],
                track[2][:col_widths['Filename']-3] + '...' if len(track[2]) > col_widths['Filename'] else track[2],
                track[3][:col_widths['Artist']-3] + '...' if len(track[3]) > col_widths['Artist'] else track[3],
                track[4][:col_widths['Album']-3] + '...' if len(track[4]) > col_widths['Album'] else track[4],
                f"{track[5]:.2f}" if track[5] else "N/A",
                id_width=col_widths['ID'],
                filename_width=col_widths['Filename'],
                artist_width=col_widths['Artist'],
                album_width=col_widths['Album'],
                duration_width=col_widths['Duration']
            ))

    def play(self, tracks=None):
        """Play tracks"""
        if tracks:
            self.current_playlist = tracks
            self.current_track_index = 0

        if not self.current_playlist:
            print("No tracks to play.")
            return

        # Stop any existing playback
        self.stop()

        # Play current track
        current_track = self.current_playlist[self.current_track_index]
        try:
            # Use mpv for playback
            self.player_process = subprocess.Popen([
                'mpv', current_track[1],  # Use full path
                '--no-video',
                '--terminal=no'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.is_playing = True
            print(f"Now playing: {current_track[2]} - {current_track[3]}")
        except Exception as e:
            print(f"Error playing track: {e}")

    def pause(self):
        """Pause playback"""
        if self.player_process:
            self.player_process.send_signal(subprocess.signal.SIGSTOP)
            self.is_paused = True
            print("Playback paused.")

    def resume(self):
        """Resume playback"""
        if self.player_process and self.is_paused:
            self.player_process.send_signal(subprocess.signal.SIGCONT)
            self.is_paused = False
            print("Playback resumed.")

    def stop(self):
        """Stop playback"""
        if self.player_process:
            try:
                self.player_process.terminate()
                self.player_process.wait()
            except Exception:
                pass
            
            self.player_process = None
            self.is_playing = False
            self.is_paused = False
            print("Playback stopped.")

    def next_track(self):
        """Play next track in playlist"""
        if not self.current_playlist:
            return

        self.current_track_index = (self.current_track_index + 1) % len(self.current_playlist)
        self.play()

    def previous_track(self):
        """Play previous track in playlist"""
        if not self.current_playlist:
            return

        self.current_track_index = (self.current_track_index - 1) % len(self.current_playlist)
        self.play()

    def shuffle_playlist(self):
        """Shuffle current playlist"""
        if self.current_playlist:
            random.shuffle(self.current_playlist)
            print("Playlist shuffled.")

    def interactive_shell(self):
        """Interactive shell interface"""
        print("MTSP - Multimedia Terminal Soundtrack Player")
        print("Type 'help' for available commands")

        while True:
            try:
                command = input("mtsp> ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()

                if cmd == 'scan':
                    tracks = self.scan_music_library()
                    print(f"Added {tracks} new tracks to library")
                
                elif cmd == 'list':
                    # Allow sorting and limiting
                    order_by = command[1] if len(command) > 1 else 'filename'
                    sort = command[2] if len(command) > 2 else 'ASC'
                    tracks = self.get_tracks(limit=20, order_by=order_by, sort=sort)
                    self.display_tracks(tracks)
                
                elif cmd == 'play':
                    if len(command) > 1:
                        # Play specific tracks or playlist
                        tracks = [self.get_tracks(limit=1, offset=int(command[1])-1)[0]]
                    else:
                        # Get random tracks to play
                        tracks = self.get_tracks(limit=10)
                    self.play(tracks)
                
                elif cmd == 'pause':
                    self.pause()
                
                elif cmd == 'resume':
                    self.resume()
                
                elif cmd == 'stop':
                    self.stop()
                
                elif cmd == 'next':
                    self.next_track()
                
                elif cmd == 'prev':
                    self.previous_track()
                
                elif cmd == 'shuffle':
                    self.shuffle_playlist()
                
                elif cmd == 'search':
                    if len(command) > 1:
                        tracks = self.get_tracks(search=' '.join(command[1:]))
                        self.display_tracks(tracks)
                
                elif cmd == 'help':
                    print("""
Available commands:
  scan                  - Scan music library
  list [col] [sort]     - List tracks (optional: sort column, sort order)
  play [id]             - Play tracks (optional: start from track ID)
  pause                 - Pause playback
  resume                - Resume playback
  stop                  - Stop playback
  next                  - Next track
  prev                  - Previous track
  shuffle               - Shuffle playlist
  search [term]         - Search tracks
  help                  - Show this help
  exit                  - Exit application
""")
                
                elif cmd == 'exit':
                    break
                
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="MTSP - Multimedia Terminal Soundtrack Player")
    parser.add_argument('-d', '--dir', help="Music directory path")
    args = parser.parse_args()

    player = ShellMusicPlayer(music_dir=args.dir)
    player.interactive_shell()

if __name__ == "__main__":
    main()
