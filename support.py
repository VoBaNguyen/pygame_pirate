import os
import pygame
from csv import reader


def import_folder(path):
    surface_list = []

    for _, _, img_files in os.walk(path):
        for image in img_files:
            image_path = os.path.join(path, image)
            image_surface = pygame.image.load(image_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list


def import_csv_layout(path):
    terrain_map = []
    with open(path, "r") as map:
        level = reader(map, delimiter=",")
        for row in level:
            terrain_map.append(list(row))

    return terrain_map
