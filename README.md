# Pinsplorer

## Prerequisites

- python
- Pillow (python -m pip install pillow)

## Objectives

Create a fun way to explorer locally saved images, primarily intended for
browsing locally saved Pinterest images for inspiration.

### Functional Requirements

- User should be able to select a folder
- A Gallery view with thumbnails containing all the images of the selected
  folder
  - A randomize button that will randomize the order of the images
  - A button to select order (filename ascending or desc)
  - Should handle 8K+ images (upper estimate 50K in future) and still have good
    performance
- Image view (Clicking an image should display it in full screen)
  - should be contained in the app window
  - should have arrow buttons to go to the previous or next image
  - Full screen can be exited by clicking on the black around the image or
    pressing esc
- be able to resize the scale of the thumbnail
