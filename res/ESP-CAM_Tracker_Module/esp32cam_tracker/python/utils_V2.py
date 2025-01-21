import pygame

def fill(surface, position, fill_color):
    fill_color = surface.map_rgb(fill_color)  # Convert the color to mapped integer value.
    surf_array = pygame.surfarray.pixels2d(surface)  # Create an array from the surface.
    current_color = surf_array[position]  # Get the mapped integer color value.

    # 'frontier' is a list where we put the pixels that's we haven't checked. Imagine that we first check one pixel and 
    # then expand like rings on the water. 'frontier' are the pixels on the edge of the pool of pixels we have checked.
    #
    # During each loop we get the position of a pixel. If that pixel contains the same color as the ones we've checked
    # we paint it with our 'fill_color' and put all its neighbours into the 'frontier' list. If not, we check the next
    # one in our list, until it's empty.

    frontier = [position]
    while len(frontier) > 0:
        x, y = frontier.pop()
        try:  # Add a try-except block in case the position is outside the surface.
            if surf_array[x, y] != current_color:
                continue
        except IndexError:
            continue
        surf_array[x, y] = fill_color
        # Then we append the neighbours of the pixel in the current position to our 'frontier' list.
        frontier.append((x + 1, y))  # Right.
        frontier.append((x - 1, y))  # Left.
        frontier.append((x, y + 1))  # Down.
        frontier.append((x, y - 1))  # Up.

    pygame.surfarray.blit_array(surface, surf_array)