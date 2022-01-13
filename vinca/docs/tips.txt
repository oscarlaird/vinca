                                    ┌────────┐
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┥  TIPS  ┝━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                   └────────┘                              ┃
┃  Vinca can support Images!                                                ┃
┃  - Create a normal card with `vinca 2`                                    ┃
┃  - `vinca lc add-file /path/to/image.png --new-name front.png             ┃
┃  - This image will now appear on the front side of the card.              ┃
┃  - If you name the image back.png instead it will appear on the back.     ┃
┃  - Only 1 image can be shown at a time; only PNGs are supported.          ┃
┃  - Advanced:                                                              ┃
┃      - If the png has transparent background it can match your terminal   ┃
┃      - Edit the TERMINAL_BACKGROUND variable in the source                ┃
┃      - You will find it in _lib/video.py                                  ┃
┃                                                                           ┃
┃  ζ(-2) = ∑ n⁻² = π²                                                       ┃
┃                                                                           ┃
┃  Vinca can support typing greek letters and math symbols!                 ┃
┃  - When making a card with `vinca 2` you can use digraphs.                ┃
┃  - All the digraphs from vim are available in vinca.                      ┃
┃  - Go to vim and read `:help digraphs` if you are unfamiliar.             ┃
┃  - Just like vim you use Ctrl-K to insert digraphs.                       ┃
┃  - Examples:                                                              ┃
┃      - a* is α (use asterisk to convert any latin letter to greek)        ┃
┃      - 2S is ² (Use S for superscript numbers)                            ┃
┃      - 0s is ₀ (Use s for subscript numbers)                              ┃
┃      - dP => h* 00 FA TE RT DG a' o:                                      ┃
┃      -  ∂  ⇒  θ  ∞  ∀  ∃  √  ° á  ö                                       ┃
┃      - There are many more!                                               ┃
┃                                                                           ┃
┃  Backing up a collection of cards is easy!                                ┃
┃  Method 1:                                                                ┃
┃  - Create an empty backup directory to store your cards                   ┃
┃  - `vinca collection save /path/to/backup/directory`                      ┃
┃  Method 2:                                                                ┃
┃  - Use git. (This is my preferred method.)                                ┃
┃  - Make your cards folder a git repository.                               ┃
┃  - Setup with github, bitbucket, &c.                                      ┃
┃  - Navigate to your folder.                                               ┃
┃  - `git push origin`                                                      ┃
┃                                                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
