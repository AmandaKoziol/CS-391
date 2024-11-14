import spotipy
import config
import openai
import json
import argparse

# API Token
openai.api_key = config.OPENAI_API_KEY

sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id = config.SPOTIFY_CLIENT_ID,
        client_secret = config.SPOTIFY_CLIENT_SECRET,
        redirect_uri="http://127.0.0.1:8080"
    )
)

current_user = sp.current_user()
print(current_user)

parser = argparse.ArgumentParser(description="Generate a playlist based on a prompt")
parser.add_argument("-p", type=str, help="The prompt to generate the playlist")
parser.add_argument("-n", type=int, default=8, help="The number of songs in the playlist")
args = parser.parse_args()


def generate_playlist(prompt, count=8):
    example_json = """
    [
        {"song": "Someone Like You", "artist": "Adele"},
        {"song": "Skinny Love", "artist": "Bon Iver"},
        {"song": "Hurt", "artist": "Johnny Cash"},
        {"song": "Back to December", "artist": "Taylor Swift"},
        {"song": "Say Something", "artist": "A Great Big World, Christina Aguilera"}
    ]
    """
    messages = [
        {"role": "system", "content": """You are a helpful playlist generating assistant. \
            You should generate a list of songs and their artists according to a text prompt. \
            You should return a JSON array, where each element follows this format: \
            {"song": <song_title>, "artist": <artist_name>}"""
        },
        {"role": "user", "content": f"Generate a playlist of 5 songs based on this prompt: super super sad songs"},
        {"role": "assistant", "content": example_json},
        {"role": "user", "content": f"Generate a playlist of {count} songs based on this prompt: {prompt}"}
    ]

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=400
    )

    playlist = json.loads(response.choices[0].message.content)
    return playlist

playlist = generate_playlist(args.p, args.n)

print(playlist)

sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config.SPOTIFY_CLIENT_ID,
        client_secret=config.SPOTIFY_CLIENT_SECRET,
        redirect_uri="http://127.0.0.1:8080",
        scope="playlist-modify-private"
    )
)
current_user = sp.current_user()
#create an empty list of track ids
track_ids = []

# Search for each song in the playlist and get the track id
for item in playlist:
    artist, song = item["artist"], item["song"]
    query = f"{song} {artist}" 
    search_results = sp.search(q=query, type="track", limit=10)
    track_ids.append(search_results["tracks"]["items"][0]["id"])

# Create a playlist 
created_playlist = sp.user_playlist_create(
    user=current_user["id"],
    name=args.p,
    public=False
)

# Add track ids to the playlist
sp.user_playlist_add_tracks(
    current_user["id"],
    created_playlist["id"],
    track_ids  
)