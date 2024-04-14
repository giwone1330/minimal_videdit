# minimal_videdit

minimalistic video editor in python

## Usage

1. install [ffmpeg](https://www.ffmpeg.org/)
2. prepare a python venv with requirements installed (_developed using python=3.12_)
3. place video in `videos` folder (_tested with .mp4_)
4. run `main.py`
5. navigate video using `j`, `l` keys, play and pause using `o`, `p`
6. control target area using `wasd` and `arrow_keys`
7. `c` changes rectangle color
8. `x` performs _crop_ operation to the selected area for the whole video
9. `v` perfoms _mask_ operation to the selected area for the whole video (_color of the mask depends on the rectangle color_)
10. output video is saved back in `videos` folder
