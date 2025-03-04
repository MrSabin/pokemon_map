import folium

from django.http import HttpResponseNotFound, HttpRequest
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import localtime
from pokemon_entities.models import Pokemon, PokemonEntity
from django.core.exceptions import ObjectDoesNotExist

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    "https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision"
    "/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832"
    "&fill=transparent"
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    local_time = localtime()
    pokemons = Pokemon.objects.all()
    pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lt=local_time, disappeared_at__gt=local_time
    )

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        pokemon = pokemon_entity.pokemon
        image_url = request.build_absolute_uri(pokemon.photo.url)
        add_pokemon(
            folium_map,
            pokemon_entity.lat,
            pokemon_entity.lon,
            image_url,
        )

    pokemons_on_page = []

    for pokemon in pokemons:
        pokemons_on_page.append(
            {
                "pokemon_id": pokemon.id,
                "img_url": request.build_absolute_uri(pokemon.photo.url)
                if pokemon.photo
                else DEFAULT_IMAGE_URL,
                "title_ru": pokemon.title_ru,
            }
        )

    return render(
        request,
        "mainpage.html",
        context={
            "map": folium_map._repr_html_(),
            "pokemons": pokemons_on_page,
        },
    )


def show_pokemon(request, pokemon_id):
    local_time = localtime()

    pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    requested_pokemon = {
        "title_ru": pokemon.title_ru,
        "title_en": pokemon.title_en,
        "title_jp": pokemon.title_jp,
        "img_url": request.build_absolute_uri(pokemon.photo.url),
        "description": pokemon.description,
        "entities": pokemon.entities.filter(
            pokemon=pokemon, appeared_at__lt=local_time, disappeared_at__gt=local_time
        ).values(),
    }

    if pokemon.previous_evolution:
        requested_pokemon["previous_evolution"] = {
            "title_ru": pokemon.previous_evolution.title_ru,
            "pokemon_id": pokemon.previous_evolution.id,
            "img_url": request.build_absolute_uri(pokemon.previous_evolution.photo.url),
        }

    pokemon_next_evolution = pokemon.next_evolutions.first()

    if pokemon_next_evolution:
        requested_pokemon["next_evolution"] = {
            "title_ru": pokemon_next_evolution.title_ru,
            "pokemon_id": pokemon_next_evolution.id,
            "img_url": request.build_absolute_uri(pokemon_next_evolution.photo.url),
        }

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon["entities"]:
        add_pokemon(
            folium_map,
            pokemon_entity["lat"],
            pokemon_entity["lon"],
            requested_pokemon["img_url"],
        )

    return render(
        request,
        "pokemon.html",
        context={"map": folium_map._repr_html_(), "pokemon": requested_pokemon},
    )
