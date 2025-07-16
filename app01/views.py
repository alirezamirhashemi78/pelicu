from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, QueryDict
from django.db.models import QuerySet

from .models import Movie, Profile

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import math


def index(request: HttpRequest) -> HttpResponse:
    # Home page - display all movies and recommended movies
    movies: QuerySet = Movie.objects.all()
    recommended_movies = []
    if request.user.is_authenticated:
        recommended_movies: QuerySet = handle_recom(user=request.user)
    return render(request, 'index.html', {'movies': movies, "recommended_movies": recommended_movies})


def register_user(request: HttpRequest) -> HttpResponse:
    # Register a new user
    if request.method == 'POST':
        username: str = request.POST['username']
        email: str = request.POST['email']
        password1: str = request.POST['password1']
        password2: str = request.POST['password2']

        if password1 != password2:
            return redirect('register_user')

        if User.objects.filter(username=username).exists():
            return redirect('register_user')

        user: User = User.objects.create_user(username=username, password=password1, email=email)
        profile, created = Profile.objects.get_or_create(user=user)  # safer than create()

        login(request, user)
        return redirect('index')

    return render(request, 'register.html')


def login_user(request: HttpRequest) -> HttpResponse:
    # Log in a user
    if request.method == 'POST':
        username: str = request.POST['username']
        password: str = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
    return render(request, 'login.html')


def logout_user(request: HttpRequest) -> HttpResponse:
    # Log out the current user
    logout(request)
    return redirect('index')


@login_required
def view_profile(request: HttpRequest, username: str) -> HttpResponse:
    # Display user's profile
    if request.user.username == username:
        return render(request, 'profile.html')
    return HttpResponse()


def clean_data(x) -> str | list[str]:
    # Convert strings or lists to lowercase and remove spaces
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    if isinstance(x, str):
        return str.lower(x.replace(" ", ""))
    return ''


def create_soup(x: pd.Series) -> str:
    # Combine title and genres to create a text feature
    return x['title'] + x['genres']


def find_similars(df_movies: pd.DataFrame, indices: pd.Series, title: str, cosine_sim: pd.DataFrame) -> pd.Series:
    # Find similar movies for a given title
    if title not in indices:
        return pd.Series(dtype=int)
    idx: int = indices[title]
    sim_scores: list[tuple[int, float]] = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:5]
    movie_indices = [i[0] for i in sim_scores]
    return df_movies['id'].iloc[movie_indices]


def boost_movie(recommended_movies: list[dict], movie_id: int) -> dict:
    # Increase the score of a recommended movie
    movie = next(item for item in recommended_movies if item["id"] == movie_id)
    movie["score"] *= 1 + math.log(movie["score"] + 1)
    return movie


def get_ranked_similar_movies(
    df_movies: pd.DataFrame,
    indices: pd.Series,
    recommended_movies: list[dict],
    movie: str,
    cosine_sim: pd.DataFrame
) -> list[dict]:
    # Retrieve and rank similar movies for a given movie
    movie = clean_data(movie)
    similar_movie_ids = find_similars(df_movies, indices, movie, cosine_sim)

    for movie_id in similar_movie_ids:
        existing = next((m for m in recommended_movies if m["id"] == movie_id), None)
        if existing:
            boost_movie(recommended_movies, movie_id)
        else:
            recommended_movies.append({"id": movie_id, "score": 1})
    return recommended_movies


@login_required
def toggle_like_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    profile = request.user.profile

    if movie in profile.interested_movies.all():
        profile.interested_movies.remove(movie)
    else:
        profile.interested_movies.add(movie)
    
    return redirect('index')


def handle_recom(user):
    # Get all movies as DataFrame
    query_movies = Movie.objects.all().values(
        'id', 
        'title', 
        'year', 
        'duration_minutes', 
        'imdb_score',
        'genres'
    )
    df_movies = pd.DataFrame.from_records(query_movies)

    # Clean features
    features = ['title', 'genres']
    for feature in features:
        df_movies[feature] = df_movies[feature].apply(clean_data)

    # Create the soup for similarity
    df_movies['soup'] = df_movies.apply(create_soup, axis=1)

    # Vectorize soup and calculate cosine similarity
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(df_movies['soup'])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    df_movies = df_movies.reset_index()
    indices = pd.Series(df_movies.index, index=df_movies['title'])

    recommended_movies = []

    # Get the user's liked movies from profile
    try:
        profile = user.profile
        liked_movies = profile.interested_movies.all()
    except Profile.DoesNotExist:
        liked_movies = []

    # If user has liked movies, use them for recommendation
    if liked_movies:
        for movie in liked_movies:
            # Use movie title as input to find similar movies
            recommended_movies = get_ranked_similar_movies(
                df_movies, indices, recommended_movies, movie.title.lower(), cosine_sim
            )
    else:
        # Fallback recommendations if no likes: some defaults
        recommended_movies = get_ranked_similar_movies(df_movies, indices, recommended_movies, "frozen", cosine_sim)
        recommended_movies = get_ranked_similar_movies(df_movies, indices, recommended_movies, "kung fu panda", cosine_sim)

    # Sort and limit results
    recommended_movies = sorted(recommended_movies, key=lambda x: x["score"], reverse=True)[0:5]

    # Query recommended movies from DB
    recommended_movie_ids = [item["id"] for item in recommended_movies]
    query_recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)

    return query_recommended_movies