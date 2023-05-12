# musicAI

## Music Score Visualization
### Project Dependencies
 - `pyglet`
 - `numpy`
 - `scipy`
 - `python-dotenv`

## Quick Start
#### Installing Dependencies

To install dependencies, run `musicai/install.sh`.

### Running the Application

To run the application, run the `musicai/visualization/main.py`.

To load and visualize a score:
```python
file = './example.musicxml'
score = MusicXML.load(file)
window = ScoreWindow(score, WindowConfig())
window.display()
```
**Note**: `WindowConfig()` is an instance of a window configuration file as defined in `visualization/window_config.py`.
An example of default configuration can be seen in `visualization/.msvconfig`. An edited configuration can be passed as 
an argument to the `WindowConfig()` constructor.

### Module Structure
![plot](./musicAI_structure.png)

### Visualization Features
#### Window and Slicing:
- Scrolling
- Resizing
- Score Information
- Structure Slicing
#### Glyph Placement:
- Staff Lines
- Time Signature
- Clef
- Notes
- Beamed Notes
- Ledger Lines
- Accidentals
- Bar Lines
- Dotted Notes
- Rests
#### In Progress / Next Steps:
- Zooming
- Note Satellites
- Lyrics
- Percussion
- Rest (cont.)
- Dynamic Marks
- Ties / Slurs
- Chords
- Keyboard Parts
- Tuplets
- etc.

## Useful Links
- [Bravura Docs](https://w3c.github.io/smufl/latest/index.html)
- [MusicXML Docs](https://www.w3.org/2021/06/musicxml40/)

## Credits
All credits for this module go to the `Soundbendor Lab` at Oregon State University run by Dr. Patrick Donnelly.
### Contributors
- `Kobe Chenea`
- `Paul Koos`
- `Victor Marquez`
- `Alexander Prestwich`
